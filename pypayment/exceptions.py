class NotAuthorized(Exception):
    """Raised when payment provider class has not been authorized."""


class AuthorizationError(Exception):
    """Raised when authorization failed."""


class PaymentCreationError(Exception):
    """Raised when payment creation failed."""


class PaymentGettingError(Exception):
    """Raised when payment getting failed."""
