import hashlib
from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple, Mapping, Any

import requests

from pypayment import Payment, PaymentStatus, AuthorizationError, PaymentCreationError, PaymentGettingError, \
    PaymentNotFound, ChargeCommission


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
    """Uzbekistani soʻm."""
    BYN = "BYN"
    """Belarusian ruble."""


@dataclass
class BetaTransferGateway:
    name: str
    currency: BetaTransferCurrency
    commission_in_percent: float
    min_amount: Optional[float]
    max_amount: Optional[float]


class BetaTransferPaymentType(Enum):
    """BeteTransfer payment type enum."""

    USDT_TRC20 = BetaTransferGateway(
        name="USDT_TRC20",
        currency=BetaTransferCurrency.USD,
        commission_in_percent=2,
        min_amount=5,
        max_amount=5000
    )
    """USDT TRC20 payment type."""
    USDT_ERC20 = BetaTransferGateway(
        name="USDT_ERC20",
        currency=BetaTransferCurrency.USD,
        commission_in_percent=2,
        min_amount=30,
        max_amount=5000
    )
    """USDT ERC20 payment type."""
    ETH = BetaTransferGateway(
        name="ETH",
        currency=BetaTransferCurrency.USD,
        commission_in_percent=0,
        min_amount=22,
        max_amount=5000
    )
    """Etherium payment type."""
    BTC = BetaTransferGateway(
        name="BTC",
        currency=BetaTransferCurrency.USD,
        commission_in_percent=0,
        min_amount=20,
        max_amount=500
    )
    """Bitcoin payment type."""
    CRYPTO = BetaTransferGateway(
        name="CRYPTO",
        currency=BetaTransferCurrency.USD,
        commission_in_percent=2,
        min_amount=5,
        max_amount=5000
    )
    """Crypto payment type."""
    KZT_CARD_USD = BetaTransferGateway(
        name="P2R_KZT",
        currency=BetaTransferCurrency.USD,
        commission_in_percent=12,
        min_amount=12,
        max_amount=1000
    )
    """P2R KZT payment type."""
    KZT_CARD = BetaTransferGateway(
        name="P2R_KZT",
        currency=BetaTransferCurrency.KZT,
        commission_in_percent=12,
        min_amount=None,
        max_amount=None
    )
    """P2R KZT payment type."""
    UZS_CARD = BetaTransferGateway(
        name="Card6",
        currency=BetaTransferCurrency.UZS,
        commission_in_percent=12,
        min_amount=100000,
        max_amount=None
    )
    """UZS payment type."""
    RUB_P2R = BetaTransferGateway(
        name="P2R",
        currency=BetaTransferCurrency.RUB,
        commission_in_percent=14,
        min_amount=100,
        max_amount=50000
    )
    """RUB P2R payment type."""
    RUB_SBP = BetaTransferGateway(
        name="Card4",
        currency=BetaTransferCurrency.RUB,
        commission_in_percent=13,
        min_amount=100,
        max_amount=10000
    )
    """SBP payment type."""
    YOOMONEY = BetaTransferGateway(
        name="YooMoney",
        currency=BetaTransferCurrency.RUB,
        commission_in_percent=14,
        min_amount=100,
        max_amount=50000
    )
    """YooMoney payment type."""
    QIWI = BetaTransferGateway(
        name="Qiwi",
        currency=BetaTransferCurrency.RUB,
        commission_in_percent=12,
        min_amount=100,
        max_amount=50000
    )
    """Qiwi payment type."""
    QIWI_CARD = BetaTransferGateway(
        name="Qiwi2",
        currency=BetaTransferCurrency.RUB,
        commission_in_percent=12,
        min_amount=500,
        max_amount=50000
    )
    """Qiwi Card payment type."""
    RUB_CARD = BetaTransferGateway(
        name="Card",
        currency=BetaTransferCurrency.RUB,
        commission_in_percent=12,
        min_amount=10,
        max_amount=75000
    )
    # """RUB card payment type."""
    UAH_CARD = BetaTransferGateway(
        name="Card1",
        currency=BetaTransferCurrency.UAH,
        commission_in_percent=10,
        min_amount=350,
        max_amount=10000
    )
    """UAH card payment type."""
    BYN_CARD = BetaTransferGateway(
        name="Card2",
        currency=BetaTransferCurrency.BYN,
        commission_in_percent=12,
        min_amount=30,
        max_amount=10000
    )
    """BYN card payment type."""
    BYN_CARD2 = BetaTransferGateway(
        name="Card3",
        currency=BetaTransferCurrency.BYN,
        commission_in_percent=12,
        min_amount=30,
        max_amount=5000
    )
    """BYN card payment type."""



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

    _public_key: Optional[str] = None
    _private_key: Optional[str] = None
    _payment_type: Optional[BetaTransferPaymentType] = None
    _url_result: Optional[str] = None
    _url_success: Optional[str] = None
    _url_fail: Optional[str] = None
    _locale: Optional[BetaTransferLocale] = None
    _charge_commission: Optional[ChargeCommission] = None
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
        "awaiting_confirmation": PaymentStatus.WAITING
    }

    def __init__(self,
                 amount: float,
                 description: str = "",
                 id: Optional[str] = None,
                 payment_type: Optional[BetaTransferPaymentType] = None,
                 url_result: Optional[str] = None,
                 url_success: Optional[str] = None,
                 url_fail: Optional[str] = None,
                 locale: Optional[BetaTransferLocale] = None,
                 charge_commission: Optional[ChargeCommission] = None,
                 payer_id: Optional[str] = None) -> None:
        """
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

        :raises NotAuthorizedError: When class was not authorized with BetaTransferPayment.authorize()
        :raises PaymentCreationError: When payment creation failed.
        """
        self._payment_type = BetaTransferPayment._payment_type if payment_type is None else payment_type
        self._url_result = BetaTransferPayment._url_result if url_result is None else url_result
        self._url_success = BetaTransferPayment._url_success if url_success is None else url_success
        self._url_fail = BetaTransferPayment._url_fail if url_fail is None else url_fail
        self._locale = BetaTransferPayment._locale if locale is None else locale
        self._charge_commission = BetaTransferPayment._charge_commission if charge_commission is None \
            else charge_commission
        self.payer_id = payer_id

        super().__init__(amount, description, id)

    def _validate_params(self):
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
            raise PaymentCreationError(f"Amount for {payment_type_name} must be between "
                                       f"{min_amount} and {max_amount} {currency_name}!")

        if self._payment_type == BetaTransferPaymentType.QIWI_CARD and not self.payer_id:
            raise PaymentCreationError("You should specify payer_id for Qiwi Card (Qiwi2)")

    @classmethod
    def authorize(cls,
                  public_key: str,
                  private_key: str,
                  payment_type: BetaTransferPaymentType = BetaTransferPaymentType.RUB_P2R,
                  url_result: Optional[str] = None,
                  url_success: Optional[str] = None,
                  url_fail: Optional[str] = None,
                  locale: BetaTransferLocale = BetaTransferLocale.RUSSIAN,
                  charge_commission: ChargeCommission = ChargeCommission.FROM_SELLER) -> None:
        """
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

        :raises AuthorizationError: When authorization fails.
        """
        BetaTransferPayment._public_key = public_key
        BetaTransferPayment._private_key = private_key
        BetaTransferPayment._payment_type = payment_type
        BetaTransferPayment._url_result = url_result
        BetaTransferPayment._url_success = url_success
        BetaTransferPayment._url_fail = url_fail
        BetaTransferPayment._locale = locale
        BetaTransferPayment._charge_commission = charge_commission

        cls._try_authorize()

    def _create_url(self) -> str:
        if not self._payment_type or not self._locale:
            raise PaymentCreationError("You must specify payment_type and locale!")

        params = {
            "token": BetaTransferPayment._public_key
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
            "payerId": self.payer_id
        }

        try:
            response = requests.post(BetaTransferPayment._PAYMENT_URL, headers=self._get_headers(), params=params,
                                     data=data)
        except Exception as e:
            raise PaymentCreationError(e)

        if response.status_code != 200:
            raise PaymentCreationError(response.text)

        return str(response.json().get("url"))

    @classmethod
    def get_status_and_income(cls, payment_id: str) -> Tuple[Optional[PaymentStatus], float]:
        params = {
            "token": BetaTransferPayment._public_key,
        }

        data = {
            "orderId": payment_id
        }
        data["sign"] = cls._get_sign(data)

        try:
            response = requests.get(BetaTransferPayment._INFO_URL, headers=cls._get_headers(), data=data, params=params)
        except Exception as e:
            raise PaymentGettingError(e)

        if response.status_code == 404:
            raise PaymentNotFound(f"Payment with id {payment_id} not found.")

        if response.status_code != 200:
            raise PaymentGettingError(response.text)

        payment: Mapping[str, Any] = response.json()

        status = payment.get("status")
        if status:
            status = BetaTransferPayment._STATUS_MAP.get(status)
        income = float(str(payment.get("balanceAmount")))
        return status, income

    @classmethod
    def _get_headers(cls) -> Mapping[str, str]:
        return {
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        }

    @classmethod
    def _try_authorize(cls) -> None:
        params = {
            "token": str(BetaTransferPayment._public_key),
        }
        params["sign"] = cls._get_sign(params)

        try:
            response = requests.get(BetaTransferPayment._ACCOUNT_INFO_URL, headers=cls._get_headers(), params=params)
        except Exception as e:
            raise AuthorizationError(e)

        if response.status_code != 200:
            raise AuthorizationError(response.text)

        BetaTransferPayment.authorized = True

    @classmethod
    def _get_sign(cls, data: Mapping[str, str]) -> str:
        sign = "".join(str(value) for value in data.values()) + str(BetaTransferPayment._private_key)
        return hashlib.md5(sign.encode()).hexdigest()

    @property
    def _amount_with_commission(self) -> float:
        if self._charge_commission == ChargeCommission.FROM_CUSTOMER and self._payment_type:
            return self.amount + self.amount * self._payment_type.value.commission_in_percent / 100

        return self.amount
