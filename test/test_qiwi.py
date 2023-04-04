import pytest

from pypayment import QiwiPayment, Payment, AuthorizationError, NotAuthorized, PaymentStatus
from test import qiwi_secret_key


def test_payment_creation_without_authorization():
    with pytest.raises(NotAuthorized):
        QiwiPayment(1)


def test_authorization_with_invalid_key():
    with pytest.raises(AuthorizationError):
        QiwiPayment.authorize(secret_key="invalid key")


def test_authorization():
    QiwiPayment.authorize(secret_key=qiwi_secret_key)
    assert QiwiPayment.authorized


def test_payment_creation():
    payment: Payment = QiwiPayment(1)
    assert payment is not None


def test_url_getting():
    payment: Payment = QiwiPayment(1)
    assert "https://oplata.qiwi.com/form/?invoice_uid=" in payment.url


def test_status_getting():
    payment: Payment = QiwiPayment(1)
    payment.update()
    assert payment.status == PaymentStatus.WAITING


def test_income_getting():
    payment: Payment = QiwiPayment(1)
    payment.update()
    assert payment.income == 1
