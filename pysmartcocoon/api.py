"""Define a manager to interact with SmartCocoon"""
import asyncio
import logging
import traceback
from datetime import datetime, timedelta
from typing import Any, Optional, cast

import async_timeout
from aiohttp import ClientSession, ClientTimeout
from aiohttp.client_exceptions import ClientError

from pysmartcocoon.const import API_AUTH_URL, API_HEADERS, DEFAULT_TIMEOUT

_LOGGER: logging.Logger = logging.getLogger(__name__)


# pylint: disable=too-many-instance-attributes
class SmartCocoonAPI:
    """This class will communicate with the SmartCocoon cloud API"""

    def __init__(
        self,
        session: Optional[ClientSession] = None,
        request_timeout: int = DEFAULT_TIMEOUT,
    ) -> None:
        self._session = session
        self._request_timeout = request_timeout
        self._authenticated = False
        self._api_client = None
        self._bearer_token = None
        self._bearer_token_expiration = None
        self._headers_auth = API_HEADERS
        self._user_id = None

    async def async_authenticate(self, username: str, password: str) -> bool:
        """Function to authenticate user with API"""
        self._authenticated = False

        # Authenticate with user and pass
        request_body = {}
        request_body.setdefault("json", {})
        request_body["json"]["email"] = username
        request_body["json"]["password"] = password

        await self.async_request("POST", API_AUTH_URL, **request_body)

        return self._authenticated

    async def async_request(self, method: str, url: str, **kwargs) -> dict:
        """Make a request using token authentication.
        Args:
            method: Method for the HTTP request (example "GET" or "POST").
            path: path of the REST API endpoint.
        Returns:
            the Response object corresponding to the result of the API request.
        """
        # pylint: disable=broad-except
        use_running_session = self._session and not self._session.closed

        if use_running_session:
            session = self._session
        else:
            timeout_value = ClientTimeout(total=self._request_timeout)
            session = ClientSession(timeout=timeout_value)

        assert session

        data = None

        _LOGGER.debug(
            "Calling SmartCocoon API - method: %s, url: %s", method, url
        )

        has_error = False
        try:
            async with async_timeout.timeout(self._request_timeout):
                response = await session.request(
                    method,
                    url,
                    ssl=False,
                    headers=self._headers_auth,
                    **kwargs,
                )
                _LOGGER.debug(
                    "SmartCocoon API response status: %s", response.status
                )
                response.raise_for_status()
                data = await response.json(content_type=None)
        except ClientError as err:
            # 401 - Authentication failed
            # 403 - Forbidden error - likely needs to re-authenticate
            error_codes = ["401", "403", "server disconnected"]
            if any(x in str(err) for x in error_codes):
                _LOGGER.error("SmartCocoon API response error: %s", str(err))
                has_error = True
        except asyncio.TimeoutError:
            _LOGGER.error("API call to SmartCocoon timed out")
            has_error = True
        except Exception:
            _LOGGER.error("API call to SmartCocoon failed with expected error")
            _LOGGER.error(traceback.format_exc())
            has_error = True
        finally:
            if not use_running_session:
                await session.close()

        if has_error:
            return None

        # If this request is for authorization, save auth data
        if url == API_AUTH_URL:
            self._bearer_token: str = response.headers["access-token"]
            self._bearer_token_expiration: datetime = (
                datetime.now()
                + timedelta(seconds=int(response.headers["expiry"]) - 10)
            )
            self._api_client: str = response.headers["client"]

            self._headers_auth["access-token"] = self._bearer_token
            self._headers_auth["client"] = self._api_client
            self._headers_auth["uid"] = data["data"]["email"]

            self._user_id: str = data["data"]["id"]
            self._authenticated = True

        if data is not None:
            return cast(dict[str, Any], data)

        _LOGGER.error("Response data is None")
        return
