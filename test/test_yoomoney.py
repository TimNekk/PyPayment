import pytest

from pypayment import YooMoneyPayment, Payment, PaymentStatus, AuthorizationError, NotAuthorized
from test import yoomoney_access_token


def test_payment_creation_without_authorization():
    with pytest.raises(NotAuthorized):
        YooMoneyPayment(1)


def test_authorization():
    YooMoneyPayment.authorize(yoomoney_access_token)
    assert YooMoneyPayment.authorized


def test_authorization_with_invalid_key():
    with pytest.raises(AuthorizationError):
        YooMoneyPayment.authorize("invalid token")


def test_payment_creation():
    YooMoneyPayment.authorize(yoomoney_access_token)
    payment: Payment = YooMoneyPayment(1)
    assert payment is not None


def test_payment_creation_with_float():
    YooMoneyPayment.authorize(yoomoney_access_token)
    payment: Payment = YooMoneyPayment(1.23)
    assert payment is not None


def test_url_getting():
    YooMoneyPayment.authorize(yoomoney_access_token)
    payment: Payment = YooMoneyPayment(1)
    assert "https://yoomoney.ru/transfer/quickpay?requestId=" in payment.url


def test_status_getting():
    YooMoneyPayment.authorize(yoomoney_access_token)
    payment: Payment = YooMoneyPayment(1.23)
    assert payment.status == PaymentStatus.WAITING


def test_get_wrong_access_token(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda _: "some_wrong_token")
    access_token = YooMoneyPayment.get_access_token("wrong", "data", "name1")
    assert access_token is None