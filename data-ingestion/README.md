# Data Ingestion

This folder contains the data ingestion system for the UMD Waitlist Alert project.

Its job is to scrape course information from Testudo and keep the PostgreSQL database updated.

## What It Does

There are two main scraping processes.

### 1. Course Catalog Scraper

This scraper collects general course and section information such as:

* Course code
* Course name
* Description
* Credits
* Section number
* Professor
* Meeting time
* Location

This data does not change very often, so the scraper will run when a new semester becomes available and periodically afterward to keep the database updated.

### 2. Course Availability Scraper

This scraper checks seat availability for course sections.

It tracks values such as:

* Open seats
* Waitlist count
* Total seats

Sections that users are actively monitoring will be checked approximately every **5 minutes**.

When availability changes, the new values will be stored in PostgreSQL.

Example:

```text
CMSC216-0101

0 open seats
      ↓
2 open seats
```

This change can then trigger the notification system to alert users monitoring that section.

## Data Flow

```text
Testudo
   ↓
Scraper
   ↓
Parse Course Data
   ↓
PostgreSQL
   ↓
Backend / Notification System
   ↓
Email Alert
```

The ingestion service is responsible for **finding and storing changes**.

The backend is responsible for **determining which users should be notified and sending notifications**.

## Tech Stack

* **Requests** — Fetch Testudo pages
* **BeautifulSoup** — Parse course information
* **PostgreSQL** — Store course and section data
* **Psycopg 3** — Connect Python to PostgreSQL
* **FastAPI / Uvicorn** — Run the containerized ingestion service
* **Python logging** — Track scraper runs and errors

## Folder Structure

```text
data-ingestion/
├── src/
│   ├── catalog/
│   │   ├── __init__.py
│   │   ├── scraper.py
│   │   └── parser.py
│   │
│   ├── availability/
│   │   ├── __init__.py
│   │   ├── scraper.py
│   │   └── parser.py
│   │
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py
│   │   └── repository.py
│   │
│   ├── models/
│   │   ├── __init__.py
│   │   ├── course.py
│   │   └── section.py
│   │
│   ├── __init__.py
│   ├── config.py
│   └── main.py
│
├── tests/
├── Dockerfile
├── requirements.txt
├── .env.example
└── README.md
```

## Logging

Each scraper run should log:

* When the scrape started
* When it finished
* Number of courses or sections processed
* Number of database records updated
* Errors that occurred

Example:

```text
INFO - Availability scrape started
INFO - Checked 84 sections
INFO - Updated 6 sections
INFO - Availability scrape completed
```

## Running the Scrapers

Start the development API (this is also the Docker default):

```bash
uvicorn src.main:app --host 0.0.0.0 --port 8000 --reload
```

The initial scaffold exposes `GET /health`. Catalog and availability jobs can be
added to the app once their scheduling and database schema are finalized.

The intended command-line interface is:

Run the course catalog scraper:

```bash
python -m src.main catalog
```

Run the availability scraper:

```bash
python -m src.main availability
```

Scheduling is external to this service. In production, a scheduler should run
catalog jobs when terms are published and availability jobs at the desired
interval; Uvicorn's `--reload` option is for local development only.

## Goal

The goal of this service is to maintain a reliable local database of UMD course information so the rest of the application does not need to scrape Testudo whenever a user searches for a course.

Frequently monitored sections can then be checked every few minutes so users can quickly be notified when seats become available.
