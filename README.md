# Ebook Lead Engine

An automated lead generation system that scrapes Reddit, Upwork, and Amazon KDP for authors struggling with ebook formatting.

## Features

- **Reddit Collector**: Scrapes subreddits for keywords related to formatting pain points.
- **Upwork Collector**: Monitors RSS feeds for ebook formatting jobs.
- **Amazon KDP Collector**: Uses Selenium to inspect "Look Inside" for formatting issues in new releases.
- **AI Enrichment**: Uses OpenAI to draft personalized outreach messages.
- **CRM Integration**: Syncs leads to Google Sheets.
- **Notifications**: Sends high-value lead alerts via Telegram.

## Setup

### 1. Prerequisites

- Python 3.11+
- PostgreSQL
- Redis (if using Celery)
- Google Chrome (for Selenium)

### 2. Configuration

Copy `.env.example` to `.env` and fill in your API keys:

```bash
cp .env.example .env
```

You also need a `google_creds.json` file in the root directory for Google Sheets integration.

### 3. Installation

```bash
pip install -r requirements.txt
```

### 4. Database Initialization

```bash
# Initialize schema (if not using Docker)
psql -U your_user -d leads_db -f scripts/init_db.sql

# Seed keywords
python scripts/seed_keywords.py
```

### 5. Running the Application

#### Option A: Local Run (FastAPI)

```bash
uvicorn app.main:app --reload
```

#### Option B: Docker (Recommended)

```bash
docker-compose up --build
```

## API Endpoints

- `GET /health`: Check service status.
- `POST /trigger/reddit`: Manually trigger Reddit collection.
- `POST /trigger/upwork`: Manually trigger Upwork collection.
- `POST /trigger/amazon`: Manually trigger Amazon collection.

## Directory Structure

- `app/`: Core application logic.
  - `collectors/`: Source-specific scrapers.
  - `models/`: Database and Pydantic models.
  - `enrichment/`: Email finding and deduplication.
  - `outreach/`: AI draft generation.
- `scripts/`: DB initialization and seeding scripts.
- `Dockerfile` & `docker-compose.yml`: Containerization setup.
