# AI Football Live

Live football matches with AI-powered analysis. A Flutter mobile app backed by a FastAPI Python backend with PostgreSQL and Redis.

## Architecture

```
Flutter App (iOS/Android/Web)
        ↓ HTTP
FastAPI Backend (Python 3.14)
        ↓
PostgreSQL 16  ←→  Redis 7
        ↓
Football Data Provider (Mock / API-Football)
        ↓
AI Provider (Mock / Groq)
```

## Features

- **Live matches** with real-time score updates
- **Match details** with events, statistics, and venue info
- **AI analysis** with hallucination detection and validation scoring
- **Stream resolution** for authorized broadcast sources
- **Arabic + English** localization support
- **Dark/Light theme** with system theme detection
- **Pull-to-refresh** on all list screens

## Tech Stack

### Backend
- **Framework:** FastAPI (async Python)
- **Database:** PostgreSQL 16 via SQLAlchemy (async) + Alembic migrations
- **Cache:** Redis 7 (with in-memory fallback)
- **AI:** Groq API (`openai/gpt-oss-120b` default)
- **Containerization:** Docker + Docker Compose

### Flutter
- **State Management:** Provider
- **Navigation:** Material routes with go_router support
- **HTTP:** http package
- **Image Caching:** cached_network_image
- **Localization:** Flutter gen-l10n (English + Arabic)

## Project Structure

```
├── ai_football_live/              # Flutter application
│   ├── lib/
│   │   ├── main.dart              # App entry point
│   │   ├── config/                # Theme, API config
│   │   ├── models/                # Data models + enums
│   │   ├── screens/               # Screen widgets (split by feature)
│   │   ├── services/              # API client
│   │   ├── widgets/               # Reusable widgets
│   │   └── l10n/                  # Localization ARB files
│   └── test/                      # Flutter tests
│
├── ai_football_live_backend/      # Python backend
│   ├── app/
│   │   ├── main.py                # FastAPI app factory
│   │   ├── config.py              # Pydantic settings
│   │   ├── core/                  # Domain models, enums, exceptions
│   │   ├── database/              # SQLAlchemy models, repos, engine
│   │   ├── api/                   # Routes, DI, error handlers
│   │   ├── services/              # Business logic (match, stream, AI, sync)
│   │   └── providers/             # External integrations (AI, football, cache, stream)
│   ├── alembic/                   # Database migrations
│   ├── tests/                     # Backend tests
│   └── scripts/                   # Seed scripts
│
└── docker-compose.yml             # PostgreSQL + Redis + Backend
```

## Setup

### Prerequisites

- Python 3.14+
- Flutter 3.44+
- Docker & Docker Compose (optional)
- PostgreSQL 16 (if not using Docker)
- Redis 7 (optional, falls back to in-memory)

### Backend

```bash
cd ai_football_live_backend

# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install dependencies
pip install -e ".[dev]"

# Copy environment config
cp .env.example .env

# Run database migrations
alembic upgrade head

# Seed mock data
python scripts/seed.py

# Start the server
uvicorn app.main:app --reload --port 8000
```

### Flutter

```bash
cd ai_football_live

# Install dependencies
flutter pub get

# Run tests
flutter test

# Run the app
flutter run
```

### Docker

```bash
# Start all services
docker-compose up -d

# Run migrations inside the backend container
docker-compose exec backend alembic upgrade head

# Seed data
docker-compose exec backend python scripts/seed.py
```

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/api/v1/health` | Health check (DB + Redis) |
| GET | `/api/v1/matches` | List matches (filterable) |
| GET | `/api/v1/matches/live` | Live matches only |
| GET | `/api/v1/matches/{id}` | Match detail with events/stats |
| GET | `/api/v1/leagues` | All leagues |
| GET | `/api/v1/matches/{id}/ai-analysis` | AI analysis for a match |
| GET | `/api/v1/matches/{id}/streams` | Stream resolution |

## Configuration

Key environment variables (see `.env.example`):

| Variable | Default | Description |
|----------|---------|-------------|
| `DATABASE_URL` | `postgresql+asyncpg://localhost:5432/ai_football_live` | PostgreSQL connection |
| `REDIS_URL` | `redis://localhost:6379` | Redis connection |
| `AI_PROVIDER` | `mock` | AI provider: `mock` or `groq` |
| `GROQ_API_KEY` | (empty) | Groq API key |
| `GROQ_MODEL` | `openai/gpt-oss-120b` | Groq model ID |
| `AI_TEMPERATURE` | `0.3` | AI generation temperature |
| `AI_TIMEOUT_SECONDS` | `30` | AI request timeout |

## AI Analysis Pipeline

```
Match Data
    ↓
DeterministicAnalysisEngine (factual metrics extraction)
    ↓
AIContextBuilder (system prompt + context JSON)
    ↓
AIProvider.generate() (Groq API or Mock)
    ↓
AIOutputValidator
    ├── Structure validation (JSON, required fields)
    ├── Source validation (scores, teams, stats)
    └── Hallucination detection (regex score extraction)
    ↓
Validated AIAnalysis
```

## Testing

```bash
# Backend (67 tests)
cd ai_football_live_backend
pytest -q

# Flutter (47 tests)
cd ai_football_live
flutter test
flutter analyze
```

## Security

- API keys stored in environment variables only
- `.env` files excluded from version control
- No secrets in source code, Dockerfiles, or documentation
- AI output validated against source data to prevent hallucination
- Authorized streams only — no piracy or DRM bypass
- CORS configurable via `CORS_ORIGINS` environment variable

## License

Private — AI Football Live
