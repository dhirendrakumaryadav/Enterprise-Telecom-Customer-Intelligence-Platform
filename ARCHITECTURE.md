# Platform Architecture

## Overview

The Enterprise Telecom Customer Intelligence Platform is a Databricks lakehouse built on the Medallion Architecture. It combines telecom customer, billing, and network-event data from batch and streaming sources to provide reliable analytics and an AI-powered customer assistant.

## Data Flow

```text
Azure SQL Database
  (batch customer data)
        |
        v
Azure Data Factory (optional orchestration)
        |
        v
Azure Data Lake Storage Gen2
        |
        v
Databricks Auto Loader / ingestion
        |
        v
Bronze Layer (Delta Lake)
        |
        v
Spark Declarative Pipelines
        |
        v
Silver Layer
  Cleaning | Validation | CDC | Deduplication
        |
        v
Gold Layer
  Star schema | Business KPIs
        |
        +-----------------------------+
        |                             |
        v                             v
Databricks AI/BI Dashboard      Mosaic AI
                                      |
                                      v
                                Vector Search
                                      |
                                      v
                           AI Customer Assistant
```

## Layers

| Layer | Purpose |
| --- | --- |
| Bronze | Stores raw ingested data in Delta tables. |
| Silver | Cleans, validates, deduplicates, and applies change-data-capture logic. |
| Gold | Provides curated star-schema datasets and business KPIs for consumption. |

## Core Technologies

- Azure Data Lake Storage Gen2
- Azure SQL Database
- Azure Data Factory
- Databricks: Unity Catalog, Delta Lake, Auto Loader, Spark Declarative Pipelines, Lakehouse Monitoring, AI/BI Dashboards, Mosaic AI, and Vector Search
- PySpark and SQL

