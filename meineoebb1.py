"""
meineoebb1 - A simple ÖBB journey tracker.

Allows users to add, list, and search their ÖBB train journeys.
"""

from datetime import date
from typing import Optional


class Journey:
    """Represents a single ÖBB train journey."""

    def __init__(
        self,
        journey_date: date,
        origin: str,
        destination: str,
        train: str,
        price: Optional[float] = None,
    ) -> None:
        if not origin.strip():
            raise ValueError("Origin must not be empty.")
        if not destination.strip():
            raise ValueError("Destination must not be empty.")
        if not train.strip():
            raise ValueError("Train identifier must not be empty.")
        if price is not None and price < 0:
            raise ValueError("Price must not be negative.")
        self.journey_date = journey_date
        self.origin = origin.strip()
        self.destination = destination.strip()
        self.train = train.strip()
        self.price = price

    def __repr__(self) -> str:
        price_str = f"€{self.price:.2f}" if self.price is not None else "N/A"
        return (
            f"Journey({self.journey_date}, {self.origin} -> {self.destination}, "
            f"{self.train}, {price_str})"
        )

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Journey):
            return NotImplemented
        return (
            self.journey_date == other.journey_date
            and self.origin == other.origin
            and self.destination == other.destination
            and self.train == other.train
            and self.price == other.price
        )


class JourneyTracker:
    """Tracks a collection of ÖBB journeys."""

    def __init__(self) -> None:
        self._journeys: list[Journey] = []

    def add(self, journey: Journey) -> None:
        """Add a journey to the tracker."""
        self._journeys.append(journey)

    def all(self) -> list[Journey]:
        """Return all journeys, sorted by date."""
        return sorted(self._journeys, key=lambda j: j.journey_date)

    def search(self, origin: Optional[str] = None, destination: Optional[str] = None) -> list[Journey]:
        """Return journeys matching the given origin and/or destination (case-insensitive)."""
        results = self._journeys
        if origin is not None:
            results = [j for j in results if j.origin.lower() == origin.strip().lower()]
        if destination is not None:
            results = [j for j in results if j.destination.lower() == destination.strip().lower()]
        return sorted(results, key=lambda j: j.journey_date)

    def total_spent(self) -> float:
        """Return the total amount spent on journeys with a known price."""
        return sum(j.price for j in self._journeys if j.price is not None)
