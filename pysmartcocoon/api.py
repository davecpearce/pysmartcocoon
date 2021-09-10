"""Define a manager to interact with SmartCocoon"""
import asyncio
import paho.mqtt.client as mqtt
import uuid
import traceback

from aiohttp import ClientSession, ClientTimeout
from aiohttp.client_exceptions import ClientError
import async_timeout

from datetime import datetime, timedelta
import logging

from typing import (
    Any,
    Callable,
    cast,
    Dict,
    Optional,
)

from pysmartcocoon.const import (
    API_HEADERS,
    API_URL,
    API_AUTH_URL,
    API_FANS_URL,
    DEFAULT_TIMEOUT,
    FanMode,
    EntityType,
    MQTT_BROKER,
    MQTT_KEEPALIVE,
    MQTT_PORT,
)

from pysmartcocoon.errors import RequestError, SmartCocoonError
from pysmartcocoon.errors import UnauthorizedError
from pysmartcocoon.errors import TokenExpiredError

_LOGGER: logging.Logger = logging.getLogger(__name__)


class SmartCocoonAPI:
    """This class will communicate with the SmartCocoon cloud API"""

    def __init__(
        self,
        session: Optional[ClientSession] = None,
        request_timeout: int = DEFAULT_TIMEOUT,
    ) -> None:

        self._session = session
        self._request_timeout = request_timeout

        self._headersAuth = API_HEADERS
        self._authenticated = False

    async def async_authenticate(
        self,
        username: str,
        password: str
    ) -> bool:

        self._authenticated = False

        # Authenticate with user and pass
        request_body = {}
        request_body.setdefault("json", {})
        request_body["json"]["email"] = username
        request_body["json"]["password"] = password

        response = await self.async_request("POST", API_AUTH_URL, **request_body)

        return self._authenticated
        

    async def async_request(self, method: str, url: str, **kwargs) -> dict:
        """Make a request using token authentication.
        Args:
            method: Method for the HTTP request (example "GET" or "POST").
            path: path of the REST API endpoint.
        Returns:
            the Response object corresponding to the result of the API request.
        """

        use_running_session = self._session and not self._session.closed

        if use_running_session:
            session = self._session
        else:
            session = ClientSession(timeout=ClientTimeout(total=DEFAULT_TIMEOUT))

        assert session

        data = None

        _LOGGER.debug("Calling SmartCocoon API - method: %s, url: %s", method, url)

        try:
            async with async_timeout.timeout(self._request_timeout) as cm:
                response = await session.request(method, url, ssl=False, headers=self._headersAuth, **kwargs)
                _LOGGER.debug("SmartCocoon API response status: %s", response.status)
                response.raise_for_status()
                data = await response.json(content_type=None)
            _LOGGER.debug("cm.expired = %s", cm.expired)
        except ClientError as err:
            if "401" in str(err):
                # Authentication failed
                return None        
            elif "403" in str(err):
                # Forbidden error - likely needs to re-authenticate
                return None        
        except asyncio.TimeoutError as err:
            _LOGGER.error("API call to SmartCocoon timed out")
            return None
        except Exception as err:
            _LOGGER.error("API call to SmartCocoon failed with expected error")
            _LOGGER.error(traceback.format_exc())
            return None
        finally:
            if not use_running_session:
                await session.close()

        # If this request is for authorization, save auth data
        if url == API_AUTH_URL:
            self._bearerToken: str = response.headers["access-token"]
            self._bearerTokenExpiration: datetime = datetime.now() + timedelta(
                seconds=int(response.headers["expiry"]) - 10
                )
            self._apiClient: str = response.headers["client"]

            self._headersAuth["access-token"] = self._bearerToken
            self._headersAuth["client"] = self._apiClient
            self._headersAuth["uid"] = data["data"]["email"]

            self._user_id: str = data["data"]["id"]
            self._authenticated = True

        if data is not None:
            return cast(Dict[str, Any], data)
        else:
            _LOGGER.error("Response data is None")
            return
