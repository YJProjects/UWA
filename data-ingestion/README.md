# Data Ingestion Service

This folder contains the data ingestion pipeline responsible for collecting and maintaining UMD course and section data used by the application.

## Purpose

The ingestion service is responsible for the following workflow:

1. **Scrape course data from Testudo**

   * Retrieve course and section information from the UMD Testudo Schedule of Classes.
   * Extract relevant fields such as course information, section numbers, instructors, seat availability, and waitlist counts.

2. **Incrementally update the database**

   * Compare newly scraped course data with the data currently stored in PostgreSQL.
   * Insert newly discovered courses or sections.
   * Update existing records only when their values have changed.
   * Track important availability transitions, particularly when a section changes from `0` open seats to `1+`.

3. **Logging and monitoring**

   * Log the start and completion of every ingestion run.
   * Record the number of courses and sections processed.
   * Log inserted, updated, and unchanged records.
   * Record scraping, parsing, database, and network failures.
   * Include timestamps and useful context for debugging failed ingestion runs.

## Data Flow

```text
Testudo
   │
   ▼
Scraper
BeautifulSoup + Requests
   │
   ▼
Data Parsing / Normalization
   │
   ▼
Compare with existing records
   │
   ▼
PostgreSQL
   │
   ├── New records → INSERT
   │
   ├── Changed records → UPDATE
   │
   └── Unchanged records → Ignore
   │
   ▼
Database change / webhook
   │
   ▼
UWA Backend
   │
   ▼
Notify users monitoring affected sections
```

After a successful ingestion cycle, relevant database changes should trigger the backend notification workflow.

For example:

```text
Previous state:
CMSC216-0101 → 0 open seats

New scraped state:
CMSC216-0101 → 2 open seats

Database updated
      ↓
Availability-change event triggered
      ↓
Backend identifies users monitoring CMSC216-0101
      ↓
Users receive a seat-availability notification
```

The ingestion service itself should focus on **collecting and updating course data**. User notification logic should remain within the backend rather than being implemented directly inside the scraper.

## Tech Stack

### Web Scraping

* **Requests** — Retrieve HTML pages from Testudo.
* **BeautifulSoup** — Parse HTML and extract course and section information.

### Database

* **PostgreSQL** — Store normalized course and section data.
* **psycopg2** — Connect to PostgreSQL and perform database operations.

### Logging

* Python's built-in `logging` module for:

  * ingestion lifecycle events
  * scraper failures
  * database errors
  * record counts
  * availability changes

## Suggested Folder Structure

```text
data-ingestion/
├── src/
│   ├── scraper/
│   │   ├── testudo_scraper.py
│   │   └── parser.py
│   │
│   ├── database/
│   │   ├── connection.py
│   │   └── repository.py
│   │
│   ├── models/
│   │   └── course.py
│   │
│   ├── services/
│   │   └── ingestion_service.py
│   │
│   ├── config.py
│   └── main.py
│
├── tests/
│   ├── test_parser.py
│   └── test_ingestion.py
│
├── logs/
│
├── requirements.txt
├── .env.example
├── Dockerfile
└── README.md
```

## Responsibilities

The data ingestion service **should**:

* Scrape public course information.
* Parse and normalize scraped data.
* Maintain current course and section information in PostgreSQL.
* Detect changes between ingestion cycles.
* Produce structured logs.
* Handle temporary Testudo or database failures gracefully.

The data ingestion service **should not**:

* Authenticate application users.
* Store user passwords.
* Send notification emails directly.
* Handle frontend requests.
* Automatically register students for courses.

Those responsibilities belong to the UWA backend.

## Future Improvements

Potential improvements after the initial prototype include:

* Asynchronous scraping for improved performance.
* Request retries with exponential backoff.
* Configurable scraping intervals.
* Database transactions and batch upserts.
* Historical section-availability snapshots.
* Metrics for ingestion duration and failure rate.
* Automated scheduled execution using a containerized worker or scheduled job.
