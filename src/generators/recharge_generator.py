"""Generate recharge transactions for prepaid telecom customers."""

from __future__ import annotations

import logging
import random
from datetime import date, timedelta
from pathlib import Path

from .common import read_csv, write_csv

logger = logging.getLogger(__name__)

REFERENCE_DATE = date(2026, 1, 1)

RECHARGE_FIELDS = [
    "recharge_id",
    "customer_id",
    "recharge_date",
    "amount",
    "payment_method",
    "recharge_status",
    "load_date",
]


def generate_recharges(
    customers_path: str | Path,
    output_path: str | Path,
    records_per_customer: int = 2,
    seed: int = 42,
) -> Path:
    """
    Generate prepaid recharge transactions.

    Business Rules:
    - Only ACTIVE PREPAID customers can recharge.
    - Each customer performs a configurable number of recharges.
    - Payment methods follow realistic telecom usage patterns.
    - Recharge amounts reflect common telecom plans.
    """

    if records_per_customer <= 0:
        raise ValueError(
            "records_per_customer must be greater than zero"
        )

    rng = random.Random(seed)

    customers = [
        row
        for row in read_csv(customers_path)
        if row["account_type"] == "PREPAID"
        and row["status"] == "ACTIVE"
    ]

    if not customers:
        raise ValueError(
            "No active prepaid customers found."
        )

    rows = []

    recharge_sequence = 1

    start_date = REFERENCE_DATE - timedelta(days=90)

    for customer in customers:

        for _ in range(records_per_customer):

            recharge_date = (
                start_date
                + timedelta(days=rng.randrange(91))
            )

            rows.append(
                {
                    "recharge_id": f"RCH{recharge_sequence:010d}",
                    "customer_id": customer["customer_id"],
                    "recharge_date": recharge_date.isoformat(),
                    "amount": rng.choices(
                        [149, 199, 239, 299, 399, 599, 799, 2399],
                        weights=[6, 18, 8, 28, 22, 10, 5, 3],
                        k=1,
                    )[0],
                    "payment_method": rng.choices(
                        [
                            "UPI",
                            "CREDIT_CARD",
                            "DEBIT_CARD",
                            "NET_BANKING",
                            "WALLET",
                        ],
                        weights=[55, 15, 10, 10, 10],
                        k=1,
                    )[0],
                    "recharge_status": rng.choices(
                        [
                            "SUCCESS",
                            "FAILED",
                            "PENDING",
                        ],
                        weights=[95, 3, 2],
                        k=1,
                    )[0],
                    "load_date": REFERENCE_DATE.isoformat(),
                }
            )

            recharge_sequence += 1

    output_file = write_csv(
        output_path,
        RECHARGE_FIELDS,
        rows,
    )

    logger.info(
        "Generated %s recharge transactions for %s prepaid customers.",
        len(rows),
        len(customers),
    )

    return output_file