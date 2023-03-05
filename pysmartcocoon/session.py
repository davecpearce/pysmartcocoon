# -*- coding: utf-8 -*-
"""Session manager for the SmartCocoon REST API in order to maintain authentication token between calls."""
from urllib.parse import quote_plus

from datetime import datetime
from datetime import timedelta

from requests import Response
from requests import Session

from .const import API_HEADERS, API_URL
from .const import API_URL
from .const import API_AUTH_URL

class SmartCocoonClientSession(Session):
    """HTTP session manager for the SmartCocoon api.
    This session object allows to manage the authentication
    in the API using a token.
    """

    def __init__(self, username: str, password: str) -> None:
        """Initialize and authenticate.
        Args:
            username: the SmartCocoon registered app user
            password: the SmartCocoon user's password
        """
        Session.__init__(self)

        # Authenticate with user and pass and store bearer token
        payload_token = {
            "email": username,
            "password": password
        }
        self._headersAuth = API_HEADERS

        response = super().request(
            "POST", API_AUTH_URL, json=payload_token, headers=self._headersAuth
        )
        response.raise_for_status()
        # print(response.text)
        # print(response.request.body)

        json_list = response.json()

        self._bearerToken: str = response.headers["access-token"]
        self._bearerTokenExpiration: datetime = datetime.now() + timedelta(
                seconds=int(response.headers["expiry"]) - 10
            )
        self._apiClient: str = response.headers["client"]

        self._headersAuth["access-token"] = self._bearerToken
        self._headersAuth["client"] = self._apiClient
        self._headersAuth["uid"] = username

        self._user_id: str = json_list["data"]["id"]

        # print("BearerToken of authentication : " + self.bearerToken)

    def rest_request(self, method: str, path: str, **kwargs) -> Response:
        """Make a request using token authentication.
        Args:
            method: Method for the HTTP request (example "GET" or "POST").
            path: path of the REST API endpoint.
        Returns:
            the Response object corresponding to the result of the API request.
        """

        response = super().request(method, f"{API_URL}{path}", headers=self._headersAuth, **kwargs)
        response.raise_for_status()

        return response