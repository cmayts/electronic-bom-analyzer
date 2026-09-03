"""Extension points for optional lifecycle and stock-data providers.

No provider is enabled by default. Implementations must use documented vendor
APIs, read credentials from environment variables, and avoid logging secrets or
transmitting complete customer BOMs without explicit authorization.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass


@dataclass(frozen=True)
class PartAvailability:
    manufacturer_part_number: str
    lifecycle_status: str | None = None
    stock_quantity: int | None = None
    source: str | None = None


class PartDataProvider(ABC):
    """Interface for a user-configured, official component-data service."""

    @abstractmethod
    def lookup(self, manufacturer_part_number: str) -> PartAvailability:
        """Return availability metadata for one manufacturer part number."""


class DisabledProvider(PartDataProvider):
    """Privacy-safe default that performs no network requests."""

    def lookup(self, manufacturer_part_number: str) -> PartAvailability:
        return PartAvailability(manufacturer_part_number=manufacturer_part_number)
