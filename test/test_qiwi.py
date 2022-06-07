import pytest

from pypayment import QiwiPayment, Payment, PaymentStatus, AuthorizationError
from test import qiwi_secret_key


def test_authorization():
    QiwiPayment.authorize(secret_key=qiwi_secret_key)
    assert QiwiPayment.authorized


def test_authorization_with_invalid_key():
    with pytest.raises(AuthorizationError):
        QiwiPayment.authorize(secret_key="invalid key")


def test_payment_creation():
    QiwiPayment.authorize(secret_key=qiwi_secret_key)
    payment: Payment = QiwiPayment(1)
    assert payment is not None


def test_payment_creation_with_float():
    QiwiPayment.authorize(secret_key=qiwi_secret_key)
    payment: Payment = QiwiPayment(1.23)
    assert payment is not None


def test_payment_creation_with_long_float():
    QiwiPayment.authorize(secret_key=qiwi_secret_key)
    payment: Payment = QiwiPayment(1.23456789)
    assert payment is not None
