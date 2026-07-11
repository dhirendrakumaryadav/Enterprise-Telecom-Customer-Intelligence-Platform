"""Generate recharge transactions for prepaid customers."""

from __future__ import annotations

import random
from datetime import date, timedelta
from pathlib import Path

from .common import read_csv, write_csv


RECHARGE_FIELDS = ["recharge_id", "customer_id", "recharge_date", "amount", "payment_method"]


def generate_recharges(
    customers_path: str | Path,
    output_path: str | Path,
    records_per_customer: int = 2,
    seed: int = 42,
) -> Path:
    """Create recharge activity only for active prepaid customers."""
    if records_per_customer <= 0:
        raise ValueError("records_per_customer must be greater than zero")
    rng = random.Random(seed)
    customers = [
        row for row in read_csv(customers_path)
        if row["account_type"] == "PREPAID" and row["status"] == "ACTIVE"
    ]
    rows = []
    recharge_id = 1
    start_date = date.today() - timedelta(days=90)
    for customer in customers:
        for _ in range(records_per_customer):
            rows.append(
                {
                    "recharge_id": recharge_id,
                    "customer_id": customer["customer_id"],
                    "recharge_date": (start_date + timedelta(days=rng.randrange(91))).isoformat(),
                    "amount": rng.choices([149, 199, 239, 299, 399, 599, 2399], weights=[6, 18, 8, 28, 22, 12, 6], k=1)[0],
                    "payment_method": rng.choices(["UPI", "CARD", "NET_BANKING", "WALLET"], weights=[55, 25, 12, 8], k=1)[0],
                }
            )
            recharge_id += 1
    return write_csv(output_path, RECHARGE_FIELDS, rows)

