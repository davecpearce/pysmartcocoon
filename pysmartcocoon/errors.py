"""Define package errors."""


class SmartCocoonError(Exception):
    """Define a base error."""

    pass


class UnauthorizedError(SmartCocoonError):
    """Define an error related to invalid requests."""

    pass


class RequestError(SmartCocoonError):
    """Define an error related to invalid requests."""

    pass


class TokenExpiredError(SmartCocoonError):
    """Define an error for expired access tokens that can't be refreshed."""

    pass


ERROR_CODES = {1: "The email has not been validated"}
