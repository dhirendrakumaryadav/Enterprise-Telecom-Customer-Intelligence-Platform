"""Generate support tickets suitable for later AI and vector-search use cases."""

from __future__ import annotations

import random
from datetime import date, timedelta
from pathlib import Path

from .common import read_csv, write_csv


SUPPORT_FIELDS = ["ticket_id", "customer_id", "category", "priority", "description", "status", "created_date"]

ISSUES = {
    "Network Issue": "Intermittent network coverage near {city}; calls are dropping repeatedly.",
    "Slow Internet": "Mobile data speed is very slow in {city}, especially during evening hours.",
    "Billing Issue": "Unexpected charge appears on my monthly bill and needs clarification.",
    "SIM Activation": "SIM activation is still pending after identity verification.",
    "Call Drop": "Frequent call drops while connected to the network in {city}.",
    "Recharge Failure": "Recharge payment was completed but the balance has not updated.",
    "5G Issue": "5G service is unavailable in {city} despite using a compatible device.",
    "Roaming Issue": "Unable to access mobile data while roaming outside the home circle.",
}


def generate_support_tickets(
    customers_path: str | Path,
    output_path: str | Path,
    num_records: int,
    seed: int = 42,
) -> Path:
    """Create reproducible customer complaint records across operational categories."""
    if num_records <= 0:
        raise ValueError("num_records must be greater than zero")
    rng = random.Random(seed)
    customers = read_csv(customers_path)
    if not customers:
        raise ValueError("customers_path does not contain any customer records")
    categories = list(ISSUES)
    rows = []
    start_date = date.today() - timedelta(days=180)
    for ticket_id in range(1, num_records + 1):
        customer = rng.choice(customers)
        category = rng.choices(categories, weights=[20, 18, 14, 8, 14, 10, 12, 4], k=1)[0]
        priority = rng.choices(["LOW", "MEDIUM", "HIGH", "CRITICAL"], weights=[15, 55, 25, 5], k=1)[0]
        rows.append(
            {
                "ticket_id": ticket_id,
                "customer_id": customer["customer_id"],
                "category": category,
                "priority": priority,
                "description": ISSUES[category].format(city=customer["city"]),
                "status": rng.choices(["OPEN", "IN_PROGRESS", "RESOLVED", "CLOSED"], weights=[12, 18, 45, 25], k=1)[0],
                "created_date": (start_date + timedelta(days=rng.randrange(181))).isoformat(),
            }
        )
    return write_csv(output_path, SUPPORT_FIELDS, rows)

