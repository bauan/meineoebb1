# meineoebb1

A simple Python library for tracking your ÖBB (Austrian Federal Railways) train journeys.

## Features

- Record journeys with date, origin, destination, train number, and optional ticket price
- List all journeys sorted by date
- Search journeys by origin and/or destination (case-insensitive)
- Calculate total spending across all recorded journeys

## Usage

```python
from datetime import date
from meineoebb1 import Journey, JourneyTracker

tracker = JourneyTracker()
tracker.add(Journey(date(2026, 3, 10), "Wien Hbf", "Salzburg Hbf", "RJ 517", price=19.90))
tracker.add(Journey(date(2026, 3, 20), "Wien Hbf", "Innsbruck Hbf", "RJ 163", price=39.90))

# List all journeys
for j in tracker.all():
    print(j)

# Search by origin
results = tracker.search(origin="Wien Hbf")

# Total spending
print(f"Total spent: €{tracker.total_spent():.2f}")
```

## Running tests

```bash
python -m pytest test_meineoebb1.py -v
```

