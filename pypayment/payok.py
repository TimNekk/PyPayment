import hashlib
import urllib.parse
from enum import Enum
from typing import Optional, Any, Mapping

import requests

from pypayment import Payment, PaymentStatus, NotAuthorized, PaymentGettingError, AuthorizationError


class PayOkPaymentType(Enum):
    CARD = "cd"
    """Payment with bank card."""
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
    """Payment with ZСash."""


class PayOkCurrency(Enum):
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
    authorized = False
    _api_key: str
    _api_id: int
    _shop_id: int
    _shop_secret_key: str
    _payment_type: PayOkPaymentType
    _currency: PayOkCurrency
    _success_url: Optional[str] = None
    _BASE_URL = "https://payok.io"
    _PAY_URL = _BASE_URL + "/pay"
    _API_URL = _BASE_URL + "/api"
    _TRANSACTION_URL = _API_URL + "/transaction"
    _STATUS_MAP = {
        "0": PaymentStatus.WAITING,
        "1": PaymentStatus.PAID
    }

    def __init__(self,
                 amount: float,
                 description: str = "",
                 payment_type: Optional[PayOkPaymentType] = None,
                 currency: Optional[PayOkCurrency] = None,
                 success_url: Optional[str] = None):
        """
        You need to PayOkPayment.authorize() first!

        Instantiation generates new PayOk invoice instance right away.

        Passed parameters will be applied to instance, but won't override default ones.

        :param amount: The amount to be invoiced.
        :param payment_type: PayOkPaymentType enum.
        :param currency: PayOkCurrency enum.
        :param success_url: User will be redirected to this url after paying.

        :raise NotAuthorized: When class was not authorized with PayOkPayment.authorize()
        :raise PaymentCreationError: When payment creation failed.
        """
        if not PayOkPayment.authorized:
            raise NotAuthorized("You need to authorize first: PayOkPayment.authorize()")

        self._payment_type = PayOkPayment._payment_type if payment_type is None else payment_type
        self._currency = PayOkPayment._currency if currency is None else currency
        self._success_url = PayOkPayment._success_url if success_url is None else success_url

        super().__init__(amount, description)
        self.id: str = str(self.id[:16])
        if not description:
            self.description = self.id

        self._url = self._create()

    @classmethod
    def authorize(cls,
                  api_key: str,
                  api_id: int,
                  shop_id: int,
                  shop_secret_key: str,
                  payment_type: PayOkPaymentType = PayOkPaymentType.CARD,
                  currency: PayOkCurrency = PayOkCurrency.RUB,
                  success_url: Optional[str] = None) -> None:
        """
        Must be called before the first use of the class!

        Tries to authorize to PayOk API.
        Saves passed parameters as default.

        :param api_key: API key from https://payok.io/cabinet/api.php
        :param api_id: ID of API key from https://payok.io/cabinet/api.php
        :param shop_id: ID of shop from https://payok.io/cabinet/main.php
        :param shop_secret_key: Secret key of shop from https://payok.io/cabinet/main.php
        :param payment_type: PayOkPaymentType enum.
        :param currency: PayOkCurrency enum.
        :param success_url: User will be redirected to this url after paying.

        :raise AuthorizationError: When authorization fails.
        """
        PayOkPayment._api_key = api_key
        PayOkPayment._api_id = api_id
        PayOkPayment._shop_id = shop_id
        PayOkPayment._shop_secret_key = shop_secret_key
        PayOkPayment._payment_type = payment_type
        PayOkPayment._currency = currency
        PayOkPayment._success_url = success_url

        cls._try_authorize()

    @classmethod
    def _try_authorize(cls) -> None:
        data = {
            "API_ID": cls._api_id,
            "API_KEY": cls._api_key,
            "shop": cls._shop_id,
        }
        try:
            response = requests.post(cls._TRANSACTION_URL, data=data)
        except Exception as e:
            raise AuthorizationError(e)

        if response.json().get("status") == "error":
            raise AuthorizationError(response.json())

        data = {
            "amount": 1,
            "payment": "test",
            "shop": PayOkPayment._shop_id,
            "desc": "test",
            "currency": "RUB",
        }
        sign_str = "|".join(map(str, (data["amount"], data["payment"], data["shop"], data["currency"], data["desc"], PayOkPayment._shop_secret_key)))
        data["sign"] = hashlib.md5(sign_str.encode()).hexdigest()
        try:
            response = requests.post(PayOkPayment._PAY_URL, data=data)
        except Exception as e:
            raise AuthorizationError(e)

        if "Неверная подпись." in response.text:
            raise AuthorizationError("Invalid shop secret key")

        cls.authorized = True

    def _create(self) -> str:
        data = {
            "amount": self.amount,
            "payment": self.id,
            "shop": PayOkPayment._shop_id,
            "desc": self.description,
            "currency": self._currency.value,
            "success_url": self._success_url,
            "method": self._payment_type.value
        }

        sign_str = "|".join(map(str, (data["amount"], data["payment"], data["shop"], data["currency"], data["desc"], PayOkPayment._shop_secret_key)))
        data["sign"] = hashlib.md5(sign_str.encode()).hexdigest()

        return PayOkPayment._PAY_URL + "?" + urllib.parse.urlencode(data)

    def _get_payment(self) -> Optional[Mapping[str, Any]]:
        data = {
            "API_ID": PayOkPayment._api_id,
            "API_KEY": PayOkPayment._api_key,
            "shop": PayOkPayment._shop_id,
            "payment": self.id
        }
        try:
            response = requests.post(PayOkPayment._TRANSACTION_URL, data=data).json()
            print(response)
        except Exception as e:
            raise PaymentGettingError(e)

        if response.get("status") == "success":
            payment: Mapping[str, Any] = response.get("1")
            return payment

        return None

    @property
    def url(self) -> str:
        return self._url

    @property
    def status(self) -> PaymentStatus:
        payment = self._get_payment()
        status: Optional[PaymentStatus] = None

        if payment:
            transaction_status = payment.get("transaction_status")
            if transaction_status:
                status = PayOkPayment._STATUS_MAP.get(transaction_status)

        return status if status else PaymentStatus.WAITING

    @property
    def income(self) -> Optional[float]:
        payment = self._get_payment()

        if payment:
            return float(str(payment.get("amount_profit")))

        return None
