# Enterprise Telecom Customer Intelligence Platform

An end-to-end data engineering and AI portfolio project for telecom customer, billing, support, and network analytics.

The platform will use Azure Databricks and a Medallion architecture to turn raw source data into governed, analytics-ready datasets and an AI-assisted support experience.

## Status

🚧 **Sprint 1 — Project initialization**

## Target architecture

```text
Source CSVs / CDC / network events
                |
                v
        ADLS Gen2 landing zone
                |
                v
       Auto Loader -> Bronze Delta
                |
                v
 Spark Declarative Pipelines -> Silver
                |
                v
      Gold star schema and KPI tables
          |                      |
          v                      v
AI/BI dashboards     Mosaic AI + Vector Search
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for the detailed architecture.

## Planned technology stack

- Azure Data Lake Storage Gen2 and Azure Databricks
- PySpark, SQL, Delta Lake, and Spark Declarative Pipelines
- Unity Catalog, Auto Loader, and Lakehouse Monitoring
- Mosaic AI, Vector Search, and Databricks AI/BI Dashboards
- Python, Git, and GitHub

## Repository layout

```text
├── architecture/   # diagrams and architecture assets
├── configs/        # non-secret local and deployment configuration
├── datasets/raw/   # generated source-data landing files (not committed)
├── docs/           # technical and operational documentation
├── notebooks/      # exploration and Databricks notebooks
├── pipelines/      # Spark Declarative Pipeline definitions
├── src/            # reusable Python modules
│   ├── ai/
│   ├── common/
│   ├── generators/
│   ├── ingestion/
│   └── transformations/
└── tests/          # automated tests
```

## Local setup

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

No cloud credentials are committed to this repository. Copy `.env.example` to `.env` when a later sprint needs local credentials.
