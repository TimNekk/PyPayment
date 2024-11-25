from __future__ import annotations

import hashlib
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Mapping

import requests
from requests import RequestException

from pypayment import (
    AuthorizationError,
    Payment,
    PaymentCreationError,
    PaymentGettingError,
    PaymentNotFound,
    PaymentStatus,
)


class AaioCurrency(Enum):
    """Aaio payment currency enum."""

    RUB = "RUB"
    """Russian ruble."""
    UAH = "UAH"
    """Ukrainian hryvnia."""
    EUR = "EUR"
    """Euro."""
    USD = "USD"
    """US dollar."""


class AaioPaymentType(Enum):
    """Aaio payment types."""

    CARDS_RU = "cards_ru"
    """Cards RF"""
    CARDS_UA = "cards_ua"
    """Cards Ukraine"""
    CARDS_KZ = "cards_kz"
    """Cards Kazakhstan"""
    SBP = "sbp"
    """SBP (p2p, QR-code - individually)"""
    QIWI = "qiwi"
    """QIWI wallet"""
    PERFECTMONEY = "perfectmoney"
    """Perfect Money"""
    YOOMONEY = "yoomoney"
    """Yoomoney"""
    ADVCASH = "advcash"
    """Advcash"""
    PAYEER = "payeer"
    """Payeer"""
    SKINS = "skins"
    """Payment with skins"""
    BEELINE_RU = "beeline_ru"
    """Beeline RF (phone payment)"""
    TELE2 = "tele2"
    """Tele2 (phone payment)"""
    MEGAFON_RU = "megafon_ru"
    """Megafon RF (phone payment)"""
    MTS_RU = "mts_ru"
    """MTS RF (phone payment)"""
    YOTA = "yota"
    """YOTA (phone payment)"""
    BITCOIN = "bitcoin"
    """Bitcoin"""
    BITCOINCASH = "bitcoincash"
    """Bitcoin Cash"""
    ETHEREUM = "ethereum"
    """Ethereum"""
    TETHER_TRC20 = "tether_trc20"
    """Tether (TRC-20)"""
    TETHER_ERC20 = "tether_erc20"
    """Tether (ERC-20)"""
    TETHER_TON = "tether_ton"
    """Tether (TON)"""
    TETHER_POLYGON = "tether_polygon"
    """Tether (Polygon)"""
    TETHER_BSC = "tether_bsc"
    """Tether (BSC)"""
    USDCOIN_TRC20 = "usdcoin_trc20"
    """USD Coin (TRC-20)"""
    USDCOIN_ERC20 = "usdcoin_erc20"
    """USD Coin (ERC-20)"""
    USDCOIN_BSC = "usdcoin_bsc"
    """USD Coin (BSC)"""
    BNB_BSC = "bnb_bsc"
    """Binance Coin (BSC)"""
    NOTCOIN = "notcoin"
    """Notcoin"""
    TRON = "tron"
    """TRON"""
    LITECOIN = "litecoin"
    """Litecoin"""
    DOGECOIN = "dogecoin"
    """Dogecoin"""
    DAI_ERC20 = "dai_erc20"
    """DAI (ERC-20)"""
    DAI_BSC = "dai_bsc"
    """DAI (BSC)"""
    DASH = "dash"
    """DASH"""
    MONERO = "monero"
    """Monero"""
    COUPON = "coupon"
    """Coupon (Aaio internal system)"""
    BALANCE = "balance"
    """Aaio Balance (Aaio internal system)"""


class AaioPayment(Payment):
    """Aaio payment provider."""

    _api_key: str | None = None
    _secret_1: str | None = None
    _merchant_id: str | None = None
    _payment_type: AaioPaymentType | None
    _currency: AaioCurrency | None
    _BASE_URL = "https://aaio.so"
    _PAYMENT_URL = _BASE_URL + "/merchant/get_pay_url"
    _INFO_URL = _BASE_URL + "/api/info-pay"
    _PAY_METHODS_URL = _BASE_URL + "/api/methods-pay"
    _BALANCE_URL = _BASE_URL + "/api/balance"
    _STATUS_MAP = {
        "success": PaymentStatus.PAID,
        "in_process": PaymentStatus.WAITING,
        "expired": PaymentStatus.EXPIRED,
        "hold": PaymentStatus.WAITING,
    }

    def __init__(
        self,
        amount: float,
        description: str,
        id: str | None = None,
        payment_type: AaioPaymentType | None = None,
        currency: AaioCurrency | None = None,
    ) -> None:
        """Initialize AaioPayment class.

        You need to AaioPayment.authorize() first!

        Instantiation generates new AaioPayment invoice instance right away.

        Passed parameters will be applied to instance, but won't override default ones.

        :param amount: The amount to be invoiced.
        :param description: Payment comment.
        :param id: (default: generated with uuid4).
        :param payment_type: AaioPaymentType enum.
        :param currency: AaioPaymentCurrency enum.
        """
        self._payment_type = payment_type or self._payment_type
        self._currency = currency or self._currency

        super().__init__(amount, description, id)

    @classmethod
    def authorize(
        cls,
        api_key: str,
        secret_1: str,
        merchant_id: str,
        payment_type: AaioPaymentType = AaioPaymentType.CARDS_RU,
        currency: AaioCurrency = AaioCurrency.RUB,
    ) -> None:
        """Authorize AaioPayment class.

        Must be called before the first use of the class!

        Tries to authorize to Aaio API.
        Saves passed parameters as default.

        :param api_key: Aaio API key.
        :param secret_1: Aaio secret 1.
        :param merchant_id: Aaio merchant ID.
        :param payment_type: AaioPaymentType enum.
        :param currency: AaioPaymentCurrency enum.
        """
        cls._api_key = api_key
        cls._secret_1 = secret_1
        cls._merchant_id = merchant_id
        cls._payment_type = payment_type
        cls._currency = currency

        cls._try_authorize()

    def _create_url(self) -> str:
        if not self._merchant_id or not self._currency:
            raise PaymentCreationError("You must specify merchant_id and currency!")

        data = {
            "merchant_id": self._merchant_id,
            "amount": self.amount,
            "order_id": self.id,
            "sign": self._sign,
            "currency": self._currency.value,
            "desc": self.description,
            "method": self._payment_type.value,
        }

        print(data)

        try:
            response = requests.post(
                self._PAYMENT_URL,
                headers=self._get_headers(),
                data=data,
                timeout=10,
            )
        except RequestException as e:
            raise PaymentCreationError() from e

        if response.status_code != requests.codes.ok:
            raise PaymentCreationError(response.text)

        return response.json().get("url")

    @classmethod
    def get_status_and_income(cls, payment_id: str) -> tuple[PaymentStatus | None, float]:
        params = {
            "order_id": payment_id,
            "merchant_id": cls._merchant_id,
        }

        try:
            response = requests.get(
                cls._INFO_URL,
                headers=cls._get_headers(),
                params=params,
                timeout=10,
            )
        except RequestException as e:
            raise PaymentGettingError() from e

        if response.status_code == requests.codes.not_found:
            raise PaymentNotFound(f"Payment with id {payment_id} not found.")

        if response.status_code != requests.codes.ok:
            raise PaymentGettingError(response.text)

        payment: Mapping[str, Any] = response.json()

        status = payment.get("status")
        if status:
            status = cls._STATUS_MAP.get(status)
        income = payment.get("profit")

        return status, income

    @classmethod
    def _get_headers(cls) -> Mapping[str, str]:
        return {
            "Accept": "application/json",
            "Content-Type": "application/x-www-form-urlencoded",
            "X-Api-Key": cls._api_key,
        }

    @classmethod
    def _try_authorize(cls) -> None:
        params = {
            "merchant_id": cls._merchant_id,
        }

        try:
            response = requests.get(
                cls._PAY_METHODS_URL,
                headers=cls._get_headers(),
                params=params,
                timeout=10,
            )
        except RequestException as e:
            raise AuthorizationError() from e

        if response.status_code != requests.codes.ok:
            raise AuthorizationError(response.text)

        cls.authorized = True

    @property
    def _sign(self) -> str:
        return hashlib.sha256(
            ":".join(
                [
                    self._merchant_id,
                    str(self.amount),
                    self._currency.value,
                    self._secret_1,
                    self.id,
                ],
            ).encode("utf-8"),
        ).hexdigest()
