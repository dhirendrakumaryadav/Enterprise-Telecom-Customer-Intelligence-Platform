"""Generate monthly billing records for telecom postpaid customers."""

from __future__ import annotations

import logging
import random
from datetime import date, timedelta
from pathlib import Path

from dateutil.relativedelta import relativedelta

from .common import month_start, read_csv, write_csv

logger = logging.getLogger(__name__)

REFERENCE_DATE = date(2026, 1, 1)

BILLING_FIELDS = [
    "bill_id",
    "customer_id",
    "plan_id",
    "billing_cycle",
    "bill_date",
    "amount",
    "due_date",
    "payment_status",
    "load_date",
]


def generate_billing(
    customers_path: str | Path,
    plans_path: str | Path,
    output_path: str | Path,
    months: int = 3,
    seed: int = 42,
) -> Path:
    """
    Generate telecom billing records for active postpaid customers.

    Business Rules:
    - Only ACTIVE POSTPAID customers receive bills.
    - One bill per customer per billing cycle.
    - Bill amount is based on subscribed plan price.
    - Optional overage charges may be applied.
    - Payment status follows realistic distribution.
    """

    if months <= 0:
        raise ValueError("months must be greater than zero")

    rng = random.Random(seed)

    plan_prices = {
        str(row["plan_id"]): float(row["monthly_price"])
        for row in read_csv(plans_path)
    }

    customers = [
        row
        for row in read_csv(customers_path)
        if row["account_type"] == "POSTPAID"
        and row["status"] == "ACTIVE"
    ]

    billing_anchor = month_start(
        REFERENCE_DATE.year,
        REFERENCE_DATE.month,
    )

    rows = []

    bill_sequence = 1

    for month_offset in range(months):

        billing_month = billing_anchor - relativedelta(
            months=month_offset
        )

        for customer in customers:

            plan_id = str(customer["plan_id"])

            base_price = plan_prices[plan_id]

            overage_charge = rng.choice(
                [
                    0.0,
                    0.0,
                    0.0,
                    round(rng.uniform(25, 250), 2),
                ]
            )

            total_amount = round(
                base_price + overage_charge,
                2,
            )

            rows.append(
                {
                    "bill_id": f"BILL{bill_sequence:010d}",
                    "customer_id": customer["customer_id"],
                    "plan_id": plan_id,
                    "billing_cycle": billing_month.strftime("%Y-%m"),
                    "bill_date": billing_month.isoformat(),
                    "amount": total_amount,
                    "due_date": (
                        billing_month + timedelta(days=15)
                    ).isoformat(),
                    "payment_status": rng.choices(
                        ["PAID", "PENDING", "OVERDUE"],
                        weights=[90, 7, 3],
                        k=1,
                    )[0],
                    "load_date": REFERENCE_DATE.isoformat(),
                }
            )

            bill_sequence += 1

    output_file = write_csv(
        output_path,
        BILLING_FIELDS,
        rows,
    )

    logger.info(
        "Generated %s billing records for %s customers across %s months.",
        len(rows),
        len(customers),
        months,
    )

    return output_file