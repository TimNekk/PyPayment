from __future__ import annotations

from enum import Enum


class ChargeCommission(Enum):
    """Charge commission enum."""

    FROM_CUSTOMER = 0
    """Charge commission from customer."""
    FROM_SELLER = 1
    """Charge commission from seller."""
