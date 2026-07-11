"""Generate monthly billing records for postpaid customers."""

from __future__ import annotations

import random
from datetime import date, timedelta
from pathlib import Path

from .common import month_start, read_csv, write_csv


BILLING_FIELDS = ["bill_id", "customer_id", "bill_date", "amount", "due_date", "payment_status"]


def generate_billing(
    customers_path: str | Path,
    plans_path: str | Path,
    output_path: str | Path,
    months: int = 3,
    seed: int = 42,
) -> Path:
    """Create one bill per active postpaid customer for each requested month."""
    if months <= 0:
        raise ValueError("months must be greater than zero")
    rng = random.Random(seed)
    plan_prices = {row["plan_id"]: float(row["monthly_price"]) for row in read_csv(plans_path)}
    customers = [
        row for row in read_csv(customers_path)
        if row["account_type"] == "POSTPAID" and row["status"] == "ACTIVE"
    ]
    today = month_start(date.today().year, date.today().month)
    rows = []
    bill_id = 1
    for month_offset in range(months):
        billing_month = today - timedelta(days=30 * month_offset)
        for customer in customers:
            base_price = plan_prices[customer["plan_id"]]
            overage = rng.choice([0.0, 0.0, 0.0, round(rng.uniform(25, 250), 2)])
            rows.append(
                {
                    "bill_id": bill_id,
                    "customer_id": customer["customer_id"],
                    "bill_date": billing_month.isoformat(),
                    "amount": round(base_price + overage, 2),
                    "due_date": (billing_month + timedelta(days=15)).isoformat(),
                    "payment_status": rng.choices(["PAID", "PENDING", "OVERDUE"], weights=[90, 7, 3], k=1)[0],
                }
            )
            bill_id += 1
    return write_csv(output_path, BILLING_FIELDS, rows)
