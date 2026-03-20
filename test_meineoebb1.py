"""Tests for meineoebb1 journey tracker."""

import json
import os
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

    def test_to_dict_roundtrip(self):
        j = Journey(date(2026, 3, 19), "Wien Hbf", "Salzburg Hbf", "RJ 517", price=19.90)
        assert Journey.from_dict(j.to_dict()) == j

    def test_to_dict_roundtrip_no_price(self):
        j = Journey(date(2026, 3, 19), "Wien Hbf", "Salzburg Hbf", "RJ 517")
        assert Journey.from_dict(j.to_dict()) == j

    def test_to_dict_keys(self):
        j = Journey(date(2026, 3, 19), "Wien Hbf", "Salzburg Hbf", "RJ 517", price=19.90)
        d = j.to_dict()
        assert d["journey_date"] == "2026-03-19"
        assert d["origin"] == "Wien Hbf"
        assert d["destination"] == "Salzburg Hbf"
        assert d["train"] == "RJ 517"
        assert d["price"] == pytest.approx(19.90)


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

    # --- remove ---

    def test_remove_by_index(self):
        tracker = self._make_tracker()
        # sorted: [Graz(3-5), Wien->Sbg(3-10), Wien->IBK(3-20)]
        removed = tracker.remove(0)
        assert removed.origin == "Graz Hbf"
        assert tracker.count() == 2

    def test_remove_last(self):
        tracker = self._make_tracker()
        removed = tracker.remove(2)
        assert removed.destination == "Innsbruck Hbf"
        assert tracker.count() == 2

    def test_remove_invalid_index_raises(self):
        tracker = self._make_tracker()
        with pytest.raises(IndexError):
            tracker.remove(99)

    def test_remove_negative_index_raises(self):
        tracker = self._make_tracker()
        with pytest.raises(IndexError):
            tracker.remove(-1)

    def test_remove_from_empty_raises(self):
        tracker = JourneyTracker()
        with pytest.raises(IndexError):
            tracker.remove(0)

    # --- count ---

    def test_count(self):
        tracker = self._make_tracker()
        assert tracker.count() == 3

    def test_count_empty(self):
        assert JourneyTracker().count() == 0

    # --- persistence ---

    def test_save_and_load(self, tmp_path):
        filepath = str(tmp_path / "journeys.json")
        tracker = self._make_tracker()
        tracker.save(filepath)

        tracker2 = JourneyTracker()
        tracker2.load(filepath)
        assert tracker2.all() == tracker.all()
        assert tracker2.count() == 3

    def test_save_creates_valid_json(self, tmp_path):
        filepath = str(tmp_path / "journeys.json")
        tracker = self._make_tracker()
        tracker.save(filepath)

        with open(filepath, encoding="utf-8") as fh:
            data = json.load(fh)
        assert len(data) == 3
        assert data[0]["journey_date"] is not None

    def test_load_missing_file_does_nothing(self, tmp_path):
        filepath = str(tmp_path / "does_not_exist.json")
        tracker = JourneyTracker()
        tracker.load(filepath)  # should not raise
        assert tracker.count() == 0

    def test_save_load_no_price(self, tmp_path):
        filepath = str(tmp_path / "journeys.json")
        tracker = JourneyTracker()
        tracker.add(Journey(date(2026, 3, 1), "Wien Hbf", "Linz Hbf", "REX 1508"))
        tracker.save(filepath)

        tracker2 = JourneyTracker()
        tracker2.load(filepath)
        assert tracker2.all()[0].price is None

    def test_load_replaces_existing(self, tmp_path):
        filepath = str(tmp_path / "journeys.json")
        tracker = self._make_tracker()
        tracker.save(filepath)

        tracker2 = JourneyTracker()
        tracker2.add(Journey(date(2026, 1, 1), "Linz Hbf", "Wien Hbf", "REX 1"))
        tracker2.load(filepath)  # should replace the one pre-added journey
        assert tracker2.count() == 3


# ---------------------------------------------------------------------------
# CLI tests
# ---------------------------------------------------------------------------

from cli import main as cli_main


class TestCLI:
    def _run(self, args: list[str], tmp_path) -> str:
        """Run CLI with a temp data file and capture stdout."""
        import io
        from contextlib import redirect_stdout
        filepath = str(tmp_path / "data.json")
        buf = io.StringIO()
        with redirect_stdout(buf):
            cli_main(["--file", filepath] + args)
        return buf.getvalue()

    def test_add_and_list(self, tmp_path):
        self._run(["add", "2026-03-19", "Wien Hbf", "Salzburg Hbf", "RJ 517", "--price", "19.90"], tmp_path)
        out = self._run(["list"], tmp_path)
        assert "Wien Hbf" in out
        assert "Salzburg Hbf" in out

    def test_add_no_price(self, tmp_path):
        out = self._run(["add", "2026-03-19", "Wien Hbf", "Linz Hbf", "REX 1508"], tmp_path)
        assert "Wien Hbf" in out

    def test_list_empty(self, tmp_path):
        out = self._run(["list"], tmp_path)
        assert "Keine" in out

    def test_stats(self, tmp_path):
        self._run(["add", "2026-03-19", "Wien Hbf", "Salzburg Hbf", "RJ 517", "--price", "19.90"], tmp_path)
        out = self._run(["stats"], tmp_path)
        assert "1" in out
        assert "19.90" in out

    def test_search(self, tmp_path):
        self._run(["add", "2026-03-19", "Wien Hbf", "Salzburg Hbf", "RJ 517"], tmp_path)
        self._run(["add", "2026-03-20", "Graz Hbf", "Wien Hbf", "RJ 64"], tmp_path)
        out = self._run(["search", "--origin", "Wien Hbf"], tmp_path)
        assert "Wien Hbf" in out
        assert "Graz Hbf" not in out

    def test_search_no_results(self, tmp_path):
        out = self._run(["search", "--origin", "Linz Hbf"], tmp_path)
        assert "Keine" in out

    def test_remove(self, tmp_path):
        self._run(["add", "2026-03-19", "Wien Hbf", "Salzburg Hbf", "RJ 517"], tmp_path)
        self._run(["add", "2026-03-20", "Graz Hbf", "Wien Hbf", "RJ 64"], tmp_path)
        self._run(["remove", "0"], tmp_path)
        out = self._run(["list"], tmp_path)
        assert "Graz Hbf" in out
        assert "Salzburg Hbf" not in out

    def test_remove_invalid_index_exits(self, tmp_path):
        with pytest.raises(SystemExit):
            self._run(["remove", "99"], tmp_path)

    def test_add_invalid_date_exits(self, tmp_path):
        with pytest.raises(SystemExit):
            self._run(["add", "not-a-date", "Wien Hbf", "Salzburg Hbf", "RJ 517"], tmp_path)

