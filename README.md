## Universal Price Tracker

Search any product by keyword across multiple stores and get the best price — automatically.

![Python](https://img.shields.io/badge/Python-3.11+-blue?logo=python)
![FastAPI](https://img.shields.io/badge/FastAPI-0.110+-green?logo=fastapi)
![Playwright](https://img.shields.io/badge/Playwright-latest-orange?logo=playwright)
![PostgreSQL](https://img.shields.io/badge/PostgreSQL-15+-blue?logo=postgresql)
![Docker](https://img.shields.io/badge/Docker-ready-blue?logo=docker)
![License](https://img.shields.io/badge/License-MIT-yellow)

---

## What is this?

Universal Price Tracker is a web scraping application that takes any keyword (e.g. `"RTX 4070"`, `"Elden Ring"`, `"iPhone 15"`) and searches multiple online stores simultaneously to find and compare the best prices — sorted cheapest first.

It is not limited to games — it works for any product on any supported store.

---

## Features

- Search by any keyword — games, electronics, books, anything
- Scrapes multiple stores in parallel (Amazon, eBay, Newegg, Google Shopping, and more)
- Returns results sorted by price (cheapest first)
- Supports multiple currencies (USD, EUR, GBP, MAD, AED)
- Deduplicates and normalizes results across stores
- Async scraping — fast, non-blocking
- Price history stored in PostgreSQL
- Auto-refresh prices via Celery scheduler
- Full QA test suite (unit, integration, E2E)
- Docker ready — runs on any Linux machine

---

## Tech Stack

| Layer      | Tool                  | Purpose                          |
|------------|-----------------------|----------------------------------|
| Language   | Python 3.11+          | Core language                    |
| Scraping   | Playwright            | JS-heavy sites                   |
| HTTP       | httpx                 | Async API calls                  |
| Parsing    | BeautifulSoup4        | Extract data from HTML           |
| Backend    | FastAPI               | REST API                         |
| Database   | PostgreSQL            | Store price history              |
| ORM        | SQLAlchemy            | Database models                  |
| Cache      | Redis                 | Avoid re-scraping same keyword   |
| Scheduler  | Celery + Redis        | Auto price refresh every 6h      |
| Testing    | Pytest + Playwright   | Unit, integration, E2E tests     |
| QA / Lint  | Ruff + Black + mypy   | Code quality                     |
| Container  | Docker + Compose      | Linux deployment                 |
| CI/CD      | GitHub Actions        | Auto test on every push          |

---

## Project Structure

```
universal-price-tracker/
│
├── backend/
│   ├── app/
│   │   ├── main.py                  # FastAPI entry point
│   │   ├── config.py                # Settings, env vars
│   │   │
│   │   ├── scrapers/
│   │   │   ├── base.py              # Base scraper (retry, timeout, headers)
│   │   │   ├── google_shopping.py   # Google Shopping by keyword
│   │   │   ├── amazon.py            # Amazon search
│   │   │   ├── ebay.py              # eBay search
│   │   │   ├── newegg.py            # Newegg (tech products)
│   │   │   └── manager.py           # Run all scrapers in parallel
│   │   │
│   │   ├── api/
│   │   │   ├── routes/
│   │   │   │   ├── search.py        # GET /search?q=RTX+4070
│   │   │   │   └── history.py       # GET /history/{keyword}
│   │   │   └── deps.py              # Shared dependencies
│   │   │
│   │   ├── models/
│   │   │   ├── result.py            # PriceResult DB model
│   │   │   └── search.py            # SearchQuery model
│   │   │
│   │   ├── schemas/
│   │   │   └── price.py             # Pydantic response schemas
│   │   │
│   │   ├── core/
│   │   │   ├── normalizer.py        # Normalize price formats + currencies
│   │   │   ├── deduplicator.py      # Remove duplicate results
│   │   │   └── ranker.py            # Sort by price / relevance
│   │   │
│   │   ├── services/
│   │   │   ├── search_service.py    # Orchestrate scraping + ranking
│   │   │   └── cache_service.py     # Redis caching logic
│   │   │
│   │   └── tasks/
│   │       └── celery_tasks.py      # Scheduled auto-refresh jobs
│   │
│   ├── tests/
│   │   ├── unit/
│   │   │   ├── test_normalizer.py
│   │   │   ├── test_deduplicator.py
│   │   │   ├── test_amazon.py
│   │   │   └── test_google_shopping.py
│   │   ├── integration/
│   │   │   └── test_api.py
│   │   └── e2e/
│   │       └── test_full_flow.py
│   │
│   ├── Dockerfile
│   ├── requirements.txt
│   └── pytest.ini
│
├── frontend/                        # Phase 2
│   ├── src/
│   │   ├── components/
│   │   │   ├── SearchBar.jsx
│   │   │   ├── ResultCard.jsx
│   │   │   └── PriceChart.jsx
│   │   └── pages/
│   │       └── Home.jsx
│   └── package.json
│
├── docker-compose.yml
├── .env.example
├── .github/
│   └── workflows/
│       └── ci.yml
└── README.md
```

---

## Development Phases

### Phase 1 — Core Scrapers
- [ ] Project setup (venv, folder structure)
- [ ] Base scraper class (retry, timeout, user-agent rotation)
- [ ] Google Shopping scraper with Playwright
- [ ] Amazon scraper
- [ ] eBay scraper
- [ ] Run all scrapers in parallel with asyncio.gather()

### Phase 2 — Backend API
- [ ] FastAPI app + router setup
- [ ] GET /search?q={keyword}&currency={USD} endpoint
- [ ] GET /history/{keyword} endpoint
- [ ] PostgreSQL models + migrations (Alembic)
- [ ] Redis caching — skip re-scraping same keyword within 1 hour
- [ ] Structured error handling + logging

### Phase 3 — QA and Testing
- [ ] Pytest setup + fixtures
- [ ] Unit tests for each scraper (mock HTTP responses)
- [ ] Unit tests for normalizer, deduplicator, ranker
- [ ] Integration tests for API endpoints
- [ ] E2E tests with Playwright
- [ ] Coverage report — target 80%+
- [ ] Ruff + Black linting
- [ ] mypy type checking
- [ ] GitHub Actions CI pipeline

### Phase 4 — Scheduler and Monitoring
- [ ] Celery + Redis setup
- [ ] Auto-refresh tracked keywords every 6 hours
- [ ] Flower dashboard for monitoring tasks
- [ ] Structured logging (JSON format)

### Phase 5 — Frontend
- [ ] React + Tailwind UI
- [ ] Keyword search bar
- [ ] Results grid (price card per store)
- [ ] Price history chart (Recharts)
- [ ] Currency selector
- [ ] Email alert for price drops

---

## Quick Start (Linux)

### 1. Clone the repo
```bash
git clone https://github.com/your-username/universal-price-tracker.git
cd universal-price-tracker
```

### 2. Create virtual environment
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Install Playwright browsers
```bash
playwright install chromium
```

### 4. Set environment variables
```bash
cp .env.example .env
# Edit .env with your values
```

### 5. Start services (PostgreSQL + Redis)
```bash
docker-compose up -d
```

### 6. Run the API
```bash
uvicorn app.main:app --reload
```

### 7. Test it
```bash
curl "http://localhost:8000/search?q=RTX+4070&currency=USD"
```

---

## Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage report
pytest tests/ -v --cov=app --cov-report=html

# Run only unit tests
pytest tests/unit/ -v

# Run only integration tests
pytest tests/integration/ -v

# Run linter
ruff check app/

# Run type checker
mypy app/
```

---

## API Reference

### Search by keyword

```
GET /search?q={keyword}&currency={USD}&country={US}
```

Example:
```bash
curl "http://localhost:8000/search?q=iPhone+15&currency=USD"
```

Response:
```json
{
  "keyword": "iPhone 15",
  "currency": "USD",
  "total_results": 12,
  "results": [
    {
      "title": "Apple iPhone 15 128GB",
      "price": 699.99,
      "currency": "USD",
      "store": "Amazon",
      "url": "https://amazon.com/...",
      "image": "https://...",
      "rating": 4.7,
      "in_stock": true
    }
  ]
}
```

### Price history

```
GET /history/{keyword}?days=30
```

---

## QA Testing Strategy

| Test Type   | Tool                    | What It Covers                              |
|-------------|-------------------------|---------------------------------------------|
| Unit        | pytest + pytest-mock    | Scraper logic, parsing, normalizer          |
| Mock HTTP   | pytest-mock / responses | Fake store responses, no real scraping      |
| API         | httpx + pytest          | FastAPI endpoints, status codes, schema     |
| E2E         | Playwright              | Full keyword to scrape to response flow     |
| Load        | Locust                  | Concurrent search capacity                  |
| Lint        | Ruff + Black            | Code style consistency                      |
| Types       | mypy                    | Type safety across the codebase             |
| Coverage    | pytest-cov              | Percentage of code covered by tests         |
| CI          | GitHub Actions          | Auto-run all tests on every push            |

### Edge cases to always test

```
keyword = ""                        -> 422 validation error, not a crash
keyword = "xyznotarealproduct123"   -> empty results, 200 OK
price = "$1,299.00"                 -> parsed correctly as 1299.00
currency = "MAD"                    -> converted correctly from USD
one scraper fails                   -> others still return results
same product from 2 stores          -> deduplicated correctly
```

---

## Free APIs You Can Use

| API               | What it gives                    | Key needed?    |
|-------------------|----------------------------------|----------------|
| Steam Store API   | Game prices + discounts          | No             |
| IsThereAnyDeal    | 30+ game stores aggregated       | Free key       |
| CheapShark        | PC game deals                    | No             |
| RAWG              | Game metadata + images           | Free key       |
| Google Shopping   | Any product (via scraping)       | No (scrape)    |
| SerpAPI           | Google Shopping results via API  | Paid/free tier |

---

## Docker Compose

```yaml
version: "3.9"
services:
  api:
    build: ./backend
    ports:
      - "8000:8000"
    depends_on:
      - db
      - redis
    env_file: .env

  db:
    image: postgres:15
    environment:
      POSTGRES_DB: pricetracker
      POSTGRES_USER: user
      POSTGRES_PASSWORD: password
    volumes:
      - pgdata:/var/lib/postgresql/data

  redis:
    image: redis:7-alpine

  celery:
    build: ./backend
    command: celery -A app.tasks worker --loglevel=info
    depends_on:
      - redis

volumes:
  pgdata:
```

---

## CI/CD — GitHub Actions

```yaml
name: CI

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-python@v5
        with:
          python-version: "3.11"
      - name: Install dependencies
        run: |
          cd backend
          pip install -r requirements.txt
          playwright install chromium
      - name: Lint
        run: ruff check backend/app/
      - name: Type check
        run: mypy backend/app/
      - name: Run tests
        run: pytest backend/tests/ -v --cov=app
```

---

## Anti-blocking Strategy

To avoid getting blocked by stores:

- Rotate User-Agent headers randomly
- Add random delays between requests (1-3 seconds)
- Use Playwright for JS-heavy pages (looks like a real browser)
- Use proxy rotation for high-volume scraping
- Respect robots.txt where possible
- Cache results in Redis — do not scrape the same keyword twice within 1 hour

---

## Requirements

```
fastapi>=0.110
uvicorn>=0.29
playwright>=1.43
httpx>=0.27
beautifulsoup4>=4.12
sqlalchemy>=2.0
alembic>=1.13
psycopg2-binary>=2.9
redis>=5.0
celery>=5.3
pydantic>=2.6
pytest>=8.0
pytest-asyncio>=0.23
pytest-mock>=3.14
pytest-cov>=5.0
ruff>=0.4
black>=24.0
mypy>=1.9
locust>=2.28
```

---

## Git Workflow

```bash
# Start a new feature
git checkout -b feature/amazon-scraper

# Get latest changes from main
git fetch origin
git merge origin/main

# Push your branch
git push origin feature/amazon-scraper

# Open a pull request on GitHub -> CI runs automatically
```

---

## License

MIT Forfunn
