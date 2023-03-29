*****
Other
*****

Enums
==================

.. _ChargeCommission:

ChargeCommission
****************

Enum for ``charge_commission`` setting argument:

- ``FROM_CUSTOMER`` - Charge commission from customer.
- ``FROM_SELLER`` - Charge commission from seller.


.. _PaymentStatus:

PaymentStatus
****************

Enum that represents the status of a payment:

- ``WAITING`` - Payment has been created, but has not yet been paid.
- ``PAID`` - Payment was successfully paid.
- ``REJECTED`` - Payment was rejected.
- ``EXPIRED`` - Payment has expired.