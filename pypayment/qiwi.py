import json
from datetime import datetime, timedelta
from enum import Enum
from typing import Optional, Mapping, Any

import requests

from pypayment import Payment, PaymentStatus, NotAuthorized, PaymentCreationError, PaymentGettingError, \
    AuthorizationError


class QiwiPaymentType(Enum):
    WALLET = "qw"
    """Payment with Qiwi wallet."""
    CARD = "card"
    """Payment with bank card."""
    ALL = ""
    """Payment with every type possible."""


class QiwiPayment(Payment):
    authorized = False
    _secret_key: Optional[str] = None
    _theme_code: Optional[str] = None
    _expiration_duration: timedelta
    _payment_type: QiwiPaymentType
    _API_URL = "https://api.qiwi.com/partner/bill/v1/bills/"
    _STATUS_MAP = {
        "WAITING": PaymentStatus.WAITING,
        "PAID": PaymentStatus.PAID,
        "REJECTED": PaymentStatus.REJECTED,
        "EXPIRED": PaymentStatus.EXPIRED
    }

    def __init__(self,
                 amount: float,
                 description: str = "",
                 theme_code: Optional[str] = None,
                 expiration_duration: Optional[timedelta] = None,
                 payment_type: Optional[QiwiPaymentType] = None):
        """
        You need to QiwiPayment.authorize() first!

        Instantiation generates new QIWI invoice instance right away.

        Passed parameters will be applied to instance, but won't override default ones.

        :param amount: The amount to be invoiced.
        :param description: Payment comment.
        :param theme_code: Theme code from https://qiwi.com/p2p-admin/transfers/link
        :param expiration_duration: Time that the invoice will be available for payment.
        :param payment_type: QiwiPaymentType enum.

        :raise NotAuthorized: When class was not authorized with QiwiPayment.authorize()
        :raise PaymentCreationError: When payment creation failed.
        """
        if not QiwiPayment.authorized:
            raise NotAuthorized("You need to authorize first: QiwiPayment.authorize()")

        self._theme_code = QiwiPayment._theme_code if theme_code is None else theme_code
        self._expiration_duration = QiwiPayment._expiration_duration if expiration_duration is None else expiration_duration
        self._payment_type = QiwiPayment._payment_type if payment_type is None else payment_type

        super().__init__(amount, description)

        self._url = self._create()

    @classmethod
    def _get_headers(cls) -> Mapping[str, str]:
        return {
            "Authorization": f"Bearer {cls._secret_key}",
            "Content-Type": "application/json",
            "Accept": "application/json"
        }

    @classmethod
    def authorize(cls,
                  secret_key: str,
                  theme_code: Optional[str] = None,
                  expiration_duration: timedelta = timedelta(hours=1),
                  payment_type: QiwiPaymentType = QiwiPaymentType.ALL) -> None:
        """
        Must be called before the first use of the class!

        Tries to authorize to Qiwi p2p API.
        Saves passed parameters as default.

        :param secret_key: Secret key from https://qiwi.com/p2p-admin/transfers/api
        :param theme_code: Theme code from https://qiwi.com/p2p-admin/transfers/link
        :param expiration_duration: The time that the invoice will be available for payment.
        :param payment_type: QiwiPaymentType enum.

        :raise AuthorizationError: When authorization fails.
        """
        QiwiPayment._secret_key = secret_key
        QiwiPayment._theme_code = theme_code
        QiwiPayment._expiration_duration = expiration_duration
        QiwiPayment._payment_type = payment_type

        cls._try_authorize()

    @classmethod
    def _try_authorize(cls) -> None:
        try:
            response = requests.get(QiwiPayment._API_URL, headers=QiwiPayment._get_headers())
        except Exception as e:
            raise AuthorizationError(e)

        if response.status_code == 401:
            raise AuthorizationError("Secret key is invalid.")

        cls.authorized = True

    def _create(self) -> str:
        data = {
            "amount": {
                "currency": "RUB",
                "value": round(self.amount, 2)
            },
            "comment": self.description,
            "expirationDateTime": (
                        datetime.now().replace(microsecond=0).astimezone() + self._expiration_duration).isoformat(),
            "customFields": {
                "themeCode": self._theme_code,
                "paySourcesFilter": self._payment_type.value
            }
        }

        try:
            response = requests.put(QiwiPayment._API_URL + self.id, headers=QiwiPayment._get_headers(),
                                    data=json.dumps(data))
        except Exception as e:
            raise PaymentCreationError(e)

        if response.status_code != 200:
            raise PaymentCreationError(response.text)

        return str(response.json().get("payUrl"))

    def _get_payment(self) -> Optional[Mapping[str, Any]]:
        try:
            response = requests.get(QiwiPayment._API_URL + self.id, headers=QiwiPayment._get_headers())
        except Exception as e:
            raise PaymentGettingError(e)

        if response.status_code != 200:
            raise PaymentGettingError(response.text)

        if response:
            payment: Mapping[str, Any] = response.json()
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
            status_literal = payment.get("status")
            if status_literal:
                status = QiwiPayment._STATUS_MAP.get(status_literal.get("value"))

        return status if status else PaymentStatus.WAITING

    @property
    def income(self) -> Optional[float]:
        payment = self._get_payment()

        if payment:
            amount = payment.get("amount")
            if amount:
                return float(amount.get("value"))

        return None
