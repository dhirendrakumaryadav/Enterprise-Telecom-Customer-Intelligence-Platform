"""Generate support tickets suitable for AI and vector-search use cases."""

from __future__ import annotations

import logging
import random
from datetime import date, timedelta
from pathlib import Path

from .common import read_csv, write_csv

logger = logging.getLogger(__name__)

REFERENCE_DATE = date(2026, 1, 1)

SUPPORT_FIELDS = [
    "ticket_id",
    "customer_id",
    "category",
    "priority",
    "description",
    "status",
    "created_date",
    "resolved_date",
    "circle",
    "load_date",
]

ISSUES = {
    "Network Issue": (
        "Intermittent network coverage near {city}; calls are dropping repeatedly."
    ),
    "Slow Internet": (
        "Mobile data speed is very slow in {city}, especially during evening hours."
    ),
    "Billing Issue": (
        "Unexpected charge appears on my monthly bill and needs clarification."
    ),
    "SIM Activation": (
        "SIM activation is still pending after identity verification."
    ),
    "Call Drop": (
        "Frequent call drops while connected to the network in {city}."
    ),
    "Recharge Failure": (
        "Recharge payment was completed but the balance has not updated."
    ),
    "5G Issue": (
        "5G service is unavailable in {city} despite using a compatible device."
    ),
    "Roaming Issue": (
        "Unable to access mobile data while roaming outside the home circle."
    ),
}


def generate_support_tickets(
    customers_path: str | Path,
    output_path: str | Path,
    num_records: int,
    seed: int = 42,
) -> Path:
    """
    Generate realistic telecom support tickets.

    Business Rules:
    - Tickets are linked to existing customers.
    - Complaint categories follow common telecom issues.
    - Priority and status distributions mimic real support operations.
    - Resolved tickets receive a resolution timestamp.
    """

    if num_records <= 0:
        raise ValueError("num_records must be greater than zero")

    rng = random.Random(seed)

    customers = read_csv(customers_path)

    if not customers:
        raise ValueError(
            "customers_path does not contain any customer records"
        )

    categories = list(ISSUES.keys())

    start_date = REFERENCE_DATE - timedelta(days=180)

    rows = []

    for ticket_number in range(1, num_records + 1):

        customer = rng.choice(customers)

        category = rng.choices(
            categories,
            weights=[20, 18, 14, 8, 14, 10, 12, 4],
            k=1,
        )[0]

        priority = rng.choices(
            ["LOW", "MEDIUM", "HIGH", "CRITICAL"],
            weights=[15, 55, 25, 5],
            k=1,
        )[0]

        status = rng.choices(
            ["OPEN", "IN_PROGRESS", "RESOLVED", "CLOSED"],
            weights=[12, 18, 45, 25],
            k=1,
        )[0]

        created_date = (
            start_date
            + timedelta(days=rng.randrange(181))
        )

        resolved_date = None

        if status in ("RESOLVED", "CLOSED"):
            resolved_date = (
                created_date
                + timedelta(days=rng.randint(1, 10))
            ).isoformat()

        rows.append(
            {
                "ticket_id": f"TKT{ticket_number:010d}",
                "customer_id": customer["customer_id"],
                "category": category,
                "priority": priority,
                "description": ISSUES[category].format(
                    city=customer["city"]
                ),
                "status": status,
                "created_date": created_date.isoformat(),
                "resolved_date": resolved_date,
                "circle": customer.get(
                    "circle",
                    customer.get("state", "UNKNOWN"),
                ),
                "load_date": REFERENCE_DATE.isoformat(),
            }
        )

    output_file = write_csv(
        output_path,
        SUPPORT_FIELDS,
        rows,
    )

    logger.info(
        "Generated %s support tickets at %s",
        num_records,
        output_file,
    )

    return output_file