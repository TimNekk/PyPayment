import pytest

from pypayment import Payment


def test_default_url():
    with pytest.raises(TypeError):
        payment = Payment(1)
        payment.url


def test_default_status():
    with pytest.raises(TypeError):
        payment = Payment(1)
        payment.status


def test_default_income():
    with pytest.raises(TypeError):
        payment = Payment(1)
        payment.income
