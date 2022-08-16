from enum import Enum
from typing import Optional, Mapping, Any

import requests

from pypayment import Payment, PaymentStatus, NotAuthorized, PaymentCreationError, PaymentGettingError, \
    AuthorizationError, ChargeCommission


class YooMoneyPaymentType(Enum):
    WALLET = "PC"
    """Payment with YooMoney wallet."""
    CARD = "AC"
    """Payment with bank card."""
    PHONE = "MC"
    """Payment from phone balance."""


class YooMoneyPayment(Payment):
    authorized = False
    _access_token: str
    _account_id: Optional[str] = None
    _payment_type: YooMoneyPaymentType
    _charge_commission: ChargeCommission
    _success_url: Optional[str] = None
    _BASE_URL = "https://yoomoney.ru"
    _OAUTH_URL = _BASE_URL + "/oauth"
    _API_URL = _BASE_URL + "/api"
    _QUICKPAY_URL = _BASE_URL + "/quickpay/confirm.xml"
    _AUTHORIZE_URL = _OAUTH_URL + "/authorize"
    _TOKEN_URL = _OAUTH_URL + "/token"
    _ACCOUNT_INFO_URL = _API_URL + "/account-info"
    _OPERATION_HISTORY_URL = _API_URL + "/operation-history"
    _STATUS_MAP = {
        "success": PaymentStatus.PAID,
        "refused": PaymentStatus.REJECTED,
        "in_progress": PaymentStatus.WAITING
    }

    def __init__(self,
                 amount: float,
                 description: str = "",
                 payment_type: Optional[YooMoneyPaymentType] = None,
                 charge_commission: Optional[ChargeCommission] = None,
                 success_url: Optional[str] = None):
        """
        You need to YooMoneyPayment.authorize() first!

        Instantiation generates new YooMoney invoice instance right away.

        Passed parameters will be applied to instance, but won't override default ones.

        :param amount: The amount to be invoiced.
        :param payment_type: YooMoneyPaymentType enum.
        :param success_url: User will be redirected to this url after paying.

        :raise NotAuthorized: When class was not authorized with YooMoneyPayment.authorize()
        :raise PaymentCreationError: When payment creation failed.
        """
        if not YooMoneyPayment.authorized:
            raise NotAuthorized("You need to authorize first: YooMoneyPayment.authorize()")

        self._payment_type = YooMoneyPayment._payment_type if payment_type is None else payment_type
        self._charge_commission = YooMoneyPayment._charge_commission if charge_commission is None else charge_commission
        self._success_url = YooMoneyPayment._success_url if success_url is None else success_url

        super().__init__(amount, description)

        self._url = self._create()

    @classmethod
    def get_access_token(cls,
                         client_id: str,
                         redirect_uri: str,
                         instance_name: Optional[str] = "") -> Optional[str]:
        """
        Gets access_token from client_id.

        You need to call method only once, to get access_token required in YooMoneyPayment.authorize().

        :param client_id: client_id from https://yoomoney.ru/myservices/new
        :param redirect_uri: redirect_uri you specified when creating the application.
        :param instance_name: ID of the authorization instance in the application.
        """
        data = {
            "client_id": client_id,
            "response_type": "code",
            "redirect_uri": redirect_uri,
            "scope": "account-info operation-history",
        }

        if instance_name:
            data["instance_name"] = instance_name

        response = requests.post(cls._AUTHORIZE_URL, data=data)
        print("1)\tGo to this URL and give access to the application\n",
              f"\t{response.url}\n\n",
              f"2)\tAfter accepting you will be redirected to {redirect_uri}?code=YOUR_CODE_VALUE with \"code\" as query parameter")
        code = input("\tCopy YOUR_CODE_VALUE OR whole redirect url and paste it here: ")

        try:
            code = code[code.index("code=") + 5:].replace(" ", "")
        except ValueError:
            pass

        data = {
            'code': code,
            'client_id': client_id,
            'grant_type': 'authorization_code',
            'redirect_uri': redirect_uri,
        }

        response = requests.post(cls._TOKEN_URL, data=data)
        access_token: str = response.json()['access_token']

        if access_token == "":
            print("\n3)\tSomething went wrong, try again")
            return ""

        print("\n3)\tYour access token:\n",
              "\t(Save it and use in YooMoneyPayment.authorize())\n",
              access_token)

        return access_token

    @classmethod
    def _get_headers(cls) -> Mapping[str, str]:
        return {
            "Authorization": f"Bearer {cls._access_token}",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json"
        }

    @classmethod
    def authorize(cls,
                  access_token: str,
                  payment_type: YooMoneyPaymentType = YooMoneyPaymentType.CARD,
                  charge_commission: ChargeCommission = ChargeCommission.FROM_SELLER,
                  success_url: Optional[str] = None) -> None:
        """
        Must be called before the first use of the class!

        Tries to authorize to YooMoney API.
        Saves passed parameters as default.

        :param access_token: Use YooMoneyPayment.get_access_token() to get it.
        :param payment_type: YooMoneyPaymentType enum.
        :param charge_commission: ChargeCommission enum.
        :param success_url: User will be redirected to this url after paying.

        :raise AuthorizationError: When authorization fails.
        """
        YooMoneyPayment._access_token = access_token
        YooMoneyPayment._payment_type = payment_type
        YooMoneyPayment._charge_commission = charge_commission
        YooMoneyPayment._success_url = success_url

        cls._try_authorize()

    @classmethod
    def _try_authorize(cls) -> None:
        try:
            response = requests.get(cls._ACCOUNT_INFO_URL, headers=cls._get_headers())
        except Exception as e:
            raise AuthorizationError(e)

        if response.status_code != 200:
            raise AuthorizationError("Access Token is invalid.")

        cls._account_id = response.json().get('account')
        cls.authorized = True

    def _create(self) -> str:
        data = {
            "receiver": YooMoneyPayment._account_id,
            "quickpay-form": "shop",
            "targets": self.id,
            "paymentType": self._payment_type.value,
            "sum": self.sum_with_commission,
            "formcomment": self.description,
            "short-dest": self.description,
            "label": self.id,
            "successURL": self._success_url
        }

        try:
            response = requests.post(YooMoneyPayment._QUICKPAY_URL, headers=YooMoneyPayment._get_headers(), data=data)
        except Exception as e:
            raise PaymentCreationError(e)

        if response.status_code != 200:
            raise PaymentCreationError(response.text)

        return str(response.url)

    @property
    def sum_with_commission(self) -> float:
        if self._charge_commission == ChargeCommission.FROM_CUSTOMER:
            if self._payment_type == YooMoneyPaymentType.WALLET:
                # https://yoomoney.ru/docs/payment-buttons/using-api/forms?lang=en#:~:text=YooMoney%20wallet%0APC,and%202%C2%A0kopecks.
                commission_multiplier = 0.005
                return self.amount * (1 + commission_multiplier)

            elif self._payment_type == YooMoneyPaymentType.CARD:
                # https://yoomoney.ru/docs/payment-buttons/using-api/forms?lang=en#:~:text=Bank%20card%0AAC,get%20980%C2%A0rubles.
                commission_multiplier = 0.02
                return self.amount / (1 - commission_multiplier)

        return self.amount

    def _get_payment(self) -> Optional[Mapping[str, Any]]:
        try:
            response = requests.post(YooMoneyPayment._OPERATION_HISTORY_URL,
                                     headers=YooMoneyPayment._get_headers(),
                                     data={"label": self.id})
        except Exception as e:
            raise PaymentGettingError(e)

        if response.status_code != 200:
            raise PaymentGettingError(response.text)

        operations = response.json().get("operations")

        if operations:
            payment: Mapping[str, Any] = operations[0]
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
            status = YooMoneyPayment._STATUS_MAP.get(str(payment.get("status")))

        return status if status else PaymentStatus.WAITING

    @property
    def income(self) -> Optional[float]:
        payment = self._get_payment()

        if payment:
            return payment.get("amount")

        return None
