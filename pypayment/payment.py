from abc import ABC, abstractmethod
from typing import Optional, Tuple
from uuid import uuid4

from pypayment import NotAuthorized, PaymentStatus, PaymentNotFound


class Payment(ABC):
    """Payment interface than allows to create and check invoices."""

    authorized = False
    """Is payment class authorized."""

    def __init__(self, amount: float, description: str = "", id: Optional[str] = None) -> None:
        self._check_authorization()

        self.id: str = id if id is not None else str(uuid4())
        """Unique Payment ID (default: generated with uuid4)."""

        self.amount: float = amount
        """Amount to be invoiced. May not include commission."""

        self.description: str = description if description else str(self.id)
        """Payment comment."""

        self.status: PaymentStatus = PaymentStatus.WAITING
        """Payment status. Use update() to update it."""

        self.income: Optional[float] = None
        """Payment income. Use update() to update it."""

        self._validate_params()

        self.url: str = self._create_url()
        """Payment URL."""

    @classmethod
    @abstractmethod
    def get_status_and_income(cls, payment_id: str) -> Tuple[Optional[PaymentStatus], float]:
        """Returns payment status and income.

        :param payment_id: Payment ID.
        :raises PaymentNotFound: Payment not found.
        :return: Payment status and income.
        """

    def update(self) -> None:
        try:
            status, income = self.__class__.get_status_and_income(self.id)
        except PaymentNotFound:
            return

        if status:
            self.status = status
        self.income = income

    @abstractmethod
    def _create_url(self) -> str:
        """Creates payment URL."""

    def _check_authorization(self) -> None:
        """Raises NotAuthorized if class was not authorized."""
        if not self.authorized:
            raise NotAuthorized(f"You need to authorize first: {self.__class__.__name__}.authorize()")

    def _validate_params(self) -> None:
        """Validates payment parameters."""
        pass
