from __future__ import annotations

from abc import ABC, abstractmethod
from uuid import uuid4

from pypayment import NotAuthorized, PaymentNotFound, PaymentStatus


class Payment(ABC):
    """Payment interface than allows to create and check invoices."""

    authorized = False
    """Is payment class authorized."""

    def __init__(self, amount: float, description: str = "", id: str | None = None) -> None:
        """Initialize Payment class."""
        self._check_authorization()

        self.id: str = id or str(uuid4())
        """Unique Payment ID (default: generated with uuid4)."""

        self.amount: float = round(amount, 2)
        """Amount to be invoiced. May not include commission."""

        self.description: str = description if description else str(self.id)
        """Payment comment."""

        self.status: PaymentStatus = PaymentStatus.WAITING
        """Payment status. Use update() to update it."""

        self.income: float | None = None
        """Payment income. Use update() to update it."""

        self._validate_params()

        self.url: str = self._create_url()
        """Payment URL."""

    @classmethod
    @abstractmethod
    def get_status_and_income(cls, payment_id: str) -> tuple[PaymentStatus | None, float]:
        """Return payment status and income.

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
        """Create payment URL."""

    def _check_authorization(self) -> None:
        """Raise NotAuthorized if class was not authorized."""
        if not self.authorized:
            raise NotAuthorized(f"You need to authorize first: {self.__class__.__name__}.authorize()")

    def _validate_params(self) -> None:
        """Validate payment parameters."""
