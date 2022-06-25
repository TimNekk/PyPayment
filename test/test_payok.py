import pytest

from pypayment import PayOkPayment, Payment, PaymentStatus, AuthorizationError, NotAuthorized
from test import payok_api_key, payok_api_id, payok_shop_id, payok_shop_secret_key


def test_payment_creation_without_authorization():
    with pytest.raises(NotAuthorized):
        PayOkPayment(1)


def test_authorization_with_invalid_api_key():
    with pytest.raises(AuthorizationError):
        PayOkPayment.authorize("invalid data", payok_api_id, payok_shop_id, payok_shop_secret_key)


def test_authorization_with_invalid_api_id():
    with pytest.raises(AuthorizationError):
        PayOkPayment.authorize(payok_api_key, 0, payok_shop_id, payok_shop_secret_key)


def test_authorization_with_invalid_shop_id():
    with pytest.raises(AuthorizationError):
        PayOkPayment.authorize(payok_api_key, payok_api_id, 0, payok_shop_secret_key)


def test_authorization_with_invalid_shop_secret_key():
    with pytest.raises(AuthorizationError):
        PayOkPayment.authorize(payok_api_key, payok_api_id, payok_shop_id, "invalid data")


def test_authorization():
    PayOkPayment.authorize(payok_api_key, payok_api_id, payok_shop_id, payok_shop_secret_key)
    assert PayOkPayment.authorized


def test_payment_creation():
    payment: Payment = PayOkPayment(1)
    assert payment is not None


def test_payment_creation_with_float():
    payment: Payment = PayOkPayment(1.23)
    assert payment is not None


def test_url_getting():
    payment: Payment = PayOkPayment(1)
    assert "https://payok.io/pay?" in payment.url


def test_status_getting():
    payment: Payment = PayOkPayment(1.23)
    assert payment.status == PaymentStatus.WAITING
