"""Generate CRM customer records with realistic Indian telecom attributes."""

from __future__ import annotations

import logging
import random
from datetime import date, timedelta
from pathlib import Path
from typing import Iterator

from faker import Faker

from .common import CITY_STATE, TELECOM_PLANS, write_csv


logger = logging.getLogger(__name__)
REFERENCE_DATE = date(2026, 1, 1)

CUSTOMER_FIELDS = [
    "customer_id",
    "full_name",
    "email",
    "phone_number",
    "city",
    "state",
    "plan_id",
    "account_type",
    "join_date",
    "status",
]


def generate_customers(output_path: str | Path, num_records: int, seed: int = 42) -> Path:
    """Generate deterministic CRM customer master data for the telecom platform.

    The output is the parent dataset for billing, recharge, support, and network
    source systems. A seed and fixed reference date make repeated runs reproducible.
    """
    if num_records <= 0:
        raise ValueError("num_records must be greater than zero")

    rng = random.Random(seed)
    fake = Faker("en_IN")
    fake.seed_instance(seed)
    cities = list(CITY_STATE.items())
    start_date = REFERENCE_DATE - timedelta(days=365 * 5)

    def customer_rows() -> Iterator[dict[str, object]]:
        for customer_id in range(1, num_records + 1):
            city, state = rng.choice(cities)
            plan = rng.choices(TELECOM_PLANS, weights=[18, 20, 12, 5, 18, 15, 8, 4], k=1)[0]
            join_date = start_date + timedelta(days=rng.randrange((REFERENCE_DATE - start_date).days + 1))
            phone_prefix = rng.choice(("6", "7", "8", "9"))
            phone_suffix = "".join(str(rng.randrange(10)) for _ in range(9))
            yield {
                "customer_id": customer_id,
                "full_name": fake.name(),
                "email": fake.email(),
                "phone_number": f"+91{phone_prefix}{phone_suffix}",
                "city": city,
                "state": state,
                "plan_id": plan["plan_id"],
                "account_type": plan["account_type"],
                "join_date": join_date.isoformat(),
                "status": rng.choices(
                    ["ACTIVE", "SUSPENDED", "INACTIVE", "TERMINATED"],
                    weights=[93, 4, 2, 1],
                    k=1,
                )[0],
            }

    path = write_csv(output_path, CUSTOMER_FIELDS, customer_rows())
    logger.info("Generated %s CRM customer records at %s", num_records, path)
    return path
