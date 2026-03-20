# meineoebb1

A simple Python library and command-line tool for tracking your ÖBB (Austrian Federal Railways) train journeys.

## Features

- Record journeys with date, origin, destination, train number, and optional ticket price
- List all journeys sorted by date
- Search journeys by origin and/or destination (case-insensitive)
- Remove journeys
- Calculate total spending and journey count
- **Persist data** to a JSON file so nothing is lost between sessions
- **Command-line interface** — use directly from the terminal

## Command-line usage

```bash
# Add a journey (price optional)
python cli.py add 2026-03-19 "Wien Hbf" "Salzburg Hbf" "RJ 517" --price 19.90
python cli.py add 2026-03-20 "Wien Hbf" "Innsbruck Hbf" "RJ 163"

# List all journeys (sorted by date)
python cli.py list

# Search by origin and/or destination
python cli.py search --origin "Wien Hbf"
python cli.py search --destination "Wien Hbf"

# Show statistics (count + total spending)
python cli.py stats

# Remove a journey by index (as shown in 'list')
python cli.py remove 0
```

By default journeys are stored in `~/.meineoebb1.json`. Use `--file PATH` to specify a different file.

## Library usage

```python
from datetime import date
from meineoebb1 import Journey, JourneyTracker

tracker = JourneyTracker()
tracker.add(Journey(date(2026, 3, 10), "Wien Hbf", "Salzburg Hbf", "RJ 517", price=19.90))
tracker.add(Journey(date(2026, 3, 20), "Wien Hbf", "Innsbruck Hbf", "RJ 163", price=39.90))

# Save to disk
tracker.save("journeys.json")

# Load from disk
tracker.load("journeys.json")

# List all journeys
for j in tracker.all():
    print(j)

# Search by origin
results = tracker.search(origin="Wien Hbf")

# Remove by index (index refers to the sorted list)
tracker.remove(0)

# Statistics
print(f"Reisen: {tracker.count()}")
print(f"Ausgaben: €{tracker.total_spent():.2f}")
```

## Running tests

```bash
python -m pytest test_meineoebb1.py -v
```

