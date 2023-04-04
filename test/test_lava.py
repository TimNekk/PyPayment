import pytest

from pypayment import LavaPayment, Payment, AuthorizationError, NotAuthorized, PaymentStatus
from test import lava_token, lava_wallet


@pytest.mark.skip(reason="Lava API is not working")
def test_payment_creation_without_authorization():
    with pytest.raises(NotAuthorized):
        LavaPayment(1)


@pytest.mark.skip(reason="Lava API is not working")
def test_authorization_with_invalid_key():
    with pytest.raises(AuthorizationError):
        LavaPayment.authorize("invalid token", lava_wallet)


@pytest.mark.skip(reason="Lava API is not working")
def test_authorization():
    LavaPayment.authorize(lava_token, lava_wallet)
    assert LavaPayment.authorized


@pytest.mark.skip(reason="Lava API is not working")
def test_payment_creation():
    payment: Payment = LavaPayment(1)
    assert payment is not None


@pytest.mark.skip(reason="Lava API is not working")
def test_url_getting():
    payment: Payment = LavaPayment(1)
    assert "https://acquiring.lava.kz/invoice/" in payment.url or \
           "https://acquiring.lava.ru/invoice/" in payment.url


@pytest.mark.skip(reason="Lava API is not working")
def test_status_getting():
    payment: Payment = LavaPayment(1)
    payment.update()
    assert payment.status == PaymentStatus.WAITING


@pytest.mark.skip(reason="Lava API is not working")
def test_income_getting():
    payment: Payment = LavaPayment(1)
    payment.update()
    assert payment.income == 1
