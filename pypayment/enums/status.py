from __future__ import annotations

from enum import Enum


class PaymentStatus(Enum):
    """Payment status enum."""

    WAITING = 0
    """Payment has been created, but has not yet been paid."""
    PAID = 1
    """Payment was successfully paid."""
    REJECTED = 2
    """Payment was rejected."""
    EXPIRED = 3
    """Payment has expired."""
