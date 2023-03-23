from abc import ABC, abstractmethod
from typing import Optional
from uuid import uuid4

from pypayment import NotAuthorized
from pypayment.enums.status import PaymentStatus


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

        self.url: str = self._create_url()
        """Payment URL."""

    @abstractmethod
    def _create_url(self) -> str:
        """Creates payment URL."""

    @abstractmethod
    def update(self) -> None:
        """Updates payment status and income."""

    def _check_authorization(self) -> None:
        """Raises NotAuthorized if class was not authorized."""
        if not self.authorized:
            raise NotAuthorized(f"You need to authorize first: {self.__class__.__name__}.authorize()")
