
# Podcast-Sentiment-Analysis
<img width="1160" height="429" alt="image" src="https://github.com/user-attachments/assets/f01b4952-fa57-4795-82b6-751f5a6b771b" />

<img width="1202" height="620" alt="image" src="https://github.com/user-attachments/assets/dcaf1d6e-2efd-4bca-94e2-2dcf618ec19c" />


<img width="1185" height="503" alt="Screenshot 2025-12-10 at 18 06 22" src="https://github.com/user-attachments/assets/62f135df-bf44-4d64-96c6-a850990c1b18" />

After making the streamlit app, the next step was to automate it.

This is where Audience Says – Automated Sentiment Analysis Pipeline was developed 

Overview

Audience Says is an automated sentiment analysis pipeline designed to ingest unstructured audience feedback (e.g. podcast comments, reviews, social content), clean and standardise the data, enrich it with AI-driven sentiment and emotion analysis, and surface insights through a lightweight analytics application.

The project focuses on end-to-end automation, data pipeline design, and practical analytics engineering, rather than just model output.

This repository represents the automated backend and data engineering layer that powers the application.

⸻

Key Objectives
	•	Automate ingestion of raw audience feedback
	•	Clean and standardise unstructured text data
	•	Apply AI-based sentiment and emotion analysis
	•	Maintain schema consistency across pipeline stages
	•	Store intermediate and final datasets for reuse
	•	Enable downstream analytics and visualisation

⸻

Architecture & Pipeline Flow

The pipeline follows a multi-layer data model inspired by modern analytics engineering practices:
Raw Data → Bronze → Silver → Gold → Application / Insights

1. Data Ingestion (Raw / Bronze)
	•	Source data is collected via APIs and scraping scripts
	•	Data is stored in its raw form with minimal transformation
	•	Purpose: preserve original data for traceability and reprocessing

Examples:
	•	Podcast comments
	•	Audience reviews
	•	User-generated feedback

⸻

2. Data Cleaning & Normalisation (Silver)

At this stage the data is prepared for analysis:
	•	Text cleaned (whitespace, encoding, noise removal)
	•	Nested JSON structures flattened
	•	Columns normalised and standardised
	•	Schema aligned across all records

This ensures:
	•	Consistent column names
	•	Predictable data types
	•	Reliable downstream processing

⸻

3. Enrichment & Analytics Layer (Gold)

The cleaned data is enriched with AI-driven analysis:
	•	Sentiment scoring (positive / neutral / negative)
	•	Emotion classification
	•	Confidence and relevance signals
	•	Aggregated metrics for trend analysis

This layer represents analysis-ready datasets used by the application and dashboards.

⸻

Automation & Orchestration

The pipeline is fully automated and designed to be repeatable:
	•	Python scripts handle ingestion, transformation, and enrichment
	•	Environment variables are managed securely using .env
	•	API keys and service credentials are isolated from source control
	•	The pipeline can be rerun end-to-end without manual intervention

This setup reflects real-world production patterns rather than one-off scripts.

project-root/
│
├── data/
│   ├── raw/        # Original ingested data
│   ├── bronze/     # Lightly structured data
│   ├── silver/     # Cleaned & normalised data
│   └── gold/       # Analysis-ready datasets
│
├── scripts/
│   ├── ingest/     # Data ingestion logic
│   ├── transform/  # Cleaning & normalisation
│   └── enrich/     # Sentiment & emotion analysis
│
├── app/
│   └── streamlit/  # Frontend analytics app
│
├── .env.example
├── requirements.txt
└── README.md

Technologies Used
	•	Python
	•	APIs & Web Scraping
	•	AI / LLM-based Sentiment Analysis
	•	Pandas for data transformation
	•	Streamlit for analytics delivery
	•	Environment-based configuration
	•	CSV-based analytical storage (extensible to DBs)

⸻

What This Project Demonstrates
	•	End-to-end data pipeline thinking
	•	Automation-first mindset
	•	Practical handling of unstructured data
	•	Schema consistency and data quality control
	•	Applying AI as a tool within a pipeline (not as a black box)
	•	Translating raw data into business-facing insights

⸻

Status

This project is actively evolving and forms part of a broader suite of analytics products, including:
	•	Automated sentiment analysis tools
	•	Market-level insight dashboards
	•	Executive-friendly reporting applications

⸻

Notes

This repository intentionally focuses on pipeline design, automation, and analytics readiness, rather than model training. The goal is to demonstrate how AI-powered insights are operationalised in a real product environment.

