from __future__ import annotations


class PyPaymentException(Exception):
    """Base class for all PyPayment exceptions."""


class NotAuthorized(PyPaymentException):
    """Raised when payment provider class has not been authorized."""


class AuthorizationError(PyPaymentException):
    """Raised when authorization failed."""


class PaymentCreationError(PyPaymentException):
    """Raised when payment creation failed."""


class PaymentGettingError(PyPaymentException):
    """Raised when payment getting failed."""


class PaymentNotFound(PyPaymentException):
    """Raised when payment not found."""
