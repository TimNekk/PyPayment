from __future__ import annotations

from datetime import timedelta
from typing import TYPE_CHECKING, Any

import requests
from requests import RequestException

from pypayment import (
    AuthorizationError,
    ChargeCommission,
    Payment,
    PaymentCreationError,
    PaymentGettingError,
    PaymentStatus,
)

if TYPE_CHECKING:
    from collections.abc import Mapping

class LavaPayment(Payment):
    """Lava payment class."""

    _token: str | None = None
    _wallet_to: str | None = None
    _expiration_duration: timedelta | None = None
    _charge_commission: ChargeCommission | None = None
    _success_url: str | None = None
    _fail_url: str | None = None
    _BASE_URL = "https://api.lava.ru"
    _PING_URL = _BASE_URL + "/test/ping"
    _INVOICE_URL = _BASE_URL + "/invoice"
    _CREATING_URL = _INVOICE_URL + "/create"
    _INFO_URL = _INVOICE_URL + "/info"
    _STATUS_MAP = {
        "success": PaymentStatus.PAID,
        "pending": PaymentStatus.WAITING,
        "cancel": PaymentStatus.REJECTED,
    }

    def __init__(
        self,
        amount: float,
        description: str = "",
        id: str | None = None,
        wallet_to: str | None = None,
        expiration_duration: timedelta | None = None,
        charge_commission: ChargeCommission | None = None,
        success_url: str | None = None,
        fail_url: str | None = None,
    ) -> None:
        """Authorize LavaPayment class.

        You need to LavaPayment.authorize() first!

        Instantiation generates new Lava invoice instance right away.

        Passed parameters will be applied to instance, but won't override default ones.

        :param amount: The amount to be invoiced.
        :param description: Payment comment.
        :param id: Unique Payment ID (default: generated with uuid4).
        :param wallet_to: Account number to which the funds will be credited. (e.x. R40510054)
        :param expiration_duration: The time that the invoice will be available for payment.
        :param charge_commission: ChargeCommission enum.
        :param success_url: User will be redirected to this url after paying.
        :param fail_url: User will be redirected to this url if payment failed.

        :raise NotAuthorized: When class was not authorized with LavaPayment.authorize()
        :raise PaymentCreationError: When payment creation failed.
        """
        self._wallet_to = wallet_to or self._wallet_to
        self._expiration_duration = expiration_duration or self._expiration_duration
        self._charge_commission = charge_commission or self._charge_commission
        self._success_url = success_url or self._success_url
        self._fail_url = fail_url or self._fail_url

        super().__init__(amount, description, id)

    @classmethod
    def authorize(
        cls,
        token: str,
        wallet_to: str,
        expiration_duration: timedelta = timedelta(hours=1),
        charge_commission: ChargeCommission = ChargeCommission.FROM_SELLER,
        success_url: str | None = None,
        fail_url: str | None = None,
    ) -> None:
        """Authorize LavaPayment class.

        Must be called before the first use of the class!

        Tries to authorize to Lava API.
        Saves passed parameters as default.

        :param token: Secret key from https://lava.ru/dashboard/settings/api
        :param wallet_to: Account number to which the funds will be credited. (e.x. R40510054)
        :param expiration_duration: The time that the invoice will be available for payment.
        :param charge_commission: ChargeCommission enum.
        :param success_url: User will be redirected to this url after paying.
        :param fail_url: User will be redirected to this url if payment failed.

        :raise PaymentCreationError: When authorization fails.
        """
        cls._token = token
        cls._wallet_to = wallet_to
        cls._expiration_duration = expiration_duration
        cls._charge_commission = charge_commission
        cls._success_url = success_url
        cls._fail_url = fail_url

        cls._try_authorize()

    def _create_url(self) -> str:
        data = {
            "wallet_to": self._wallet_to,
            "sum": self.amount,
            "order_id": self.id,
            "success_url": self._success_url,
            "fail_url": self._fail_url,
            "expire": int(self._expiration_duration.seconds / 60) if self._expiration_duration else 0,
            "subtract": 1 if self._charge_commission == ChargeCommission.FROM_CUSTOMER else 0,
            "comment": self.description,
        }

        try:
            response = requests.post(
                self._CREATING_URL,
                headers=self._get_headers(),
                data=data,
                timeout=10,
            )
        except RequestException as e:
            raise PaymentCreationError() from e

        if response.status_code != requests.codes.ok or response.json().get("status") != "success":
            raise PaymentCreationError(response.text)

        return str(response.json().get("url"))

    def update(self) -> None:
        try:
            response = requests.post(
                self._INFO_URL,
                headers=self._get_headers(),
                data={"order_id": self.id},
                timeout=10,
            )
        except RequestException as e:
            raise PaymentGettingError() from e

        response_json = response.json()
        if response.status_code != requests.codes.ok or response_json.get("status") != "success":
            raise PaymentCreationError(response.text)

        payment: Mapping[str, Any] = response_json.get("invoice")

        if not payment:
            return

        status_literal = payment.get("status")
        if status_literal:
            status = self._STATUS_MAP.get(str(status_literal))
            if status:
                self.status = status

        self.income = float(str(payment.get("sum")))

    @classmethod
    def _get_headers(cls) -> Mapping[str, str]:
        return {
            "Authorization": str(cls._token),
            "Accept": "application/json",
        }

    @classmethod
    def _try_authorize(cls) -> None:
        try:
            response = requests.get(
                cls._PING_URL,
                headers=cls._get_headers(),
                timeout=10,
            ).json()
        except RequestException as e:
            raise AuthorizationError() from e

        if response.get("status") is not True:
            raise AuthorizationError(response.get("message"))

        cls.authorized = True
