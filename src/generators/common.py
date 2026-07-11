"""Shared data definitions and CSV helpers for telecom source generators."""

from __future__ import annotations

import csv
import random
from datetime import date, datetime
from pathlib import Path
from typing import Iterable, Mapping


TELECOM_PLANS = (
    {
        "plan_id": 101,
        "plan_name": "Prepaid Starter 199",
        "account_type": "PREPAID",
        "monthly_price": 199.0,
        "data_limit_gb": 2,
        "voice_minutes": 300,
        "sms_limit": 100,
        "validity_days": 28,
    },
    {
        "plan_id": 102,
        "plan_name": "Prepaid Unlimited 299",
        "account_type": "PREPAID",
        "monthly_price": 299.0,
        "data_limit_gb": 28,
        "voice_minutes": 1000,
        "sms_limit": 100,
        "validity_days": 28,
    },
    {
        "plan_id": 103,
        "plan_name": "Prepaid 5G 399",
        "account_type": "PREPAID",
        "monthly_price": 399.0,
        "data_limit_gb": 42,
        "voice_minutes": 1500,
        "sms_limit": 100,
        "validity_days": 28,
    },
    {
        "plan_id": 104,
        "plan_name": "Prepaid Annual 2399",
        "account_type": "PREPAID",
        "monthly_price": 199.92,
        "data_limit_gb": 365,
        "voice_minutes": 12000,
        "sms_limit": 36500,
        "validity_days": 365,
    },
    {
        "plan_id": 201,
        "plan_name": "Postpaid Plus 399",
        "account_type": "POSTPAID",
        "monthly_price": 399.0,
        "data_limit_gb": 40,
        "voice_minutes": -1,
        "sms_limit": 100,
        "validity_days": 30,
    },
    {
        "plan_id": 202,
        "plan_name": "Postpaid Unlimited 599",
        "account_type": "POSTPAID",
        "monthly_price": 599.0,
        "data_limit_gb": 75,
        "voice_minutes": -1,
        "sms_limit": 100,
        "validity_days": 30,
    },
    {
        "plan_id": 203,
        "plan_name": "Postpaid Family 999",
        "account_type": "POSTPAID",
        "monthly_price": 999.0,
        "data_limit_gb": 150,
        "voice_minutes": -1,
        "sms_limit": 200,
        "validity_days": 30,
    },
    {
        "plan_id": 204,
        "plan_name": "Postpaid Premium 1499",
        "account_type": "POSTPAID",
        "monthly_price": 1499.0,
        "data_limit_gb": 250,
        "voice_minutes": -1,
        "sms_limit": 500,
        "validity_days": 30,
    },
)

CITY_STATE = {
    "Bengaluru": "Karnataka",
    "Chennai": "Tamil Nadu",
    "Delhi": "Delhi",
    "Hyderabad": "Telangana",
    "Kolkata": "West Bengal",
    "Mumbai": "Maharashtra",
    "Pune": "Maharashtra",
    "Jaipur": "Rajasthan",
    "Ahmedabad": "Gujarat",
    "Lucknow": "Uttar Pradesh",
}


def write_csv(output_path: str | Path, fieldnames: list[str], rows: Iterable[Mapping[str, object]]) -> Path:
    """Write dictionaries to a UTF-8 CSV file and return its resolved path."""
    path = Path(output_path)
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(file, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    return path


def read_csv(input_path: str | Path) -> list[dict[str, str]]:
    with Path(input_path).open(newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def month_start(year: int, month: int) -> date:
    return date(year, month, 1)


def random_datetime(rng: random.Random, start: datetime, end: datetime) -> datetime:
    """Return a reproducible timestamp between two timestamps."""
    return start + (end - start) * rng.random()

