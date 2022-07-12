<h1 align="center">
  <br>
  <img src="logo.png" alt="PyPayment" height="300"></a>
  <br>
  PyPayment
  <br>
</h1>

<h4 align="center">Payment providers API wrapper.</h4>

<p align="center">
    <img src="https://img.shields.io/pypi/v/pypayment?color=orange" alt="PyPI">
    <img src="https://img.shields.io/pypi/pyversions/pypayment?color=blueviolet" alt="Python 3">
    <img src="https://github.com/TimNekk/pypayment/actions/workflows/tests.yml/badge.svg" alt="Tests">

</p>

<p align="center">
  <a href="#providers">Providers</a> •
  <a href="#installation">Installation</a> •
  <a href="#usage">Usage</a> •
  <a href="#enums">Enums</a> •
  <a href="#exceptions">Exceptions</a> •
  <a href="#contributing">Contributing</a> •
  <a href="#license">License</a>
</p>

## Providers:
- [Qiwi P2P](https://p2p.qiwi.com/) ([Usage](#qiwi))
- [YooMoney](https://yoomoney.ru/) ([Usage](#yoomoney))
- [PayOk](https://payok.io/) ([Usage](#yoomoney))

## Installation

Install the current version with [PyPI](https://pypi.org/project/pypayment/)

```bash
pip install -U pypayment
```

## Usage

The module provides an interface `Payment` for the unification of each payment provider.

It has 2 properties:

- `url` - Link to the created payment form.
- `status` - Current payment status.

```python
from pypayment import Payment
```


<details>
  <summary>
    <img src="https://icons.iconarchive.com/icons/cjdowner/cryptocurrency-flat/1024/Qiwi-icon.png" align="left" height="40">
    <br><br>
    <b>Qiwi</b>
  </summary>

#### Authorization

Before using `QiwiPayment` class you must authorize with [secret key](https://qiwi.com/p2p-admin/transfers/api) from QIWI P2P.

```python
from pypayment import QiwiPayment

QiwiPayment.authorize("my_secret_key")
```

You can set default parameters for every `QiwiPayment` instance.

- `theme_code` - Code for displaying custom name and colors of the form. (Get it [here](https://qiwi.com/p2p-admin/transfers/link))
- `expiration_duration` - Time that the invoice will be available for payment.
- `payment_type` - [QiwiPaymentType](#qiwi-payment-types) enum.

```python
from pypayment import QiwiPayment, QiwiPaymentType
from datetime import timedelta

QiwiPayment.authorize("my_secret_key",
                      theme_code="my_theme_code",
                      expiration_duration=timedelta(hours=1),
                      payment_type=QiwiPaymentType.CARD)
```

#### Creating invoice

To created new QIWI invoice, you need to instantiate `QiwiPayment` with 1 required parameter.

- `amount` - The amount to be invoiced. _(will be rounded to 2 decimal places)_

```python
from pypayment import Payment, QiwiPayment

payment: Payment = QiwiPayment(amount=123.45)

print(payment.url)  # https://oplata.qiwi.com/form/?invoice_uid=payment_unique_id
```

And 4 optional parameters that will override default ones for specific instance.

- `description` - Payment comment that will be displayed to user.
- `theme_code` - Code for displaying custom name and colors of the form. (Get it [here](https://qiwi.com/p2p-admin/transfers/link))
- `expiration_duration` - Time that the invoice will be available for payment.
- `payment_type` - [QiwiPaymentType](#qiwi-payment-types) enum.

```python
from pypayment import Payment, QiwiPayment, QiwiPaymentType
from datetime import timedelta

different_payment: Payment = QiwiPayment(amount=987.65,
                                         description="Flower pot",
                                         theme_code="my_new_theme_code",
                                         expiration_duration=timedelta(days=3),
                                         payment_type=QiwiPaymentType.CARD)

print(different_payment.url) # https://oplata.qiwi.com/form/?invoice_uid=payment_unique_id_2
```

_Recommended to put `QiwiPayment` into `Payment` variable to keep unification._

#### Getting status

To get payment [status](#payment-statuses), you need to use `status` property.

```python
from pypayment import Payment, QiwiPayment, PaymentStatus

payment: Payment = QiwiPayment(100)

if payment.status == PaymentStatus.PAID:
    print("Got ur money!")  # Got ur money!
```

#### Qiwi Payment Types

Enum `QiwiPaymentType` that represents every possible Qiwi payment type.

- `WALLET` - Payment with Qiwi wallet.
- `CARD` - Payment with bank card.
- `ALL` - Payment with every type possible.

</details>


<details>
  <summary>
    <img src="https://static.insales-cdn.com/files/1/19/20037651/original/_.png" align="left" height="40">
    <br><br>
    <b>YooMoney</b>
  </summary>

#### Getting access token

You need to get `access_token` to authorize.

- `client_id` - Create new application and copy client_id (Do it [here](https://yoomoney.ru/myservices/new))
- `redirect_uri` - redirect_uri you specified when creating the application.
- `instance_name` - (Optional) ID of the authorization instance in the application.

```python
from pypayment import YooMoneyPayment

YooMoneyPayment.get_access_token(client_id="my_client_id",
                                 redirect_uri="my_redirect_uri",
                                 instance_name="my_instance_name")  # access_token = XXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

#### Authorization

Before using `YooMoneyPayment` class you must authorize with [access_token](#getting-access-token).

```python
from pypayment import YooMoneyPayment

YooMoneyPayment.authorize("my_access_token")
```

You can set default parameters for every `YooMoneyPayment` instance.

- `payment_type` - [YooMoney Payment Type](#yoomoney-payment-types) enum.
- `charge_commission` - [Charge Commission](#charge-commission) enum.
- `success_url` - User will be redirected to this url after paying.

```python
from pypayment import YooMoneyPayment, YooMoneyPaymentType, ChargeCommission

YooMoneyPayment.authorize("my_access_token",
                          payment_type=YooMoneyPaymentType.CARD,
                          charge_commission=ChargeCommission.FROM_CUSTOMER,
                          success_url="my_success_url.com")
```

#### Creating invoice

To created new YooMoney invoice, you need to instantiate `YooMoneyPayment` with 1 required parameter.

- `amount` - The amount to be invoiced. _(will be rounded to 2 decimal places)_

```python
from pypayment import Payment, YooMoneyPayment

payment: Payment = YooMoneyPayment(amount=123.45)

print(payment.url)  # https://yoomoney.ru/transfer/quickpay?requestId=XXXXXXXXXXXXXXXXXXXXXXXXXX
```

And 3 optional parameters that will override default ones for specific instance.

- `description` - Payment comment that will be displayed to user.
- `payment_type` - [YooMoney Payment Type](#yoomoney-payment-types) enum.
- `charge_commission` - [Charge Commission](#charge-commission) enum.
- `success_url` - User will be redirected to this url after paying.

```python
from pypayment import Payment, YooMoneyPayment, YooMoneyPaymentType, ChargeCommission

different_payment: Payment = YooMoneyPayment(amount=987.65,
                                             description="Flower pot",
                                             payment_type=YooMoneyPaymentType.CARD,
                                             charge_commission=ChargeCommission.FROM_CUSTOMER,
                                             success_url="my_success_url.com")

print(different_payment.url)  # https://yoomoney.ru/transfer/quickpay?requestId=XXXXXXXXXXXXXXXXXXXXXXXXXX
```

_Recommended to put `YooMoneyPayment` into `Payment` variable to keep unification._

#### Getting status

To get payment [status](#payment-statuses), you need to use `status` property.

```python
from pypayment import Payment, YooMoneyPayment, PaymentStatus

payment: Payment = YooMoneyPayment(100)

if payment.status == PaymentStatus.PAID:
    print("Got ur money!")  # Got ur money!
```

#### YooMoney Payment Types

Enum `YooMoneyPaymentType` that represents every possible yoomoney payment type.

- `WALLET` - Payment with YooMoney wallet.
- `CARD` - Payment with bank card.
- `PHONE` - Payment from phone balance.

</details>


<details>
  <summary>
    <img src="https://payok.io/files/image/logo_white.svg" align="left" height="40">
    <br><br>
    <b>PayOk</b>
  </summary>

#### Authorization

Before using `PayOkPayment` class you must authorize with:

- [API Key](https://payok.io/cabinet/api.php)
- [API ID](https://payok.io/cabinet/api.php)
- [Shop ID](https://payok.io/cabinet/main.php)
- [Shop secret key](https://payok.io/cabinet/main.php)

```python
from pypayment import PayOkPayment

PayOkPayment.authorize("my_api_key", "my_api_id", "my_shop_id", "my_shop_secret_key")
```

You can set default parameters for every `PayOkPayment` instance.

- `payment_type` - [PayOkPaymentType](#payok-payment-types) enum.
- `currency` - [PayOkCurrency](#payok-currency) enum.
- `success_url` - User will be redirected to this url after paying.

```python
from pypayment import PayOkPayment, PayOkPaymentType, PayOkCurrency

PayOkPayment.authorize("my_api_key", "my_api_id", "my_shop_id", "my_shop_secret_key",
                        payment_type=PayOkPaymentType.CARD,
                        currency=PayOkCurrency.RUB,
                        success_url="my_success_url.com")
```

#### Creating invoice

To created new PayOk invoice, you need to instantiate `PayOkPayment` with 1 required parameter.

- `amount` - The amount to be invoiced.

```python
from pypayment import Payment, PayOkPayment

payment: Payment = PayOkPayment(amount=123)

print(payment.url)  # https://payok.io/pay?amount=XXX&...
```

And 4 optional parameters that will override default ones for specific instance.

- `description` - Payment comment that will be displayed to user.
- `payment_type` - [PayOkPaymentType](#payok-payment-types) enum.
- `currency` - [PayOkCurrency](#payok-currency) enum.
- `success_url` - User will be redirected to this url after paying.

```python
from pypayment import Payment, PayOkPayment, PayOkPaymentType, PayOkCurrency

different_payment: Payment = PayOkPayment(amount=987.65,
                                          description="Flower pot",
                                          payment_type=PayOkPaymentType.CARD,
                                          currency=PayOkCurrency.RUB,
                                          success_url="my_success_url.com")

print(different_payment.url) # https://payok.io/pay?amount=XXX&...
```

_Recommended to put `PayOkPayment` into `Payment` variable to keep unification._

#### Getting status

To get payment [status](#payment-statuses), you need to use `status` property.

```python
from pypayment import Payment, PayOkPayment, PaymentStatus

payment: Payment = PayOkPayment(100)

if payment.status == PaymentStatus.PAID:
    print("Got ur money!")  # Got ur money!
```

#### PayOk Payment Types

Enum `PayOkPaymentType` that represents every possible PayOk payment type.

- `CARD` - Payment with bank card.
- `QIWI` - Payment with QIWI.
- `YOOMONEY` - Payment with YooMoney.
- `WEBMONEY` - Payment with WebMoney.
- `PAYEER` - Payment with Payeer.
- `PERFECT_MONEY` - Payment with Perfect Money.
- `ADVCASH` - Payment with Advcash.
- `BEELINE` - Payment with Beeline.
- `MEGAFON` - Payment with Megafon.
- `TELE2` - Payment with Tele2.
- `MTS` - Payment with MTS.
- `QIWI_MOBILE` - Payment with QIWI Mobile.
- `BITCOIN` - Payment with Bitcoin.
- `LITECOIN` - Payment with Litecoin.
- `DOGECOIN` - Payment with Dogecoin.
- `DASH` - Payment with Dash.
- `ZCASH` - Payment with Zcash.

#### PayOk Currency

Enum `PayOkCurrency` that represents every possible PayOk currency.

- `RUB` - Russian ruble.
- `UAH` - Ukrainian hryvnia.
- `USD` - United States dollar.
- `EUR` - Euro.
- `RUB2` - Russian ruble. _(Alternative Gateway)_

</details>


## Enums

#### Charge Commission

Enum `ChargeCommission` that represents who will be charged the commission ([YooMoney commission](https://yoomoney.ru/docs/payment-buttons/using-api/forms#calculating-commissions)).

- `FROM_CUSTOMER` - Charge commission from customer.
- `FROM_SELLER` - Charge commission from seller.

#### Payment Statuses

Enum that represents every possible status of the invoice.

- `WAITING` - Payment has been created, but has not yet been paid.
- `PAID` - Payment was successfully paid.
- `REJECTED` - Payment was rejected.
- `EXPIRED` - Payment has expired.


## Exceptions

- `NotAuthorized` - Raised when payment provider class has not been authorized.
- `AuthorizationError` - Raised when authorization failed.
- `PaymentCreationError` - Raised when payment creation failed.
- `PaymentGettingError` - Raised when payment getting failed.

## Contributing

Bug reports and/or pull requests are welcome


## License

The module is available as open source under the terms of the [Apache License, Version 2.0](https://opensource.org/licenses/Apache-2.0)
