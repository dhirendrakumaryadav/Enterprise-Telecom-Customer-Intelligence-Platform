"""
Generate support tickets with realistic telecom issues, resolution notes,
and embedded PII (phone numbers, emails, customer names, IMSIs) to rigorously test
Microsoft Presidio anonymization and Change Data Feed (CDC) lifecycle pipelines.
"""

from __future__ import annotations

import logging
import random
from datetime import date, timedelta
from pathlib import Path
from typing import Dict, List, Optional

from .common import read_csv, write_csv

logger = logging.getLogger(__name__)

REFERENCE_DATE = date(2026, 1, 1)

SUPPORT_FIELDS = [
    "ticket_id",
    "customer_id",
    "category",
    "priority",
    "description",
    "resolution_notes",
    "status",
    "created_date",
    "resolved_date",
    "circle",
    "load_date",
]

ISSUES: Dict[str, List[str]] = {
    "Network Issue": [
        "Intermittent network coverage near {city}; repeated call drops during peak hours.",
        "Zero cellular signal indoors at {city} following nocturnal cell tower power failure.",
        "Severe RF interference and packet loss observed on sector antenna near {city} commercial hub.",
    ],
    "Slow Internet": [
        "Mobile data speed severely throttled in {city}, latency exceeding 450ms on 4G Band 40.",
        "High downlink packet loss observed in {city} while streaming or accessing corporate VPN.",
    ],
    "Billing Issue": [
        "Disputed roaming charges appearing on invoice after travelling outside {circle} circle.",
        "Monthly postpaid bill generated with unprorated tariff plan upgrade charge.",
        "Double deduction occurred during automatic bill debit for account ACC-{customer_id}.",
    ],
    "SIM Activation": [
        "e-SIM QR code profile installation failing with timeout at SM-DP+ server.",
        "Physical SIM port-in verification pending beyond standard regulatory SLA.",
    ],
    "Call Drop": [
        "Voice calls dropping consistently after 30 seconds across {city} sector 2 coverage zone.",
        "VoLTE handover failure occurring when transitioning between cell sites in {city}.",
    ],
    "Recharge Failure": [
        "Prepaid recharge transaction debited via UPI, but account balance was not credited by OCS.",
        "Data voucher pack activation failed despite bank confirmation reference.",
    ],
    "5G Issue": [
        "5G Standalone (SA) connection dropping to 3G/LTE in {city} despite 5G-ready device.",
        "gNodeB carrier aggregation failing on n78 band, leading to low throughput in {city}.",
    ],
    "Roaming Issue": [
        "Data roaming non-functional while traveling outside {circle} home circle.",
        "Subscriber unable to latch onto partner network in foreign roaming territory.",
    ],
}

RESOLUTIONS: Dict[str, List[str]] = {
    "Network Issue": [
        "Field dispatch restored power unit and replaced faulty RF combiner at {city} node.",
        "Re-aligned sector antenna azimuth by 15 degrees to optimize signal coverage.",
    ],
    "Slow Internet": [
        "Re-tuned carrier aggregation parameters on Band 40; bandwidth restored to SLA levels.",
        "Cleared local backhaul switch congestion and updated QoS queue allocation.",
    ],
    "Billing Issue": [
        "Billing dispute verified. Credit memo issued for disputed amount against account ACC-{customer_id}.",
        "Reversed unprorated charge and applied promotional discount to next billing cycle.",
    ],
    "SIM Activation": [
        "Re-triggered SM-DP+ profile download notification and refreshed KYC portal status.",
        "Manual profile sync performed by core network operations team; subscriber active.",
    ],
    "Call Drop": [
        "Adjusted VoLTE handover thresholds (A2/A3 events) between adjacent base stations in {city}.",
        "Reset corrupted baseband channel card on sector 2 tower.",
    ],
    "Recharge Failure": [
        "Reconciled transaction with payment gateway. OCS balance updated and SMS confirmation sent.",
        "Manual ledger adjustment executed; plan benefits credited with extended validity.",
    ],
    "5G Issue": [
        "Deployed baseband firmware patch 4.2.1 on gNodeB unit to resolve 5G SA connection drops.",
        "Reconfigured 5G core network AMF routing policy for device profile.",
    ],
    "Roaming Issue": [
        "Re-provisioned roaming service profile in HLR/HSS registry.",
        "Subscriber profile cleared in foreign VLR and roaming latch successfully established.",
    ],
}


def generate_support_tickets(
    customers_path: str | Path,
    output_path: str | Path,
    num_records: int,
    seed: int = 42,
    pii_injection_rate: float = 0.65,
) -> Path:
    """
    Generate realistic telecom support tickets with realistic operational notes,
    resolution narratives, and embedded PII to validate Presidio anonymization.
    """
    if num_records <= 0:
        raise ValueError("num_records must be greater than zero")

    rng = random.Random(seed)
    customers = read_csv(customers_path)

    if not customers:
        raise ValueError("customers_path does not contain any customer records")

    categories = list(ISSUES.keys())
    start_date = REFERENCE_DATE - timedelta(days=180)
    rows = []

    for ticket_number in range(1, num_records + 1):
        customer = rng.choice(customers)
        category = rng.choices(
            categories,
            weights=[20, 18, 14, 8, 14, 10, 12, 4],
            k=1,
        )[0]

        priority = rng.choices(
            ["LOW", "MEDIUM", "HIGH", "CRITICAL"],
            weights=[15, 55, 25, 5],
            k=1,
        )[0]

        status = rng.choices(
            ["OPEN", "IN_PROGRESS", "RESOLVED", "CLOSED"],
            weights=[12, 18, 45, 25],
            k=1,
        )[0]

        created_date = start_date + timedelta(days=rng.randrange(181))
        resolved_date = None
        resolution_note = ""

        city = customer.get("city", "Mumbai")
        circle = customer.get("circle", customer.get("state", "Maharashtra"))
        cust_id = customer.get("customer_id", f"{ticket_number:05d}")

        # Pick base description
        base_desc_template = rng.choice(ISSUES[category])
        base_desc = base_desc_template.format(city=city, circle=circle, customer_id=cust_id)

        # Inject realistic PII into description based on pii_injection_rate
        if rng.random() < pii_injection_rate:
            full_name = customer.get("full_name", "Subscriber")
            phone = customer.get("phone_number", "+919876543210")
            email = customer.get("email", "subscriber@telecom.net")
            
            pii_prefixes = [
                f"Customer {full_name} (Contact: {phone}) reported: ",
                f"Escalation for subscriber {full_name} (reachable at {phone}, {email}): ",
                f"Complaint logged by {full_name} regarding MSISDN {phone}: ",
                f"Callback requested on {phone} for account ACC-{cust_id}: ",
            ]
            description = f"{rng.choice(pii_prefixes)}{base_desc}"
        else:
            description = base_desc

        if status in ("RESOLVED", "CLOSED"):
            resolved_date = (created_date + timedelta(days=rng.randint(1, 8))).isoformat()
            res_template = rng.choice(RESOLUTIONS[category])
            resolution_note = res_template.format(city=city, circle=circle, customer_id=cust_id)

        rows.append(
            {
                "ticket_id": f"TKT{ticket_number:010d}",
                "customer_id": cust_id,
                "category": category,
                "priority": priority,
                "description": description,
                "resolution_notes": resolution_note,
                "status": status,
                "created_date": created_date.isoformat(),
                "resolved_date": resolved_date or "",
                "circle": circle,
                "load_date": REFERENCE_DATE.isoformat(),
            }
        )

    output_file = write_csv(output_path, SUPPORT_FIELDS, rows)
    logger.info("Generated %s realistic support tickets with PII at %s", num_records, output_file)
    return output_file
