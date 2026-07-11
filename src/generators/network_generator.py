"""Generate network telemetry events with normal and degraded service patterns."""

from __future__ import annotations

import random
from datetime import datetime, timedelta
from pathlib import Path

from .common import random_datetime, read_csv, write_csv


NETWORK_FIELDS = ["event_id", "tower_id", "customer_id", "signal_strength_dbm", "latency_ms", "packet_loss_pct", "event_time"]


def generate_network_events(
    customers_path: str | Path,
    output_path: str | Path,
    num_records: int,
    seed: int = 42,
) -> Path:
    """Create network telemetry records; 15% intentionally represent degraded service."""
    if num_records <= 0:
        raise ValueError("num_records must be greater than zero")
    rng = random.Random(seed)
    customers = read_csv(customers_path)
    if not customers:
        raise ValueError("customers_path does not contain any customer records")
    rows = []
    end = datetime.now().replace(microsecond=0)
    start = end - timedelta(days=30)
    for event_id in range(1, num_records + 1):
        customer = rng.choice(customers)
        degraded = rng.random() < 0.15
        rows.append(
            {
                "event_id": event_id,
                "tower_id": f"TWR-{customer['city'][:3].upper()}-{rng.randint(1, 250):03d}",
                "customer_id": customer["customer_id"],
                "signal_strength_dbm": rng.randint(-118, -96) if degraded else rng.randint(-90, -65),
                "latency_ms": round(rng.uniform(120, 450), 2) if degraded else round(rng.uniform(20, 80), 2),
                "packet_loss_pct": round(rng.uniform(3, 15), 2) if degraded else round(rng.uniform(0, 1.5), 2),
                "event_time": random_datetime(rng, start, end).isoformat(sep=" "),
            }
        )
    return write_csv(output_path, NETWORK_FIELDS, rows)

