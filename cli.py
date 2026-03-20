"""
Command-line interface for meineoebb1.

Usage:
    python -m meineoebb1 <command> [options]

Commands:
    add     Add a new journey
    list    List all journeys
    search  Search journeys by origin and/or destination
    stats   Show statistics (journey count and total spending)
    remove  Remove a journey by its list index
"""

import argparse
import os
import sys
from datetime import date

from meineoebb1 import Journey, JourneyTracker

DEFAULT_DATA_FILE = os.path.join(os.path.expanduser("~"), ".meineoebb1.json")


def _load(filepath: str) -> JourneyTracker:
    tracker = JourneyTracker()
    tracker.load(filepath)
    return tracker


def cmd_add(args: argparse.Namespace) -> None:
    try:
        journey_date = date.fromisoformat(args.date)
    except ValueError:
        print(f"Ungültiges Datum '{args.date}'. Bitte im Format YYYY-MM-DD angeben.", file=sys.stderr)
        sys.exit(1)

    price = None
    if args.price is not None:
        if args.price < 0:
            print("Preis darf nicht negativ sein.", file=sys.stderr)
            sys.exit(1)
        price = args.price

    try:
        journey = Journey(journey_date, args.origin, args.destination, args.train, price=price)
    except ValueError as exc:
        print(f"Fehler: {exc}", file=sys.stderr)
        sys.exit(1)

    tracker = _load(args.file)
    tracker.add(journey)
    tracker.save(args.file)
    print(f"Reise hinzugefügt: {journey}")


def cmd_list(args: argparse.Namespace) -> None:
    tracker = _load(args.file)
    journeys = tracker.all()
    if not journeys:
        print("Keine Reisen gespeichert.")
        return
    for idx, j in enumerate(journeys):
        price_str = f"€{j.price:.2f}" if j.price is not None else "N/A"
        print(f"[{idx}] {j.journey_date}  {j.origin} → {j.destination}  {j.train}  {price_str}")


def cmd_search(args: argparse.Namespace) -> None:
    if not args.origin and not args.destination:
        print("Bitte mindestens --origin oder --destination angeben.", file=sys.stderr)
        sys.exit(1)

    tracker = _load(args.file)
    results = tracker.search(
        origin=args.origin if args.origin else None,
        destination=args.destination if args.destination else None,
    )
    if not results:
        print("Keine passenden Reisen gefunden.")
        return
    for idx, j in enumerate(results):
        price_str = f"€{j.price:.2f}" if j.price is not None else "N/A"
        print(f"[{idx}] {j.journey_date}  {j.origin} → {j.destination}  {j.train}  {price_str}")


def cmd_stats(args: argparse.Namespace) -> None:
    tracker = _load(args.file)
    print(f"Anzahl Reisen : {tracker.count()}")
    print(f"Gesamtausgaben: €{tracker.total_spent():.2f}")


def cmd_remove(args: argparse.Namespace) -> None:
    tracker = _load(args.file)
    try:
        removed = tracker.remove(args.index)
    except IndexError as exc:
        print(f"Fehler: {exc}", file=sys.stderr)
        sys.exit(1)
    tracker.save(args.file)
    print(f"Reise entfernt: {removed}")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="meineoebb1",
        description="Persönlicher ÖBB-Reisentracker",
    )
    parser.add_argument(
        "--file",
        default=DEFAULT_DATA_FILE,
        metavar="DATEI",
        help=f"Datei zum Speichern der Reisen (Standard: {DEFAULT_DATA_FILE})",
    )

    subparsers = parser.add_subparsers(dest="command", required=True)

    # add
    p_add = subparsers.add_parser("add", help="Reise hinzufügen")
    p_add.add_argument("date", metavar="DATUM", help="Reisedatum (YYYY-MM-DD)")
    p_add.add_argument("origin", metavar="VON", help="Abfahrtsbahnhof")
    p_add.add_argument("destination", metavar="NACH", help="Zielbahnhof")
    p_add.add_argument("train", metavar="ZUG", help="Zugbezeichnung (z.B. RJ 517)")
    p_add.add_argument("--price", type=float, default=None, metavar="PREIS", help="Ticketpreis in Euro")
    p_add.set_defaults(func=cmd_add)

    # list
    p_list = subparsers.add_parser("list", help="Alle Reisen auflisten")
    p_list.set_defaults(func=cmd_list)

    # search
    p_search = subparsers.add_parser("search", help="Reisen suchen")
    p_search.add_argument("--origin", metavar="VON", help="Abfahrtsbahnhof filtern")
    p_search.add_argument("--destination", metavar="NACH", help="Zielbahnhof filtern")
    p_search.set_defaults(func=cmd_search)

    # stats
    p_stats = subparsers.add_parser("stats", help="Statistiken anzeigen")
    p_stats.set_defaults(func=cmd_stats)

    # remove
    p_remove = subparsers.add_parser("remove", help="Reise entfernen")
    p_remove.add_argument("index", type=int, metavar="INDEX", help="Index der zu entfernenden Reise (aus 'list')")
    p_remove.set_defaults(func=cmd_remove)

    return parser


def main(argv: list[str] | None = None) -> None:
    parser = build_parser()
    args = parser.parse_args(argv)
    args.func(args)


if __name__ == "__main__":
    main()
