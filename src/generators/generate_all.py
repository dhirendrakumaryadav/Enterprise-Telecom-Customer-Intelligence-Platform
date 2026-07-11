"""Command-line entry point for producing a relational telecom source-data set."""

from __future__ import annotations

import argparse
from pathlib import Path

from .billing_generator import generate_billing
from .customer_generator import generate_customers
from .network_generator import generate_network_events
from .plan_generator import generate_plans
from .recharge_generator import generate_recharges
from .support_generator import generate_support_tickets


SCALES = {
    "demo": {"customers": 2_000, "billing_months": 3, "recharges": 2, "support": 5_000, "network": 25_000},
    "portfolio": {"customers": 100_000, "billing_months": 12, "recharges": 8, "support": 200_000, "network": 3_000_000},
}


def generate_all(output_root: str | Path, scale: str = "demo", seed: int = 42) -> None:
    """Generate all source-system CSVs while preserving customer-plan relationships."""
    if scale not in SCALES:
        raise ValueError(f"scale must be one of: {', '.join(SCALES)}")
    settings = SCALES[scale]
    root = Path(output_root)
    customers = root / "customers" / "customers.csv"
    plans = root / "plans" / "plans.csv"

    generate_plans(plans)
    generate_customers(customers, settings["customers"], seed)
    generate_billing(customers, plans, root / "billing" / "billing.csv", settings["billing_months"], seed + 1)
    generate_recharges(customers, root / "recharge" / "recharge.csv", settings["recharges"], seed + 2)
    generate_support_tickets(customers, root / "support" / "support_tickets.csv", settings["support"], seed + 3)
    generate_network_events(customers, root / "network" / "network_events.csv", settings["network"], seed + 4)


def main() -> None:
    parser = argparse.ArgumentParser(description="Generate synthetic telecom source datasets.")
    parser.add_argument("--output-root", default="datasets/raw", help="Directory in which entity folders are created.")
    parser.add_argument("--scale", choices=tuple(SCALES), default="demo", help="demo is quick; portfolio generates large volumes.")
    parser.add_argument("--seed", type=int, default=42, help="Random seed for reproducible output.")
    args = parser.parse_args()
    generate_all(args.output_root, args.scale, args.seed)


if __name__ == "__main__":
    main()

