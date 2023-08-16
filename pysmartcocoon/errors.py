"""Define package errors."""


class SmartCocoonError(Exception):
    """Define a base error."""


class UnauthorizedError(SmartCocoonError):
    """Define an error related to invalid requests."""


class RequestError(SmartCocoonError):
    """Define an error related to invalid requests."""


class TokenExpiredError(SmartCocoonError):
    """Define an error for expired access tokens that can't be refreshed."""


ERROR_CODES = {1: "The email has not been validated"}
