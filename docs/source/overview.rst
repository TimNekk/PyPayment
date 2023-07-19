********
Overview
********

Concept
=======

**PyPayment** is a Python wrapper for API of different payment providers. 
It is designed to be a simple and easy to use library for developers to integrate payment into their applications.

Main idea is to provide a unified interface for different payment providers.

Supported providers:

- :ref:`Qiwi`
- :ref:`YooMoney`
- :ref:`PayOk`
- **Lava** *(under development)*

Quickstart
==========

Install the latest version with `PyPi <https://pypi.org/project/pypayment/>`_.

.. code-block:: bash
    
    pip install -U pypayment

Choose payment provider and authorize. For example, for Qiwi.

.. code-block:: python

    from pypayment import QiwiPayment

    QiwiPayment.authorize("my_secret_key")

Create a payment and get it's ``url``.

.. code-block:: python

    from pypayment import Payment, QiwiPayment

    payment: Payment = QiwiPayment(amount=100) # E.x. commission is 10%

    print(payment.url)  # https://oplata.qiwi.com/form/?invoice_uid=payment_unique_id

Wait for payment to be completed and get it's income.

Use ``update()`` method to update payment's ``status`` and ``income``.

.. code-block:: python

    from pypayment import PaymentStatus

    while payment.status != PaymentStatus.PAID:
        input("Press Enter to update payment status and income")
        payment.update()

    print("Payment is completed!")
    print(payment.income)  # 90.0

Summary.

.. code-block:: python

    from pypayment import Payment, QiwiPayment, PaymentStatus

    QiwiPayment.authorize("my_secret_key")

    payment: Payment = QiwiPayment(amount=100) # E.x. commission is 10%
    print(payment.url)  # https://oplata.qiwi.com/form/?invoice_uid=payment_unique_id

    while payment.status != PaymentStatus.PAID:
        input("Press Enter to update payment status")
        payment.update()

    print("Payment is completed!")
    print(payment.income)  # 90.0


Additionally you can get payment's ``status`` and ``income`` using static method ``get_status_and_income()``.
(You need to know provider's class)

.. code-block:: python

    from pypayment import Payment, QiwiPayment, PaymentNotFound

    QiwiPayment.authorize("my_secret_key")

    payment: Payment = QiwiPayment(amount=100)

    try:
        status, income = QiwiPayment.get_status_and_income(payment.uid)
    except PaymentNotFound as e:
        print(e)
        return

    if status:
        print(status)
    print(income)