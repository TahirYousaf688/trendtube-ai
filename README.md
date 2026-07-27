# TrendTube AI 🚀

**AI-Powered YouTube Content Factory**

TrendTube AI is a production-ready SaaS platform that automatically discovers trending topics, creates high-quality videos using AI, and publishes them to YouTube. Built with a modular, cloud-native architecture designed to scale to millions of users.

## ✨ Features

### 🤖 AI Agents (12 Specialized Agents)
- **Trend Agent** - Discovers trending topics across 13+ sources
- **Research Agent** - Gathers and synthesizes reliable information
- **Fact Checker Agent** - Verifies claims and detects misinformation
- **Script Writer Agent** - Creates engaging YouTube scripts in 7 styles
- **Voice Agent** - Generates natural narration (ElevenLabs, Azure, Google, OpenAI)
- **Thumbnail Agent** - Designs high-CTR thumbnails with A/B testing
- **SEO Agent** - Optimizes titles, descriptions, tags, and chapters
- **Video Editor Agent** - Composes final video with effects and captions
- **Publisher Agent** - Uploads and schedules to YouTube
- **Analytics Agent** - Tracks views, CTR, watch time, and revenue
- **Recommendation Agent** - Suggests content improvements
- **Monetization Agent** - Optimizes revenue and sponsorships

### 📊 Content Types
News | Technology | AI | Finance | Cryptocurrency | Stock Market | Education | Programming | Sports | Gaming | Business | Politics | Science | Health | Travel | Documentary | Product Reviews

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Frontend (Next.js + TS)                   │
│               Dashboard · Analytics · Admin                  │
├─────────────────────────────────────────────────────────────┤
│                    API Gateway (Nginx)                       │
├─────────────────────────────────────────────────────────────┤
│                    Backend (FastAPI + Python)                │
│   Auth · Users · Channels · Trends · Research · Scripts     │
│   Videos · Assets · Thumbnails · SEO · Analytics · Billing  │
├───────────────────┬─────────────────────┬───────────────────┤
│   AI Orchestration │    Task Queue       │   Storage         │
│   (LangGraph)      │    (Celery/RabbitMQ)│   (AWS S3)        │
├───────────────────┴─────────────────────┴───────────────────┤
│            PostgreSQL · Redis · ChromaDB/Pinecone            │
└─────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites
- Python 3.12+
- Node.js 20+
- Docker & Docker Compose
- PostgreSQL 16
- Redis 7

### Backend Setup

```bash
# Clone and install dependencies
pip install -r requirements.txt

# Set up database
psql -U postgres -c "CREATE DATABASE trendtube;"
psql -d trendtube -f backend/app/db/init.sql

# Run migrations
alembic upgrade head

# Start development server
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload --app-dir backend
```

### Frontend Setup

```bash
cd frontend
npm install
npm run dev
```

### Docker Deployment

```bash
docker compose up -d
```

Visit `http://localhost:8000/docs` for API documentation and `http://localhost:3000` for the dashboard.

## 📚 API Documentation

The API is documented with OpenAPI/Swagger at `/docs` when running in development mode.

### Key Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/v1/auth/register` | Register new user |
| POST | `/api/v1/auth/login` | Login |
| GET | `/api/v1/trends` | List trending topics |
| POST | `/api/v1/videos/generate` | Generate video |
| GET | `/api/v1/analytics/summary` | Analytics overview |
| POST | `/api/v1/billing/subscribe` | Subscribe to plan |

## 🐳 Docker Commands

```bash
# Build and start all services
docker compose up -d

# View logs
docker compose logs -f api

# Run tests
docker compose exec api pytest

# Stop all services
docker compose down
```

## ☸️ Kubernetes Deployment

```bash
kubectl apply -f k8s/
kubectl get pods -w
```

## 🧪 Testing

```bash
# Backend tests
pytest backend/app/tests -v --cov=backend/app

# With Docker
docker compose exec api pytest
```

## 🔧 Configuration

Configuration via environment variables (see `backend/app/core/config.py`):

```bash
# Core
DATABASE_URL=postgresql+psycopg2://user:pass@localhost:5432/trendtube
REDIS_URL=redis://localhost:6379/0
JWT_SECRET=your-secret-key

# AI/LLM
OPENAI_API_KEY=sk-...
ANTHROPIC_API_KEY=sk-...

# YouTube
YOUTUBE_API_KEY=...
YOUTUBE_CLIENT_ID=...

# Voice
ELEVENLABS_API_KEY=...

# Payments
STRIPE_SECRET_KEY=sk_...
PAYPAL_CLIENT_ID=...
```

## 📊 Monitoring

- **Prometheus** - Metrics collection at `/metrics`
- **Grafana** - Dashboards at port 3001
- **Structured Logging** - JSON-formatted logs

## 🔒 Security

- JWT-based authentication with refresh tokens
- OAuth 2.0 (Google Login)
- Role-Based Access Control (Admin, Creator, Member, Viewer)
- API key authentication for programmatic access
- Rate limiting on all endpoints
- Input validation with Pydantic
- Audit logging for all actions
- Encrypted secrets management
- CORS and CSRF protection

## 💳 Subscription Plans

| Plan | Price | Features |
|------|-------|----------|
| Free | $0 | 3 videos/month, basic analytics |
| Creator | $29/mo | 30 videos, all AI features |
| Pro | $99/mo | 100 videos, A/B testing, priority support |
| Enterprise | $299/mo | Unlimited, API access, custom workflows |

## 🎯 Target Users

- YouTubers & Digital Marketers
- Media Companies & News Agencies
- Finance & Education Creators
- Technology & AI Content Creators
- Businesses & Influencers

## 📁 Project Structure

```
trendtube-ai/
├── backend/
│   └── app/
│       ├── api/routes/        # 17 API route modules
│       ├── core/              # Config, security, database
│       ├── db/                # SQL schema and base model
│       ├── models/            # 30+ SQLAlchemy models
│       ├── schemas/           # 50+ Pydantic schemas
│       ├── services/
│       │   ├── agents/        # 12 AI agents
│       │   ├── tasks/         # Celery tasks
│       │   ├── ai_orchestrator.py
│       │   └── ai_workflow.py
│       ├── prompts/           # AI prompt templates
│       └── tests/             # Test suite
├── frontend/
│   └── app/                   # Next.js dashboard
├── k8s/                       # Kubernetes manifests
├── nginx/                     # Reverse proxy config
├── docs/                      # Documentation
└── docker-compose.yml         # Full stack deployment
```

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Open a Pull Request

## 📄 License

MIT License - see LICENSE file for details.

---

Built with ❤️ by the TrendTube AI Team

