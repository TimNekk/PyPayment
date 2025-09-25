from __future__ import annotations

import hashlib
from dataclasses import dataclass
from enum import Enum
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from collections.abc import Mapping

import requests
from requests import RequestException

from pypayment import (
    AuthorizationError,
    ChargeCommission,
    Payment,
    PaymentCreationError,
    PaymentGettingError,
    PaymentNotFound,
    PaymentStatus,
)


class BetaTransferCurrency(Enum):
    """BetaTransfer payment currency enum."""

    RUB = "RUB"
    """Russian ruble."""
    UAH = "UAH"
    """Ukrainian hryvnia."""
    USD = "USD"
    """United States dollar."""
    KZT = "KZT"
    """Kazakhstani tenge."""
    UZS = "UZS"
    """Uzbekistani so`m."""
    BYN = "BYN"
    """Belarusian ruble."""
    AZN = "AZN"
    """Azerbaijani manat."""
    TJS = "TJS"
    """Tajikistani somoni."""
    KGS = "KGS"
    """Kyrgyzstani som."""


@dataclass
class BetaTransferGateway:
    """BetaTransfer gateway dataclass."""

    name: str
    currency: BetaTransferCurrency
    commission_in_percent: float
    min_amount: float | None
    max_amount: float | None


class BetaTransferPaymentType(Enum):
    """BeteTransfer payment type enum."""

    USDT_TRC20 = BetaTransferGateway(
        name="USDT_TRC20",
        currency=BetaTransferCurrency.USD,
        commission_in_percent=2,
        min_amount=5,
        max_amount=5000,
    )
    """USDT TRC20 payment type."""
    USDT_ERC20 = BetaTransferGateway(
        name="USDT_ERC20",
        currency=BetaTransferCurrency.USD,
        commission_in_percent=2,
        min_amount=30,
        max_amount=5000,
    )
    """USDT ERC20 payment type."""
    ETH = BetaTransferGateway(
        name="ETH",
        currency=BetaTransferCurrency.USD,
        commission_in_percent=0,
        min_amount=22,
        max_amount=5000,
    )
    """Etherium payment type."""
    BTC = BetaTransferGateway(
        name="BTC",
        currency=BetaTransferCurrency.USD,
        commission_in_percent=0,
        min_amount=20,
        max_amount=500,
    )
    """Bitcoin payment type."""
    CRYPTO = BetaTransferGateway(
        name="CRYPTO",
        currency=BetaTransferCurrency.USD,
        commission_in_percent=2,
        min_amount=5,
        max_amount=5000,
    )
    """Crypto payment type."""
    KZT_CARD_USD = BetaTransferGateway(
        name="P2R_KZT",
        currency=BetaTransferCurrency.USD,
        commission_in_percent=12,
        min_amount=12,
        max_amount=1000,
    )
    """P2R KZT payment type."""
    KZT_CARD = BetaTransferGateway(
        name="P2R_KZT",
        currency=BetaTransferCurrency.KZT,
        commission_in_percent=12,
        min_amount=None,
        max_amount=None,
    )
    """P2R KZT payment type."""
    UZS_CARD = BetaTransferGateway(
        name="Card6",
        currency=BetaTransferCurrency.UZS,
        commission_in_percent=12,
        min_amount=100000,
        max_amount=None,
    )
    """UZS payment type."""
    RUB_P2R = BetaTransferGateway(
        name="P2R",
        currency=BetaTransferCurrency.RUB,
        commission_in_percent=9.5,
        min_amount=1500,
        max_amount=50000,
    )
    """RUB P2R payment type."""
    RUB_SBP = BetaTransferGateway(
        name="Card4",
        currency=BetaTransferCurrency.RUB,
        commission_in_percent=9,
        min_amount=500,
        max_amount=10000,
    )
    """Qiwi Card payment type."""
    RUB_CARD = BetaTransferGateway(
        name="Card",
        currency=BetaTransferCurrency.RUB,
        commission_in_percent=12,
        min_amount=100,
        max_amount=75000,
    )
    """SBP payment type."""
    YOOMONEY = BetaTransferGateway(
        name="YooMoney",
        currency=BetaTransferCurrency.RUB,
        commission_in_percent=14,
        min_amount=1000,
        max_amount=50000,
    )
    """YooMoney payment type."""
    SBER_PAY = BetaTransferGateway(
        name="Card5",
        currency=BetaTransferCurrency.RUB,
        commission_in_percent=10,
        min_amount=500,
        max_amount=100000,
    )
    """Sber Pay payment type."""
    RUB_IBAN = BetaTransferGateway(
        name="Card9",
        currency=BetaTransferCurrency.RUB,
        commission_in_percent=9,
        min_amount=300,
        max_amount=100000,
    )
    """RUB IBAN payment type."""
    UAH_CARD = BetaTransferGateway(
        name="Card1",
        currency=BetaTransferCurrency.UAH,
        commission_in_percent=9.5,
        min_amount=350,
        max_amount=10000,
    )
    """UAH card payment type."""
    BYN_CARD = BetaTransferGateway(
        name="Card2",
        currency=BetaTransferCurrency.BYN,
        commission_in_percent=12,
        min_amount=30,
        max_amount=10000,
    )
    """BYN card payment type."""
    BYN_CARD2 = BetaTransferGateway(
        name="Card3",
        currency=BetaTransferCurrency.BYN,
        commission_in_percent=12,
        min_amount=30,
        max_amount=5000,
    )
    """BYN card payment type."""
    AZN_CARD = BetaTransferGateway(
        name="P2R_AZN",
        currency=BetaTransferCurrency.AZN,
        commission_in_percent=9,
        min_amount=10,
        max_amount=5000,
    )
    """AZN card payment type."""
    TJS_CARD = BetaTransferGateway(
        name="P2R_TJS",
        currency=BetaTransferCurrency.TJS,
        commission_in_percent=9,
        min_amount=100,
        max_amount=10000,
    )
    """TJS card payment type."""
    KGS_CARD = BetaTransferGateway(
        name="P2R_KGS",
        currency=BetaTransferCurrency.KGS,
        commission_in_percent=9,
        min_amount=500,
        max_amount=150000,
    )
    """KGS card payment type."""


class BetaTransferLocale(Enum):
    """BeteTransfer payment form language enum."""

    RUSSIAN = "ru"
    """Russian language."""
    ENGLISH = "en"
    """English language."""
    UKRAINIAN = "uk"
    """Ukrainian language."""


class BetaTransferPayment(Payment):
    """BetaTransfer payment class."""

    _public_key: str | None = None
    _private_key: str | None = None
    _payment_type: BetaTransferPaymentType | None = None
    _url_result: str | None = None
    _url_success: str | None = None
    _url_fail: str | None = None
    _locale: BetaTransferLocale | None = None
    _charge_commission: ChargeCommission | None = None
    _do_params_validation: bool = True
    _BASE_URL = "https://merchant.betatransfer.io/api"
    _PAYMENT_URL = _BASE_URL + "/payment"
    _INFO_URL = _BASE_URL + "/info"
    _ACCOUNT_INFO_URL = _BASE_URL + "/account-info"
    _STATUS_MAP = {
        "success": PaymentStatus.PAID,
        "cancel": PaymentStatus.REJECTED,
        "processing": PaymentStatus.WAITING,
        "error": PaymentStatus.REJECTED,
        "pending": PaymentStatus.WAITING,
        "checkPayment": PaymentStatus.WAITING,
        "not_paid": PaymentStatus.WAITING,
        "not_paid_timeout": PaymentStatus.EXPIRED,
        "not_paid_unavailable_country": PaymentStatus.REJECTED,
        "hold_payment": PaymentStatus.WAITING,
        "new": PaymentStatus.WAITING,
        "entered_card_data": PaymentStatus.WAITING,
        "partial_payment": PaymentStatus.WAITING,
        "awaiting_confirmation": PaymentStatus.WAITING,
    }

    def __init__(
        self,
        amount: float,
        description: str = "",
        id: str | None = None,
        payment_type: BetaTransferPaymentType | None = None,
        url_result: str | None = None,
        url_success: str | None = None,
        url_fail: str | None = None,
        locale: BetaTransferLocale | None = None,
        charge_commission: ChargeCommission | None = None,
        validate_params: bool = True,
        payer_id: str | None = None,
    ) -> None:
        """Instantiate BetaTransferPayment class.

        You need to BetaTransferPayment.authorize() first!

        Instantiation generates new BetaTransfer invoice instance right away.

        Passed parameters will be applied to instance, but won't override default ones.

        :param amount: The amount to be invoiced.
        :param description: Payment comment.
        :param id: (default: generated with uuid4).
        :param payment_type: BetaTransferPaymentType enum.
        :param url_result: Callback URL.
        :param url_success: User will be redirected to this url after paying successfully.
        :param url_fail: User will be redirected to this url after paying unsuccessfully.
        :param locale: BetaTransferLocale enum.
        :param charge_commission: ChargeCommission enum.
        :param validate_params: Validate passed parameters.
        :param payer_id: Payer ID.

        :raises NotAuthorizedError: When class was not authorized with BetaTransferPayment.authorize()
        :raises PaymentCreationError: When payment creation failed.
        """
        self._payment_type = payment_type or self._payment_type
        self._url_result = url_result or self._url_result
        self._url_success = url_success or self._url_success
        self._url_fail = url_fail or self._url_fail
        self._locale = locale or self._locale
        self._charge_commission = charge_commission or self._charge_commission
        self._do_params_validation = validate_params or self._do_params_validation
        self.payer_id = payer_id

        super().__init__(amount, description, id)

    def _validate_params(self) -> None:
        if not self._do_params_validation:
            return

        if not self._url_success or not self._url_fail:
            raise PaymentCreationError("You must specify url_success and url_fail!")

        if not self._payment_type:
            raise PaymentCreationError("You must specify payment_type!")

        min_amount = self._payment_type.value.min_amount
        max_amount = self._payment_type.value.max_amount

        invalid_min_amount = min_amount and self._amount_with_commission < min_amount
        invalid_max_amount = max_amount and self._amount_with_commission > max_amount

        if invalid_min_amount or invalid_max_amount:
            payment_type_name = f"{self._payment_type.name} ({self._payment_type.value.name})"
            currency_name = self._payment_type.value.currency.value
            raise PaymentCreationError(
                f"Amount for {payment_type_name} must be between {min_amount} and {max_amount} {currency_name}!"
            )

    @classmethod
    def authorize(
        cls,
        public_key: str,
        private_key: str,
        payment_type: BetaTransferPaymentType = BetaTransferPaymentType.RUB_P2R,
        url_result: str | None = None,
        url_success: str | None = None,
        url_fail: str | None = None,
        locale: BetaTransferLocale = BetaTransferLocale.RUSSIAN,
        charge_commission: ChargeCommission = ChargeCommission.FROM_SELLER,
        do_params_validation: bool = True,
    ) -> None:
        """Authorize BetaTransferPayment class.

        Must be called before the first use of the class!

        Tries to authorize to BetaTransfer API.
        Saves passed parameters as default.

        :param public_key: Public API key.
        :param private_key: Private (secret) API key.
        :param payment_type: BetaTransferPaymentType enum.
        :param url_result: Callback URL.
        :param url_success: User will be redirected to this url after paying successfully.
        :param url_fail: User will be redirected to this url after paying unsuccessfully.
        :param locale: BetaTransferLocale enum.
        :param charge_commission: ChargeCommission enum.
        :param do_params_validation: Validate passed parameters.

        :raises AuthorizationError: When authorization fails.
        """
        cls._public_key = public_key
        cls._private_key = private_key
        cls._payment_type = payment_type
        cls._url_result = url_result
        cls._url_success = url_success
        cls._url_fail = url_fail
        cls._locale = locale
        cls._charge_commission = charge_commission
        cls._do_params_validation = do_params_validation

        cls._try_authorize()

    def _create_url(self) -> str:
        if not self._payment_type or not self._locale:
            raise PaymentCreationError("You must specify payment_type and locale!")

        params = {
            "token": self._public_key,
        }

        data = {
            "amount": self._amount_with_commission,
            "currency": self._payment_type.value.currency.value,
            "orderId": self.id,
            "paymentSystem": self._payment_type.value.name,
            "urlResult": self._url_result,
            "urlSuccess": self._url_success,
            "urlFail": self._url_fail,
            "locale": self._locale.value,
            "fullCallback": 1,
            "payerId": self.payer_id,
        }

        try:
            response = requests.post(
                self._PAYMENT_URL,
                headers=self._get_headers(),
                params=params,
                data=data,
                timeout=10,
            )
        except RequestException as e:
            raise PaymentCreationError() from e

        if response.status_code != requests.codes.ok:
            raise PaymentCreationError(response.text)

        return str(response.json().get("url"))

    @classmethod
    def get_status_and_income(cls, payment_id: str) -> tuple[PaymentStatus | None, float]:
        params = {
            "token": cls._public_key,
        }

        data = {
            "orderId": payment_id,
        }
        data["sign"] = cls._get_sign(data)

        try:
            response = requests.get(
                cls._INFO_URL,
                headers=cls._get_headers(),
                data=data,
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
        income = float(str(payment.get("balanceAmount")))
        return status, income

    @classmethod
    def _get_headers(cls) -> Mapping[str, str]:
        return {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        }

    @classmethod
    def _try_authorize(cls) -> None:
        params = {
            "token": str(cls._public_key),
        }
        params["sign"] = cls._get_sign(params)

        try:
            response = requests.get(
                cls._ACCOUNT_INFO_URL,
                headers=cls._get_headers(),
                params=params,
                timeout=10,
            )
        except RequestException as e:
            raise AuthorizationError() from e

        if response.status_code != requests.codes.ok:
            raise AuthorizationError(response.text)

        cls.authorized = True

    @classmethod
    def _get_sign(cls, data: Mapping[str, str]) -> str:
        sign = "".join(str(value) for value in data.values()) + str(cls._private_key)
        return hashlib.md5(sign.encode()).hexdigest()  # noqa

    @property
    def _amount_with_commission(self) -> float:
        if self._charge_commission == ChargeCommission.FROM_CUSTOMER and self._payment_type:
            return round(self.amount + self.amount * self._payment_type.value.commission_in_percent / 100, 2)

        return self.amount
