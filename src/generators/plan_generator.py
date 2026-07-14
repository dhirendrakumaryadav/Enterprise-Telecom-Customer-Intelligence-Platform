"""Generate the telecom plan catalogue used across the platform."""

from __future__ import annotations

import logging
from pathlib import Path

from .common import TELECOM_PLANS, write_csv

logger = logging.getLogger(__name__)

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
    """
    Generate the telecom plan master dataset.

    This dataset acts as a reference/master table for
    customer subscriptions, billing, and downstream analytics.
    """

    output_file = write_csv(
        output_path,
        PLAN_FIELDS,
        TELECOM_PLANS,
    )

    logger.info(
        "Generated %s telecom plans at %s",
        len(TELECOM_PLANS),
        output_file,
    )

    return output_file