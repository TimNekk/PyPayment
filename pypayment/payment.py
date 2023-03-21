from abc import ABC, abstractmethod
from typing import Optional
from uuid import uuid4

from pypayment import PaymentStatus


class Payment(ABC):
    """Payment interface than allows to create and check invoices."""

    def __init__(self, amount: float, description: str = "", id: Optional[str] = None):
        self.amount = amount
        """The amount to be invoiced."""
        self.description = description
        """Payment comment."""
        self.id = id if id is not None else str(uuid4())
        """Unique Payment ID (default: generated with uuid4)."""

    @property
    @abstractmethod
    def url(self) -> str:
        """:return: Link to the created payment form."""

    @property
    @abstractmethod
    def status(self) -> PaymentStatus:
        """
        Requests the payment status from the payment provider.

        :return: Payment status.
        """

    @property
    @abstractmethod
    def income(self) -> Optional[float]:
        """
        Requests the payment income (profit) from the payment provider.

        :return: Income from the payment.
        """
