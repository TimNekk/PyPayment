import pytest

from pypayment import YooMoneyPayment, Payment, AuthorizationError, NotAuthorized, PaymentStatus
from test import yoomoney_access_token


def test_payment_creation_without_authorization():
    with pytest.raises(NotAuthorized):
        YooMoneyPayment(1)


def test_authorization_with_invalid_key():
    with pytest.raises(AuthorizationError):
        YooMoneyPayment.authorize("invalid token")


def test_authorization():
    YooMoneyPayment.authorize(yoomoney_access_token)
    assert YooMoneyPayment.authorized


def test_payment_creation():
    payment: Payment = YooMoneyPayment(1)
    assert payment is not None


def test_url_getting():
    payment: Payment = YooMoneyPayment(1)
    assert "https://yoomoney.ru/transfer/quickpay?requestId=" in payment.url


def test_status_getting():
    payment: Payment = YooMoneyPayment(1)
    payment.update()
    assert payment.status == PaymentStatus.WAITING


def test_income_getting():
    payment: Payment = YooMoneyPayment(1)
    payment.update()
    assert payment.income is None


def test_get_wrong_access_token(monkeypatch):
    monkeypatch.setattr('builtins.input', lambda _: "some_wrong_token")
    access_token = YooMoneyPayment.get_access_token("wrong", "data", "name1")
    assert not access_token
