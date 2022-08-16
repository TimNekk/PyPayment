from datetime import timedelta
from typing import Optional, Mapping, Any

import requests

from pypayment import Payment, PaymentStatus, NotAuthorized, PaymentCreationError, PaymentGettingError, \
    AuthorizationError, ChargeCommission


class LavaPayment(Payment):
    authorized = False
    _token: Optional[str] = None
    _wallet_to: Optional[str] = None
    _expiration_duration: timedelta
    _charge_commission: ChargeCommission
    _success_url: Optional[str] = None
    _fail_url: Optional[str] = None
    _BASE_URL = "https://api.lava.ru"
    _PING_URL = _BASE_URL + "/test/ping"
    _INVOICE_URL = _BASE_URL + "/invoice"
    _CREATE_URL = _INVOICE_URL + "/create"
    _INFO_URL = _INVOICE_URL + "/info"
    _STATUS_MAP = {
        "success": PaymentStatus.PAID,
        "pending": PaymentStatus.WAITING,
        "cancel": PaymentStatus.REJECTED
    }

    def __init__(self,
                 amount: float,
                 description: str = "",
                 wallet_to: Optional[str] = None,
                 expiration_duration: Optional[timedelta] = None,
                 charge_commission: Optional[ChargeCommission] = None,
                 success_url: Optional[str] = None,
                 fail_url: Optional[str] = None):
        """
        You need to LavaPayment.authorize() first!

        Instantiation generates new Lava invoice instance right away.

        Passed parameters will be applied to instance, but won't override default ones.

        :param amount: The amount to be invoiced.
        :param description: Payment comment.
        :param wallet_to: Account number to which the funds will be credited. (e.x. R40510054)
        :param expiration_duration: The time that the invoice will be available for payment.
        :param charge_commission: ChargeCommission enum.
        :param success_url: User will be redirected to this url after paying.
        :param fail_url: User will be redirected to this url if payment failed.

        :raise NotAuthorized: When class was not authorized with LavaPayment.authorize()
        :raise PaymentCreationError: When payment creation failed.
        """
        if not LavaPayment.authorized:
            raise NotAuthorized("You need to authorize first: LavaPayment.authorize()")

        self._wallet_to = LavaPayment._wallet_to if wallet_to is None else wallet_to
        self._expiration_duration = LavaPayment._expiration_duration if expiration_duration is None else expiration_duration
        self._charge_commission = LavaPayment._charge_commission if charge_commission is None else charge_commission
        self._success_url = LavaPayment._success_url if success_url is None else success_url
        self._fail_url = LavaPayment._fail_url if fail_url is None else fail_url

        super().__init__(amount, description)

        self._url = self._create()

    @classmethod
    def _get_headers(cls) -> Mapping[str, str]:
        return {
            "Authorization": str(cls._token),
            "Accept": "application/json"
        }

    @classmethod
    def authorize(cls,
                  token: str,
                  wallet_to: str,
                  expiration_duration: timedelta = timedelta(hours=1),
                  charge_commission: ChargeCommission = ChargeCommission.FROM_SELLER,
                  success_url: Optional[str] = None,
                  fail_url: Optional[str] = None) -> None:
        """
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
        LavaPayment._token = token
        LavaPayment._wallet_to = wallet_to
        LavaPayment._expiration_duration = expiration_duration
        LavaPayment._charge_commission = charge_commission
        LavaPayment._success_url = success_url
        LavaPayment._fail_url = fail_url

        cls._try_authorize()

    @classmethod
    def _try_authorize(cls) -> None:
        try:
            response = requests.get(LavaPayment._PING_URL, headers=LavaPayment._get_headers()).json()
        except Exception as e:
            raise AuthorizationError(e)

        if response.get("status") is not True:
            raise AuthorizationError(response.get("message"))

        cls.authorized = True

    def _create(self) -> str:
        data = {
            "wallet_to": self._wallet_to,
            "sum": round(self.amount, 2),
            "order_id": self.id,
            "success_url": self._success_url,
            "fail_url": self._fail_url,
            "expire": int(self._expiration_duration.seconds / 60),
            "subtract": 1 if self._charge_commission == ChargeCommission.FROM_CUSTOMER else 0,
            "comment": self.description
        }

        try:
            response = requests.post(LavaPayment._CREATE_URL, headers=LavaPayment._get_headers(), data=data)
        except Exception as e:
            raise PaymentCreationError(e)

        if response.status_code != 200 or response.json().get("status") != "success":
            raise PaymentCreationError(response.text)

        return str(response.json().get("url"))

    def _get_payment(self) -> Optional[Mapping[str, Any]]:
        try:
            response = requests.post(LavaPayment._INFO_URL,
                                     headers=LavaPayment._get_headers(),
                                     data={"order_id": self.id})
        except Exception as e:
            raise PaymentGettingError(e)

        response_json = response.json()
        if response.status_code != 200 or response_json.get("status") != "success":
            raise PaymentCreationError(response.text)

        if response_json.get("invoice"):
            payment: Mapping[str, Any] = response_json.get("invoice")
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
                status = LavaPayment._STATUS_MAP.get(str(status_literal))

        return status if status else PaymentStatus.WAITING

    @property
    def income(self) -> Optional[float]:
        payment = self._get_payment()

        if payment:
            return float(str(payment.get("sum")))

        return None
