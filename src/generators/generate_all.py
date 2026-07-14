"""Command-line entry point for producing relational telecom source datasets."""

from __future__ import annotations

import argparse
import logging
from pathlib import Path

from .billing_generator import generate_billing
from .customer_generator import generate_customers
from .network_generator import generate_network_events
from .plan_generator import generate_plans
from .recharge_generator import generate_recharges
from .support_generator import generate_support_tickets

logger = logging.getLogger(__name__)

SCALES = {
    "demo": {
        "customers": 2_000,
        "billing_months": 3,
        "recharges": 2,
        "support": 5_000,
        "network": 25_000,
    },
    "portfolio": {
        "customers": 100_000,
        "billing_months": 12,
        "recharges": 8,
        "support": 200_000,
        "network": 500_000,
    },
    "enterprise": {
        "customers": 500_000,
        "billing_months": 24,
        "recharges": 12,
        "support": 500_000,
        "network": 5_000_000,
    },
}


def generate_all(
    output_root: str | Path,
    scale: str = "demo",
    seed: int = 42,
) -> None:
    """
    Generate all telecom source datasets while preserving
    referential integrity across entities.

    Flow:

    Plans
      ↓
    Customers
      ↓
    Billing

    Customers
      ↓
    Recharge

    Customers
      ↓
    Support

    Customers
      ↓
    Network
    """

    if scale not in SCALES:
        raise ValueError(
            f"scale must be one of: {', '.join(SCALES.keys())}"
        )

    settings = SCALES[scale]

    logger.info(
        "Generating telecom datasets using scale=%s seed=%s",
        scale,
        seed,
    )

    root = Path(output_root)

    plans_file = root / "plans" / "plans.csv"

    customers_file = (
        root
        / "customers"
        / "customers.csv"
    )

    billing_file = (
        root
        / "billing"
        / "billing.csv"
    )

    recharge_file = (
        root
        / "recharge"
        / "recharge.csv"
    )

    support_file = (
        root
        / "support"
        / "support_tickets.csv"
    )

    network_file = (
        root
        / "network"
        / "network_events.csv"
    )

    logger.info("Generating plans dataset")
    generate_plans(plans_file)

    logger.info(
        "Generating %s customers",
        settings["customers"],
    )
    generate_customers(
        customers_file,
        settings["customers"],
        seed,
    )

    logger.info("Generating billing records")
    generate_billing(
        customers_path=customers_file,
        plans_path=plans_file,
        output_path=billing_file,
        months=settings["billing_months"],
        seed=seed + 1,
    )

    logger.info("Generating recharge records")
    generate_recharges(
        customers_path=customers_file,
        output_path=recharge_file,
        records_per_customer=settings["recharges"],
        seed=seed + 2,
    )

    logger.info("Generating support tickets")
    generate_support_tickets(
        customers_path=customers_file,
        output_path=support_file,
        num_records=settings["support"],
        seed=seed + 3,
    )

    logger.info("Generating network events")
    generate_network_events(
        customers_path=customers_file,
        output_path=network_file,
        num_records=settings["network"],
        seed=seed + 4,
    )

    logger.info(
        "Dataset generation completed successfully."
    )


def main() -> None:

    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s | "
            "%(levelname)s | "
            "%(message)s"
        ),
    )

    parser = argparse.ArgumentParser(
        description=(
            "Generate synthetic telecom source datasets."
        )
    )

    parser.add_argument(
        "--output-root",
        default="datasets/raw",
        help=(
            "Directory where datasets will be generated."
        ),
    )

    parser.add_argument(
        "--scale",
        choices=tuple(SCALES.keys()),
        default="demo",
        help=(
            "demo = quick generation, "
            "portfolio = interview-sized dataset, "
            "enterprise = very large dataset"
        ),
    )

    parser.add_argument(
        "--seed",
        type=int,
        default=42,
        help="Random seed for reproducible output.",
    )

    args = parser.parse_args()

    generate_all(
        output_root=args.output_root,
        scale=args.scale,
        seed=args.seed,
    )


if __name__ == "__main__":
    main()