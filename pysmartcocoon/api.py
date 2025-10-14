"""Define a manager to interact with SmartCocoon"""

import asyncio
import logging
import random
from datetime import datetime, timedelta
from typing import Any, Optional, cast

import async_timeout
from aiohttp import ClientResponseError, ClientSession, ClientTimeout
from aiohttp.client_exceptions import ClientConnectionError

from pysmartcocoon.const import (
    API_AUTH_URL,
    API_FANS_URL,
    API_HEADERS,
    DEFAULT_TIMEOUT,
)
from pysmartcocoon.errors import RequestError, UnauthorizedError

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
        # Make a private copy of default headers to avoid global mutation
        self._headers_auth = API_HEADERS.copy()
        self._user_id = None

    async def __aenter__(self) -> "SmartCocoonAPI":
        return self

    async def __aexit__(self, *_: Any) -> None:
        await self.close()

    async def close(self) -> None:
        """Close internally-owned session if present."""
        if self._session and not self._session.closed:
            await self._session.close()

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

    def _compute_retry_delay(
        self, attempt: int, retry_after: str | None
    ) -> float:
        """Compute delay before retrying, honoring Retry-After when present.

        Uses exponential backoff with jitter when header is absent or invalid.
        """
        if retry_after and retry_after.isdigit():
            return float(int(retry_after))
        base = 2 ** (attempt - 1)
        return base + random.uniform(0, 0.5 * base)

    # pylint: disable=too-many-branches,too-many-statements
    async def async_request(
        self, method: str, url: str, **kwargs
    ) -> dict | None:
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

        # Basic retry loop for transient errors
        max_attempts = 3
        for attempt in range(1, max_attempts + 1):
            try:
                async with async_timeout.timeout(self._request_timeout):
                    response = await session.request(
                        method,
                        url,
                        headers=self._headers_auth,
                        **kwargs,
                    )
                    _LOGGER.debug(
                        "SmartCocoon API response status: %s", response.status
                    )
                    response.raise_for_status()
                    data = await response.json(content_type=None)
                    break
            except ClientResponseError as err:
                if err.status in (401, 403):
                    _LOGGER.debug(
                        "Auth error (%s), re-authenticating", err.status
                    )
                    # Try to re-authenticate once for protected endpoints
                    if url != API_AUTH_URL and self._bearer_token:
                        # Force auth to refresh token with existing uid/client
                        self._authenticated = False
                        # Raise UnauthorizedError so caller can re-authenticate
                        raise UnauthorizedError(str(err)) from err
                    raise UnauthorizedError(str(err)) from err
                if err.status == 429 and attempt < max_attempts:
                    retry_after = (
                        err.headers.get("Retry-After") if err.headers else None
                    )
                    await asyncio.sleep(
                        self._compute_retry_delay(attempt, retry_after)
                    )
                    continue
                if 500 <= err.status < 600 and attempt < max_attempts:
                    await asyncio.sleep(2 ** (attempt - 1))
                    continue
                raise RequestError(str(err)) from err
            except (ClientConnectionError, asyncio.TimeoutError) as err:
                if attempt < max_attempts:
                    await asyncio.sleep(2 ** (attempt - 1))
                    continue
                raise RequestError(str(err)) from err
            except Exception as err:  # pylint: disable=broad-except
                _LOGGER.exception("API call to SmartCocoon failed")
                raise RequestError(str(err)) from err
            finally:
                if not use_running_session:
                    await session.close()

        # If this request is for authorization, save auth data
        if url == API_AUTH_URL:
            self._bearer_token = response.headers["access-token"]
            self._bearer_token_expiration = datetime.now() + timedelta(
                seconds=int(response.headers["expiry"]) - 10
            )
            self._api_client = response.headers["client"]

            self._headers_auth["access-token"] = self._bearer_token
            self._headers_auth["client"] = self._api_client
            self._headers_auth["uid"] = data["data"]["email"]

            self._user_id = data["data"]["id"]
            self._authenticated = True

        if data is not None:
            return cast(dict[str, Any], data)

        _LOGGER.error("Response data is None")
        return None

    async def async_get_fan(self, fan_identifier: int) -> dict | None:
        """Fetch a single fan by internal identifier."""
        return await self.async_request(
            "GET", f"{API_FANS_URL}{fan_identifier}"
        )

    async def async_update_fan(
        self, fan_identifier: int, mode: str, power: int
    ) -> dict | None:
        """Update a fan's mode and power."""
        request_body: dict[str, Any] = {"json": {"mode": mode, "power": power}}
        return await self.async_request(
            "PUT", f"{API_FANS_URL}{fan_identifier}", **request_body
        )
