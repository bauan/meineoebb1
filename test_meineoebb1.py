"""Tests for meineoebb1 journey tracker."""

import pytest
from datetime import date

from meineoebb1 import Journey, JourneyTracker


# ---------------------------------------------------------------------------
# Journey tests
# ---------------------------------------------------------------------------

class TestJourney:
    def test_create_basic(self):
        j = Journey(date(2026, 3, 19), "Wien Hbf", "Salzburg Hbf", "RJ 517")
        assert j.origin == "Wien Hbf"
        assert j.destination == "Salzburg Hbf"
        assert j.train == "RJ 517"
        assert j.journey_date == date(2026, 3, 19)
        assert j.price is None

    def test_create_with_price(self):
        j = Journey(date(2026, 3, 20), "Graz Hbf", "Wien Hbf", "RJ 64", price=29.90)
        assert j.price == pytest.approx(29.90)

    def test_whitespace_stripped(self):
        j = Journey(date(2026, 3, 19), "  Wien Hbf  ", "  Salzburg Hbf  ", "  RJ 517  ")
        assert j.origin == "Wien Hbf"
        assert j.destination == "Salzburg Hbf"
        assert j.train == "RJ 517"

    def test_empty_origin_raises(self):
        with pytest.raises(ValueError, match="Origin"):
            Journey(date(2026, 3, 19), "", "Salzburg Hbf", "RJ 517")

    def test_empty_destination_raises(self):
        with pytest.raises(ValueError, match="Destination"):
            Journey(date(2026, 3, 19), "Wien Hbf", "  ", "RJ 517")

    def test_empty_train_raises(self):
        with pytest.raises(ValueError, match="Train"):
            Journey(date(2026, 3, 19), "Wien Hbf", "Salzburg Hbf", "")

    def test_negative_price_raises(self):
        with pytest.raises(ValueError, match="Price"):
            Journey(date(2026, 3, 19), "Wien Hbf", "Salzburg Hbf", "RJ 517", price=-1.0)

    def test_zero_price_allowed(self):
        j = Journey(date(2026, 3, 19), "Wien Hbf", "Salzburg Hbf", "RJ 517", price=0.0)
        assert j.price == 0.0

    def test_equality(self):
        j1 = Journey(date(2026, 3, 19), "Wien Hbf", "Salzburg Hbf", "RJ 517", price=19.90)
        j2 = Journey(date(2026, 3, 19), "Wien Hbf", "Salzburg Hbf", "RJ 517", price=19.90)
        assert j1 == j2

    def test_repr_with_price(self):
        j = Journey(date(2026, 3, 19), "Wien Hbf", "Salzburg Hbf", "RJ 517", price=19.90)
        assert "Wien Hbf" in repr(j)
        assert "Salzburg Hbf" in repr(j)
        assert "19.90" in repr(j)

    def test_repr_without_price(self):
        j = Journey(date(2026, 3, 19), "Wien Hbf", "Salzburg Hbf", "RJ 517")
        assert "N/A" in repr(j)


# ---------------------------------------------------------------------------
# JourneyTracker tests
# ---------------------------------------------------------------------------

class TestJourneyTracker:
    def _make_tracker(self) -> JourneyTracker:
        tracker = JourneyTracker()
        tracker.add(Journey(date(2026, 3, 10), "Wien Hbf", "Salzburg Hbf", "RJ 517", price=19.90))
        tracker.add(Journey(date(2026, 3, 5), "Graz Hbf", "Wien Hbf", "RJ 64", price=29.90))
        tracker.add(Journey(date(2026, 3, 20), "Wien Hbf", "Innsbruck Hbf", "RJ 163", price=39.90))
        return tracker

    def test_all_sorted_by_date(self):
        tracker = self._make_tracker()
        journeys = tracker.all()
        dates = [j.journey_date for j in journeys]
        assert dates == sorted(dates)

    def test_all_returns_all(self):
        tracker = self._make_tracker()
        assert len(tracker.all()) == 3

    def test_search_by_origin(self):
        tracker = self._make_tracker()
        results = tracker.search(origin="Wien Hbf")
        assert len(results) == 2
        assert all(j.origin == "Wien Hbf" for j in results)

    def test_search_by_destination(self):
        tracker = self._make_tracker()
        results = tracker.search(destination="Wien Hbf")
        assert len(results) == 1
        assert results[0].origin == "Graz Hbf"

    def test_search_by_origin_and_destination(self):
        tracker = self._make_tracker()
        results = tracker.search(origin="Wien Hbf", destination="Salzburg Hbf")
        assert len(results) == 1
        assert results[0].train == "RJ 517"

    def test_search_case_insensitive(self):
        tracker = self._make_tracker()
        results = tracker.search(origin="wien hbf")
        assert len(results) == 2

    def test_search_no_match(self):
        tracker = self._make_tracker()
        results = tracker.search(origin="Linz Hbf")
        assert results == []

    def test_total_spent(self):
        tracker = self._make_tracker()
        assert tracker.total_spent() == pytest.approx(19.90 + 29.90 + 39.90)

    def test_total_spent_ignores_no_price(self):
        tracker = JourneyTracker()
        tracker.add(Journey(date(2026, 3, 1), "Wien Hbf", "Salzburg Hbf", "RJ 1", price=10.0))
        tracker.add(Journey(date(2026, 3, 2), "Wien Hbf", "Graz Hbf", "RJ 2"))
        assert tracker.total_spent() == pytest.approx(10.0)

    def test_empty_tracker(self):
        tracker = JourneyTracker()
        assert tracker.all() == []
        assert tracker.total_spent() == 0.0
        assert tracker.search(origin="Wien Hbf") == []
