# Enterprise-Telecom-Customer-Intelligence-Platform
Designed an enterprise Lakehouse platform on Databricks using Medallion Architecture, integrating telecom customer, billing, and network event data through batch and streaming ingestion.
                        Azure SQL Database
                               │
                        (Batch Customer Data)
                               │
                               ▼
                   Azure Data Factory (Optional)
                               │
                               ▼
                    Azure Data Lake Storage Gen2
                               │
                               ▼
                  Databricks Auto Loader / Ingestion
                               │
                               ▼
                         Bronze Layer (Delta)
                               │
                Spark Declarative Pipelines
                               │
                               ▼
                         Silver Layer
          Cleaning • Validation • CDC • Deduplication
                               │
                               ▼
                          Gold Layer
                 Star Schema + Business KPIs
                    /                     \
                   /                       \
     Databricks AI/BI Dashboard      Mosaic AI
                                             │
                                     Vector Search
                                             │
                                   AI Customer Assistant


->Technologies We'll Actually Use
Azure
Azure Data Lake Storage Gen2
Azure SQL Database
Azure Data Factory (later)
Azure Portal
->Databricks
Unity Catalog
Delta Lake
Spark Declarative Pipelines
Auto Loader
Lakehouse Monitoring
AI/BI Dashboards
Mosaic AI
Vector Search
->Data Engineering
PySpark
SQL
Medallion Architecture
CDC
Star Schema

Step 1
Databricks

↓

Step 2
Delta Lake

↓

Step 3
Spark Declarative Pipelines

↓

Step 4
Unity Catalog

↓

Step 5
AI

↓

Step 6
ADF Orchestration



--->
