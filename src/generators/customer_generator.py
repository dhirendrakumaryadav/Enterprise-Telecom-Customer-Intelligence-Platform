"""Generate CRM customer records with realistic Indian telecom attributes."""

from __future__ import annotations

import random
from datetime import date, timedelta
from pathlib import Path

from faker import Faker

from .common import CITY_STATE, TELECOM_PLANS, write_csv


CUSTOMER_FIELDS = [
    "customer_id", "full_name", "email", "phone_number", "city", "state",
    "plan_id", "account_type", "join_date", "status",
]


def generate_customers(output_path: str | Path, num_records: int, seed: int = 42) -> Path:
    """Create customers with a 95/5 active-to-inactive distribution."""
    if num_records <= 0:
        raise ValueError("num_records must be greater than zero")

    rng = random.Random(seed)
    fake = Faker("en_IN")
    fake.seed_instance(seed)
    cities = list(CITY_STATE.items())
    start_date = date.today() - timedelta(days=365 * 5)
    rows = []

    for customer_id in range(1, num_records + 1):
        city, state = rng.choice(cities)
        plan = rng.choices(TELECOM_PLANS, weights=[18, 20, 12, 5, 18, 15, 8, 4], k=1)[0]
        join_date = start_date + timedelta(days=rng.randrange((date.today() - start_date).days + 1))
        rows.append(
            {
                "customer_id": customer_id,
                "full_name": fake.name(),
                "email": f"customer{customer_id}@example.telecom",
                "phone_number": f"+91{rng.randint(6000000000, 9999999999)}",
                "city": city,
                "state": state,
                "plan_id": plan["plan_id"],
                "account_type": plan["account_type"],
                "join_date": join_date.isoformat(),
                "status": "ACTIVE" if rng.random() < 0.95 else "INACTIVE",
            }
        )
    return write_csv(output_path, CUSTOMER_FIELDS, rows)

