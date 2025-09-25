from __future__ import annotations

import json
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from collections.abc import Mapping
from datetime import datetime, timedelta
from enum import Enum
from typing import Any

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


class QiwiPaymentType(Enum):
    """Qiwi payment type enum."""

    WALLET = "qw"
    """Payment with Qiwi wallet."""
    CARD = "card"
    """Payment with bank card."""
    ALL = ""
    """Payment with every type possible."""


class QiwiPayment(Payment):
    """Qiwi payment class."""

    _secret_key: str | None = None
    _theme_code: str | None = None
    _expiration_duration: timedelta | None = None
    _payment_type: QiwiPaymentType | None = None
    _API_URL = "https://api.qiwi.com/partner/bill/v1/bills/"
    _STATUS_MAP = {
        "WAITING": PaymentStatus.WAITING,
        "PAID": PaymentStatus.PAID,
        "REJECTED": PaymentStatus.REJECTED,
        "EXPIRED": PaymentStatus.EXPIRED,
    }

    def __init__(
        self,
        amount: float,
        description: str = "",
        id: str | None = None,
        theme_code: str | None = None,
        expiration_duration: timedelta | None = None,
        payment_type: QiwiPaymentType | None = None,
    ) -> None:
        """Authorize QiwiPayment class.

        You need to QiwiPayment.authorize() first!

        Instantiation generates new QIWI invoice instance right away.

        Passed parameters will be applied to instance, but won't override default ones.

        :param amount: The amount to be invoiced.
        :param description: Payment comment.
        :param id: Unique Payment ID (default: generated with uuid4).
        :param theme_code: Theme code from https://qiwi.com/p2p-admin/transfers/link
        :param expiration_duration: Time that the invoice will be available for payment.
        :param payment_type: QiwiPaymentType enum.

        :raise NotAuthorized: When class was not authorized with QiwiPayment.authorize()
        :raise PaymentCreationError: When payment creation failed.
        """
        self._theme_code = theme_code or self._theme_code
        self._expiration_duration = expiration_duration or self._expiration_duration
        self._payment_type = payment_type or self._payment_type

        super().__init__(amount, description, id)

    @classmethod
    def authorize(
        cls,
        secret_key: str,
        theme_code: str | None = None,
        expiration_duration: timedelta = timedelta(hours=1),
        payment_type: QiwiPaymentType = QiwiPaymentType.ALL,
    ) -> None:
        """Authorize QiwiPayment class.

        Must be called before the first use of the class!

        Tries to authorize to Qiwi p2p API.
        Saves passed parameters as default.

        :param secret_key: Secret key from https://qiwi.com/p2p-admin/transfers/api
        :param theme_code: Theme code from https://qiwi.com/p2p-admin/transfers/link
        :param expiration_duration: The time that the invoice will be available for payment.
        :param payment_type: QiwiPaymentType enum.

        :raise AuthorizationError: When authorization fails.
        """
        cls._secret_key = secret_key
        cls._theme_code = theme_code
        cls._expiration_duration = expiration_duration
        cls._payment_type = payment_type

        cls._try_authorize()

    def _create_url(self) -> str:
        data = {
            "amount": {
                "currency": "RUB",
                "value": self.amount,
            },
            "comment": self.description,
            "expirationDateTime": (
                datetime.now().replace(microsecond=0).astimezone() + self._expiration_duration
            ).isoformat() if self._expiration_duration else None,
            "customFields": {
                "themeCode": self._theme_code,
                "paySourcesFilter": self._payment_type.value if self._payment_type else None,
            },
        }

        try:
            response = requests.put(
                self._API_URL + self.id,
                headers=self._get_headers(),
                data=json.dumps(data),
                timeout=10,
            )
        except RequestException as e:
            raise PaymentCreationError() from e

        if response.status_code != requests.codes.ok:
            raise PaymentCreationError(response.text)

        return str(response.json().get("payUrl"))

    @classmethod
    def get_status_and_income(cls, payment_id: str) -> tuple[PaymentStatus | None, float]:
        try:
            response = requests.get(
                cls._API_URL + payment_id,
                headers=cls._get_headers(),
                timeout=10,
            )
        except RequestException as e:
            raise PaymentGettingError() from e

        if response.status_code != requests.codes.ok:
            raise PaymentGettingError(response.text)

        if not response:
            raise PaymentNotFound(f"Payment with id {payment_id} not found.")

        payment: Mapping[str, Any] = response.json()

        status_literal = payment.get("status")
        status = None
        if status_literal:
            status = cls._STATUS_MAP.get(status_literal.get("value"))

        amount = payment.get("amount")
        income = 0.0
        if amount:
            income = float(amount.get("value"))

        return status, income

    @classmethod
    def _get_headers(cls) -> Mapping[str, str]:
        return {
            "Authorization": f"Bearer {cls._secret_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    @classmethod
    def _try_authorize(cls) -> None:
        try:
            response = requests.get(
                cls._API_URL,
                headers=cls._get_headers(),
                timeout=10,
            )
        except RequestException as e:
            raise AuthorizationError() from e

        if response.status_code == requests.codes.unauthorized:
            raise AuthorizationError("Secret key is invalid.")

        cls.authorized = True
