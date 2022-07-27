import pytest

from pypayment import LavaPayment, Payment, PaymentStatus, AuthorizationError, NotAuthorized
from test import lava_token, lava_wallet


def test_payment_creation_without_authorization():
    with pytest.raises(NotAuthorized):
        LavaPayment(1)


def test_authorization_with_invalid_key():
    with pytest.raises(AuthorizationError):
        LavaPayment.authorize("invalid token", lava_wallet)


def test_authorization():
    LavaPayment.authorize(lava_token, lava_wallet)
    assert LavaPayment.authorized


def test_payment_creation():
    payment: Payment = LavaPayment(1)
    assert payment is not None


def test_payment_creation_with_float():
    payment: Payment = LavaPayment(1.23)
    assert payment is not None


def test_url_getting():
    payment: Payment = LavaPayment(1)
    assert "https://acquiring.lava.kz/invoice/" in payment.url


def test_status_getting():
    payment: Payment = LavaPayment(1.23)
    assert payment.status == PaymentStatus.WAITING
