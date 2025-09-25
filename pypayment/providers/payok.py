from __future__ import annotations

import hashlib
import urllib.parse
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Mapping

import requests
from requests import RequestException

from pypayment import AuthorizationError, Payment, PaymentGettingError, PaymentNotFound, PaymentStatus


class PayOkPaymentType(Enum):
    """PayOk payment type enum."""

    CARD = "cd"
    """Payment with bank card."""
    SBP = "sbp"
    """Payment with SBP."""
    QIWI = "qw"
    """Payment with QIWI."""
    YOOMONEY = "ym"
    """Payment with YooMoney."""
    WEBMONEY = "wm"
    """Payment with WebMoney."""
    PAYEER = "pr"
    """Payment with Payeer."""
    PERFECT_MONEY = "pm"
    """Payment with Perfect Money."""
    ADVCASH = "ad"
    """Payment with Advcash."""
    BEELINE = "bl"
    """Payment with Beeline."""
    MEGAFON = "mg"
    """Payment with Megafon."""
    TELE2 = "tl"
    """Payment with Tele2."""
    MTS = "mt"
    """Payment with MTS."""
    QIWI_MOBILE = "qm"
    """Payment with QIWI Mobile."""
    BITCOIN = "bt"
    """Payment with Bitcoin."""
    LITECOIN = "lt"
    """Payment with Litecoin."""
    DOGECOIN = "dg"
    """Payment with Dogecoin."""
    DASH = "ds"
    """Payment with Dash."""
    ZCASH = "zc"
    """Payment with ZCash."""


class PayOkCurrency(Enum):
    """PayOk payment currency enum."""

    RUB = "RUB"
    """Russian ruble."""
    UAH = "UAH"
    """Ukrainian hryvnia."""
    USD = "USD"
    """United States dollar."""
    EUR = "EUR"
    """Euro."""
    RUB2 = "RUB2"
    """Russian ruble. (Alternative Gateway)"""


class PayOkPayment(Payment):
    """PayOk payment class."""

    _api_key: str
    _api_id: int
    _shop_id: int
    _shop_secret_key: str
    _payment_type: PayOkPaymentType | None = None
    _currency: PayOkCurrency | None = None
    _success_url: str | None = None
    _BASE_URL = "https://payok.io"
    _PAY_URL = _BASE_URL + "/pay"
    _API_URL = _BASE_URL + "/api"
    _TRANSACTION_URL = _API_URL + "/transaction"
    _BALANCE_URL = _API_URL + "/balance"
    _STATUS_MAP = {
        "0": PaymentStatus.WAITING,
        "1": PaymentStatus.PAID,
    }

    def __init__(
        self,
        amount: float,
        description: str = "",
        id: str | None = None,
        payment_type: PayOkPaymentType | None = None,
        currency: PayOkCurrency | None = None,
        success_url: str | None = None,
    ) -> None:
        """Authorize PayOkPayment class.

        You need to PayOkPayment.authorize() first!

        Instantiation generates new PayOk invoice instance right away.

        Passed parameters will be applied to instance, but won't override default ones.

        :param amount: The amount to be invoiced.
        :param description: Payment comment.
        :param id: Unique Payment ID (default: generated with uuid4).
        :param payment_type: PayOkPaymentType enum.
        :param currency: PayOkCurrency enum.
        :param success_url: User will be redirected to this url after paying.

        :raise NotAuthorized: When class was not authorized with PayOkPayment.authorize()
        :raise PaymentCreationError: When payment creation failed.
        """
        self._payment_type = payment_type or self._payment_type
        self._currency = currency or self._currency
        self._success_url = success_url or self._success_url

        super().__init__(amount, description, id)

    @classmethod
    def authorize(
        cls,
        api_key: str,
        api_id: int,
        shop_id: int,
        shop_secret_key: str,
        payment_type: PayOkPaymentType = PayOkPaymentType.CARD,
        currency: PayOkCurrency = PayOkCurrency.RUB,
        success_url: str | None = None,
    ) -> None:
        """Authorize PayOkPayment class.

        Must be called before the first use of the class!

        Tries to authorize to PayOk API.
        Saves passed parameters as default.

        :param api_key: API key from https://payok.io/cabinet/api.php (`Balance` and `Transactions` permission required)
        :param api_id: ID of API key from https://payok.io/cabinet/api.php
        :param shop_id: ID of shop from https://payok.io/cabinet/main.php
        :param shop_secret_key: Secret key of shop from https://payok.io/cabinet/main.php
        :param payment_type: PayOkPaymentType enum.
        :param currency: PayOkCurrency enum.
        :param success_url: User will be redirected to this url after paying.

        :raise AuthorizationError: When authorization fails.
        """
        cls._api_key = api_key
        cls._api_id = api_id
        cls._shop_id = shop_id
        cls._shop_secret_key = shop_secret_key
        cls._payment_type = payment_type
        cls._currency = currency
        cls._success_url = success_url

        cls._try_authorize()

    def _create_url(self) -> str:
        data = {
            "amount": self.amount,
            "payment": self.id,
            "shop": self._shop_id,
            "desc": self.description,
            "currency": self._currency.value if self._currency else None,
            "success_url": self._success_url,
            "method": self._payment_type.value if self._payment_type else None,
        }

        sign_str = "|".join(map(str, (
            data["amount"], data["payment"], data["shop"], data["currency"], data["desc"],
            self._shop_secret_key)))
        data["sign"] = hashlib.md5(sign_str.encode()).hexdigest()  # noqa

        return self._PAY_URL + "?" + urllib.parse.urlencode(data)

    @classmethod
    def get_status_and_income(cls, payment_id: str) -> tuple[PaymentStatus | None, float]:
        data = {
            "API_ID": cls._api_id,
            "API_KEY": cls._api_key,
            "shop": cls._shop_id,
            "payment": payment_id,
        }

        try:
            response = requests.post(
                cls._TRANSACTION_URL,
                data=data,
                timeout=10,
            ).json()
        except RequestException as e:
            raise PaymentGettingError() from e

        if response.get("status") != "success":
            raise PaymentNotFound(f"Payment with id {payment_id} not found")

        payment: Mapping[str, Any] = response.get("1")

        transaction_status = payment.get("transaction_status")
        status = None
        if transaction_status:
            status = cls._STATUS_MAP.get(transaction_status)
        income = float(str(payment.get("amount_profit")))
        return status, income

    @classmethod
    def _try_authorize(cls) -> None:
        data = {
            "API_ID": cls._api_id,
            "API_KEY": cls._api_key,
        }
        try:
            response = requests.post(
                cls._BALANCE_URL,
                data=data,
                timeout=10,
            )
        except RequestException as e:
            raise AuthorizationError() from e

        if response.status_code != requests.codes.ok:
            raise AuthorizationError(response.text)
        if response.json().get("status") == "error":
            raise AuthorizationError(response.json())

        data = {
            "amount": 1,
            "payment": "test",
            "shop": cls._shop_id,
            "desc": "test",
            "currency": "RUB",
        }
        sign_str = "|".join(map(str, (
            data["amount"], data["payment"], data["shop"], data["currency"], data["desc"],
            cls._shop_secret_key)))
        data["sign"] = hashlib.md5(sign_str.encode()).hexdigest()  # noqa
        try:
            response = requests.post(
                cls._PAY_URL,
                data=data,
                timeout=10,
            )
        except RequestException as e:
            raise AuthorizationError() from e

        if response.status_code != requests.codes.ok:
            raise AuthorizationError(response.text)
        if "Такой магазин не зарегистрирован." in response.text:
            raise AuthorizationError("Invalid shop ID")
        if "Неверная подпись." in response.text:
            raise AuthorizationError("Invalid shop secret key")

        cls.authorized = True
