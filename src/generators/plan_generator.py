"""Generate the stable telecom plan catalogue."""

from __future__ import annotations

from pathlib import Path

from .common import TELECOM_PLANS, write_csv


PLAN_FIELDS = [
    "plan_id",
    "plan_name",
    "account_type",
    "monthly_price",
    "data_limit_gb",
    "voice_minutes",
    "sms_limit",
    "validity_days",
]


def generate_plans(output_path: str | Path) -> Path:
    """Write the portfolio's eight-plan catalogue to CSV."""
    return write_csv(output_path, PLAN_FIELDS, TELECOM_PLANS)

