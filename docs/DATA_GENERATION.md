# Synthetic Data Generation

Sprint 2 simulates six telecom source systems: CRM customers, plan catalogue, postpaid billing, prepaid recharge, support tickets, and network telemetry.

## Referential integrity

- Every customer receives one valid plan ID.
- Billing records are created only for active postpaid customers.
- Recharge records are created only for active prepaid customers.
- Support and network records always reference a generated customer ID.

## Run locally

After creating and activating the virtual environment, run:

```powershell
pip install -r requirements.txt
python -m src.generators.generate_all --scale demo
```

`demo` produces a small, fast dataset. `portfolio` creates the target-scale data set (100,000 customers and millions of telemetry events), so run it only when you have sufficient disk and time:

```powershell
python -m src.generators.generate_all --scale portfolio
```

Generated files stay out of Git and will later be uploaded to the ADLS Gen2 `landing` container.

