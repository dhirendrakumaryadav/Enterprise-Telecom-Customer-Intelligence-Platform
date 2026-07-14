"""Generate telecom network telemetry events."""

from __future__ import annotations

import logging
import random
from datetime import datetime, timedelta
from pathlib import Path

from .common import random_datetime, read_csv, write_csv

logger = logging.getLogger(__name__)

REFERENCE_DATETIME = datetime(2026, 1, 1, 0, 0, 0)

NETWORK_FIELDS = [
    "event_id",
    "tower_id",
    "customer_id",
    "signal_strength_dbm",
    "latency_ms",
    "packet_loss_pct",
    "network_status",
    "event_time",
    "load_date",
]


def generate_network_events(
    customers_path: str | Path,
    output_path: str | Path,
    num_records: int,
    seed: int = 42,
) -> Path:
    """
    Generate telecom network telemetry events.

    Business Rules:
    - 85% of events represent healthy network conditions.
    - 15% of events represent degraded service.
    - Events are linked to existing customers.
    - Metrics include signal strength, latency, and packet loss.
    """

    if num_records <= 0:
        raise ValueError(
            "num_records must be greater than zero"
        )

    rng = random.Random(seed)

    customers = read_csv(customers_path)

    if not customers:
        raise ValueError(
            "customers_path does not contain any customer records"
        )

    start = REFERENCE_DATETIME - timedelta(days=30)
    end = REFERENCE_DATETIME

    rows = []

    for event_number in range(1, num_records + 1):

        customer = rng.choice(customers)

        degraded = rng.random() < 0.15

        city_prefix = (
            customer["city"]
            .replace(" ", "")
            .upper()[:3]
        )

        rows.append(
            {
                "event_id": f"EVT{event_number:012d}",
                "tower_id": (
                    f"TWR-{city_prefix}-"
                    f"{rng.randint(1, 250):03d}"
                ),
                "customer_id": customer["customer_id"],
                "signal_strength_dbm": (
                    rng.randint(-118, -96)
                    if degraded
                    else rng.randint(-90, -65)
                ),
                "latency_ms": (
                    round(rng.uniform(120, 450), 2)
                    if degraded
                    else round(rng.uniform(20, 80), 2)
                ),
                "packet_loss_pct": (
                    round(rng.uniform(3, 15), 2)
                    if degraded
                    else round(rng.uniform(0, 1.5), 2)
                ),
                "network_status": (
                    "DEGRADED"
                    if degraded
                    else "HEALTHY"
                ),
                "event_time": random_datetime(
                    rng,
                    start,
                    end,
                ).isoformat(sep=" "),
                "load_date": REFERENCE_DATETIME.date().isoformat(),
            }
        )

    output_file = write_csv(
        output_path,
        NETWORK_FIELDS,
        rows,
    )

    logger.info(
        "Generated %s network events at %s",
        num_records,
        output_file,
    )

    return output_file