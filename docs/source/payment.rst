*****************
Payment providers
*****************

Payment Interface
==================

Interface for every payment is ``Payment``.

It has properties:

- ``authorized`` - Is payment provider class authorized.
- ``id`` - ID of the payment.
- ``amount`` - Amount to be invoiced. *(May not include commission.)*
- ``description`` - Payment description/comment.
- ``status`` - :ref:`PaymentStatus`.
- ``income`` - Income amount.
- ``url`` - Payment URL.

And methods:

- ``update`` - Update payment status and income.

| Before using any payment provider, you must authorize it with ``authorize()`` method.
| It accepts specific arguments for every payment provider such as ``token``, ``key`` e.t.c.
| It also accepts optional arguments such as ``success_url``, ``expiration_duration`` e.t.c. that sets default values for every payment of this provider.
| However, you can override them while instantiating payment.

To create payment, you need to instantiate chosen payment provider class with required argument ``amount`` and optional arguments ``description``, ``id``, and other arguments specific for every provider.

After that, ``url`` property will be available.

To get current payment ``status`` and ``income`` from provider's server, you need to call ``update()`` method first.

.. _Qiwi:

Qiwi
==================

QiwiPayment
***********

Qiwi payment provider class is ``QiwiPayment``.

Arguments for authorization:

- ``secret_key`` - Qiwi `secret key <https://qiwi.com/p2p-admin/transfers/api>`_.

Settings arguments:

- ``theme_code`` - Code for displaying custom name and colors of the form. (Get it `here <https://qiwi.com/p2p-admin/transfers/link>`_)
- ``expiration_duration`` - Time that the invoice will be available for payment.
- ``payment_type`` - `QiwiPaymentType`_ enum.

.. note ::

    You can set default setting for every payment of ``QiwiPayment`` and override them for specific payment.

.. code-block:: python
    
    from pypayment import QiwiPayment, QiwiPaymentType
    from datetime import timedelta

    # Set default setting
    QiwiPayment.authorize("my_secret_key",
                          theme_code="my_theme_code",
                          expiration_duration=timedelta(hours=1),
                          payment_type=QiwiPaymentType.CARD)

    # Override setting for specific payment
    payment = QiwiPayment(amount=100,
                          description="My payment",
                          theme_code="override_theme_code",
                          expiration_duration=timedelta(hours=3),
                          payment_type=QiwiPaymentType.WALLET)


QiwiPaymentType
***************

Enum for ``payment_type`` setting argument:

- ``WALLET`` - Payment using Qiwi wallet.
- ``CARD`` - Payment using bank card.
- ``ALL`` - Payment using every type possible.

.. _YooMoney:

YooMoney
========

YooMoneyPayment
***************

YooMoney payment provider class is ``YooMoneyPayment``.

You need to get `access_token` to authorize.

- ``client_id`` - Create new application and copy client_id (Do it `here <https://yoomoney.ru/myservices/new>`_)
- ``redirect_uri`` - redirect_uri you specified when creating the application.
- ``instance_name`` - (Optional) ID of the authorization instance in the application.

.. code-block:: python

    from pypayment import YooMoneyPayment

    YooMoneyPayment.get_access_token(client_id="my_client_id",
                                     redirect_uri="my_redirect_uri",
                                     instance_name="my_instance_name")  # access_token = XXXXXX.XXXXXXXXXXXXXXXXXXXXXXXXXXXX

.. hint::

    You should use ``YooMoneyPayment.get_access_token()`` to get access_token once and save it. You don't need to get it every time.

Arguments for authorization:

- ``access_token`` - YooMoney access token.

Settings arguments:

- ``payment_type`` - `YooMoneyPaymentType`_ enum.
- ``charge_commission`` - :ref:`ChargeCommission` enum.
- ``success_url`` - User will be redirected to this url after paying.

.. note ::

    You can set default setting for every payment of ``YooMoneyPayment`` and override them for specific payment.

.. code-block:: python

    from pypayment import YooMoneyPayment, YooMoneyPaymentType, ChargeCommission

    # Set default setting
    YooMoneyPayment.authorize("my_access_token",
                              payment_type=YooMoneyPaymentType.CARD,
                              charge_commission=ChargeCommission.FROM_CUSTOMER,
                              success_url="my_success_url.com")

    # Override default values
    payment = YooMoneyPayment(amount=100,
                              description="My payment",
                              payment_type=YooMoneyPaymentType.WALLET,
                              charge_commission=ChargeCommission.FROM_SELLER,
                              success_url="override_success_url.com")

YooMoneyPaymentType
*******************

Enum for ``payment_type`` setting argument:

- ``WALLET`` - Payment with YooMoney wallet.
- ``CARD`` - Payment with bank card.
- ``PHONE`` - Payment from phone balance.

.. _PayOk:

PayOk
=====

PayOkPayment
************

PayOk payment provider class is ``PayOkPayment``.

Arguments for authorization:

- ``api_key`` - PayOk `API Key <https://payok.io/cabinet/api.php>`_ 
- ``api_id`` - PayOk `API ID <https://payok.io/cabinet/api.php>`_
- ``shop_id`` - PayOk `Shop ID <https://payok.io/cabinet/main.php>`_
- ``shop_secret_key`` - PayOk `Shop secret key <https://payok.io/cabinet/main.php>`_

.. warning:: 

    **Balance** and **Transactions** permissions are required for ``api_key``

Settings arguments:

- ``payment_type`` - `PayOkPaymentType`_ enum.
- ``currency`` - `PayOkCurrency`_ enum.
- ``success_url`` - User will be redirected to this url after paying.

.. note ::

    You can set default setting for every payment of ``PayOkPayment`` and override them for specific payment.

.. code-block:: python
    
    from pypayment import PayOkPayment, PayOkPaymentType, PayOkCurrency
    from datetime import timedelta

    # Set default setting
    PayOkPayment.authorize("my_api_key", "my_api_id", "my_shop_id", "my_shop_secret_key",
                           payment_type=PayOkPaymentType.CARD,
                           currency=PayOkCurrency.RUB,
                           success_url="my_success_url.com")

    # Override setting for specific payment
    payment = PayOkPayment(amount=100,
                           description="My payment",
                           payment_type=PayOkPaymentType.BITCOIN,
                           currency=PayOkCurrency.USD,
                           success_url="override_success_url.com")

PayOkPaymentType
****************

Enum for ``payment_type`` setting argument:

- ``CARD`` - Payment with bank card.
- ``YOOMONEY`` - Payment with YooMoney.
- ``QIWI`` - Payment with QIWI.
- ``WEBMONEY`` - Payment with WebMoney.
- ``PAYEER`` - Payment with Payeer.
- ``PERFECT_MONEY`` - Payment with Perfect Money.
- ``ADVCASH`` - Payment with Advcash.
- ``BEELINE`` - Payment with Beeline.
- ``MEGAFON`` - Payment with Megafon.
- ``TELE2`` - Payment with Tele2.
- ``MTS`` - Payment with MTS.
- ``QIWI_MOBILE`` - Payment with QIWI Mobile.
- ``BITCOIN`` - Payment with Bitcoin.
- ``LITECOIN`` - Payment with Litecoin.
- ``DOGECOIN`` - Payment with Dogecoin.
- ``DASH`` - Payment with Dash.
- ``ZCASH`` - Payment with Zcash.

PayOkCurrency
*************

Enum for ``currency`` setting argument:

- ``RUB`` - Russian ruble.
- ``UAH`` - Ukrainian hryvnia.
- ``USD`` - United States dollar.
- ``EUR`` - Euro.
- ``RUB2`` - Russian ruble. *(Alternative Gateway)*