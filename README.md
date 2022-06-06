# PyPayment

![PyPI](https://img.shields.io/pypi/v/pypayment?color=orange) ![Python 3](https://img.shields.io/pypi/pyversions/nalog?color=blueviolet)

**pypayment** - Payment providers API wrapper.

Available providers:
- [Qiwi P2P](https://p2p.qiwi.com/) ([Usage](#qiwi))

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

### Qiwi

#### Authorization

Before using `QiwiPayment` class you must authorize with [secret key](https://qiwi.com/p2p-admin/transfers/api) from QIWI P2P.

```python
from pypayment import QiwiPayment

QiwiPayment.authorize("my_secret_key")
```

You can set default parameters for every `QiwiPayment` instance.

- `theme_code` - Code for displaying custom name and colors of the form. (Get it [here](https://qiwi.com/p2p-admin/transfers/link))
- `expiration_duration` - Time that the invoice will be available for payment.

```python
from pypayment import QiwiPayment
from datetime import timedelta

QiwiPayment.authorize("my_secret_key",
                      theme_code="my_theme_code",
                      expiration_duration=timedelta(hours=1))
```

#### Creating invoice

To created new QIWI invoice, you need to instantiate `QiwiPayment` with 1 required parameter.

- `amount` - The amount to be invoiced. _(will be rounded to 2 decimal places)_

```python
from pypayment import Payment, QiwiPayment

payment: Payment = QiwiPayment(amount=123.45)

print(payment.url)  # https://oplata.qiwi.com/form/?invoice_uid=payment_unique_id
```

And 3 optional parameters that will override default ones for specific instance.

- `description` - Payment comment that will be displayed to user.
- `theme_code` - Code for displaying custom name and colors of the form. (Get it [here](https://qiwi.com/p2p-admin/transfers/link))
- `expiration_duration` - Time that the invoice will be available for payment.

```python
from pypayment import Payment, QiwiPayment
from datetime import timedelta

different_payment: Payment = QiwiPayment(amount=987.65,
                                         description="Flower pot",
                                         theme_code="my_new_theme_code",
                                         expiration_duration=timedelta(days=3))

print(different_payment.url) # https://oplata.qiwi.com/form/?invoice_uid=payment_unique_id_2
```

_Recommended to put `QiwiPayment` into `Payment` variable to keep unification._

#### Getting status

To get payment [status](#payment-status), you need to use `status` property.

```python
from pypayment import Payment, QiwiPayment, PaymentStatus

payment: Payment = QiwiPayment(100)

if payment.status == PaymentStatus.PAID:
    print("Got ur money!")  # Got ur money!
```

### Payment Statuses

Enum that represents every possible status of the invoice.

- `WAITING` - Payment has been created, but has not yet been paid.
- `PAID` - Payment was successfully paid.
- `REJECTED` - Payment was rejected.
- `EXPIRED` - Payment has expired.

### Exceptions

- `NotAuthorized` - Raised when payment provider class has not been authorized.
- `AuthorizationError` - Raised when authorization failed.
- `PaymentCreationError` - Raised when payment creation failed.
- `PaymentGettingError` - Raised when payment getting failed.

## Contributing

Bug reports and/or pull requests are welcome


## License

The module is available as open source under the terms of the [Apache License, Version 2.0](https://opensource.org/licenses/Apache-2.0)