import pytest

from pypayment import PayOkPayment, Payment, AuthorizationError, NotAuthorized, PaymentStatus
from test import payok_api_key, payok_api_id, payok_shop_id, payok_shop_secret_key


def test_payment_creation_without_authorization():
    with pytest.raises(NotAuthorized) as exception:
        PayOkPayment(1)

    assert exception.value.args[0] == "You need to authorize first: PayOkPayment.authorize()"


def test_authorization_with_invalid_api_key():
    with pytest.raises(AuthorizationError) as exception:
        PayOkPayment.authorize("invalid data", payok_api_id, payok_shop_id, payok_shop_secret_key)

    response = dict(exception.value.args[0])
    assert response["error_code"] == "4"


def test_authorization_with_invalid_api_id():
    with pytest.raises(AuthorizationError) as exception:
        PayOkPayment.authorize(payok_api_key, 0, payok_shop_id, payok_shop_secret_key)

    response = dict(exception.value.args[0])
    assert response["error_code"] == "3"


def test_authorization_with_invalid_shop_id():
    with pytest.raises(AuthorizationError) as exception:
        PayOkPayment.authorize(payok_api_key, payok_api_id, 0, payok_shop_secret_key)

    assert exception.value.args[0] == "Invalid shop ID"


def test_authorization_with_invalid_shop_secret_key():
    with pytest.raises(AuthorizationError) as exception:
        PayOkPayment.authorize(payok_api_key, payok_api_id, payok_shop_id, "invalid data")

    assert exception.value.args[0] == "Invalid shop secret key"


def test_authorization():
    PayOkPayment.authorize(payok_api_key, payok_api_id, payok_shop_id, payok_shop_secret_key)
    assert PayOkPayment.authorized


def test_payment_creation():
    payment: Payment = PayOkPayment(1)
    assert payment is not None


def test_url_getting():
    payment: Payment = PayOkPayment(1)
    assert "https://payok.io/pay?" in payment.url


def test_status_getting():
    payment: Payment = PayOkPayment(1)
    payment.update()
    assert payment.status == PaymentStatus.WAITING


def test_income_getting():
    payment: Payment = PayOkPayment(1)
    payment.update()
    assert payment.income is None
