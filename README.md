<p align="center">
  <img src="frontend/static/pricehound-logo.png" alt="PriceHound Logo" width="120" height="120">
</p>

<h1 align="center">PriceHound</h1>

<p align="center">
  <strong>Get a sense of your Datadog costs before you commit.</strong>
</p>

<p align="center">
  <img src="https://img.shields.io/badge/Datadog-632CA6?style=for-the-badge&logo=datadog&logoColor=white" alt="Datadog">
  <img src="https://img.shields.io/badge/FastAPI-009688?style=for-the-badge&logo=fastapi&logoColor=white" alt="FastAPI">
  <img src="https://img.shields.io/badge/SvelteKit-FF3E00?style=for-the-badge&logo=svelte&logoColor=white" alt="SvelteKit">
  <img src="https://img.shields.io/badge/Redis-DC382D?style=for-the-badge&logo=redis&logoColor=white" alt="Redis">
</p>

---

## ✨ Features

### 📊 Build Your Quote

- **Smart Product Search** — Quickly find any Datadog product from 100+ options with instant search
- **Multi-Region Support** — Switch between US, US1-FED (Government), EU, AP1, AP2, and more with accurate regional pricing
- **Pro/Enterprise Filtering** — Filter products by plan tier to see only relevant options
- **Flexible Billing** — Compare Annual, Monthly, and On-Demand pricing side by side
- **Real-time Calculations** — Watch totals update instantly as you build your quote
- **Allotment Tracking** — Automatically displays included allotments (scraped from [Datadog's allotments page](https://www.datadoghq.com/pricing/allotments/))

### 🚀 Quick Start Templates

Pre-built quote templates to jumpstart your estimates:
- **E-commerce Website** — RUM, Session Replay, APM, DBM, Logs & Synthetic Tests (1M sessions/month)
- **API Backend on Kubernetes** — Infrastructure, Containers, APM, Logs, Cloud Network & Profiler
- **Serverless AWS Architecture** — Lambda, Data Streams, RDS, Logs, On-Call & CI Visibility

### 🔗 Share & Protect

- **Public URLs** — Generate shareable links to collaborate on quotes (30-day retention)
- **Password Protection** — Lock quotes with a password to prevent unauthorized edits
- **Clone & Fork** — Anyone can clone a shared quote to create their own version
- **Edit Mode** — Unlock protected quotes with the password to make changes
- **Quote Descriptions** — Add notes and context to your quotes

### 📄 Export & Print

- **PDF Export** — Print-optimized light theme for professional documents
- **Clean Output** — Buttons and UI elements hidden in print view
- **Copy to Clipboard** — Quick copy of quote URLs for easy sharing

### 📈 Log Indexing Estimator

Built-in calculator for log management costs:
- **Volume-based Estimates** — Input ingestion volume and average log size
- **Retention Options** — Compare 3, 7, 15, and 30-day retention costs
- **Indexing Presets** — Quick presets for common use cases (Minimal, Standard, Extended, Compliance)
- **Flex Logs Support** — Add Flex Logs Starter or Storage with compute pricing notes
- **Log Forwarding** — Forwarding to Amazon S3, Azure Storage, and Google Cloud Storage is included at no extra charge; the estimator can add **custom** destination forwarding (paid per GB) when needed

### 📊 Cost Insights

- **Cost Distribution Chart** — Visual pie chart breakdown by product category
- **Sticky Summary Footer** — Always-visible cost summary when scrolling
- **Annual/Monthly Comparison** — Quick toggle between billing periods

### 🎨 User Experience

- **Guided Tour** — Interactive onboarding for new users (powered by driver.js)
- **Dark/Light Mode** — Toggle between themes with persistent preference
- **Smooth Animations** — Fade and slide transitions throughout the interface
- **Responsive Design** — Works beautifully on desktop and mobile
- **Auto-sync Pricing** — Hourly background sync keeps pricing data fresh
- **FAQ Page** — Common questions answered

### 📈 Observability

- **Datadog RUM** — Real User Monitoring for frontend performance
- **OTLP Logging** — Backend logs shipped directly to Datadog (no agent required)

---

## 🖼️ Screenshots

<details>
<summary>Click to expand</summary>

### Main Quote Builder
Build quotes with real-time pricing calculations and allotment tracking.

### Shared Quote View
Clean, read-only view for sharing with stakeholders.

### Log Indexing Estimator
Calculate log costs with visual breakdowns.

</details>

---

## 🚀 Getting Started

### Prerequisites

- Python 3.10+
- Node.js 18+
- Redis (optional, falls back to file storage)

### Quick Start

**One-command startup (recommended):**

```bash
# Clone and run
git clone https://github.com/toomone/pricehound.git
cd pricehound
./run.sh
```

The `run.sh` script automatically sets up virtual environments, installs dependencies, and starts both services.

**Manual setup:**

```bash
# Backend setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8000

# Frontend setup (new terminal)
cd frontend
npm install
npm run dev
```

### Access the Application

| Service | URL |
|---------|-----|
| Frontend | http://localhost:5173 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |

---

## 📖 Usage Guide

### Building a Quote

1. **Select Region** — Choose your Datadog region (US, EU, AP1, AP2)
2. **Add Products** — Search and select products, specify quantities
3. **Review Allotments** — See included resources automatically displayed
4. **Compare Pricing** — Toggle billing types to compare costs
5. **Save & Share** — Generate a public URL, optionally with password protection

### Using Templates

1. Click **"or stack example"** next to Add Product
2. Select a template (Website, IoT, Kubernetes)
3. Template items are added to your existing quote
4. Customize quantities as needed

### Protecting Your Quote

1. When saving, enter an optional password
2. Share the URL — anyone can view but not edit
3. To edit: click Unlock, enter password, make changes

---

## 🔌 API Reference

### Health & Status

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/health` | Health check endpoint |

### Products & Pricing

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/products` | List all products for a region |
| GET | `/api/pricing` | Get full pricing data |
| POST | `/api/pricing/sync` | Force sync from Datadog |
| GET | `/api/regions` | List available regions |
| GET | `/api/allotments` | Get allotment mappings (auto-scraped from Datadog) |

### Quotes

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/quotes` | Create a new quote |
| GET | `/api/quotes/{id}` | Get quote by ID |
| PUT | `/api/quotes/{id}` | Update quote (password required if protected) |
| POST | `/api/quotes/{id}/verify-password` | Verify quote password |

### Templates

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/templates` | List all templates |
| GET | `/api/templates/{id}` | Get template by ID |
| POST | `/api/templates/seed` | Re-sync templates from files |

---

## 🏗️ Architecture

```
ddog-pricing-calculator/
├── backend/
│   ├── app/
│   │   ├── main.py              # FastAPI application & routes
│   │   ├── models.py            # Pydantic models
│   │   ├── scraper.py           # Datadog pricing scraper
│   │   ├── allotments_scraper.py # Allotments data scraper
│   │   ├── quotes.py            # Quote CRUD operations
│   │   ├── templates.py         # Template management
│   │   ├── redis_client.py      # Redis connection & utilities
│   │   ├── config.py            # Environment configuration
│   │   └── telemetry.py         # OTLP logging to Datadog
│   ├── data/
│   │   ├── pricing/             # Cached pricing by region
│   │   ├── quotes/              # Stored quotes (file fallback)
│   │   └── templates/           # Template JSON files
│   ├── tests/                   # Pytest test suite
│   └── requirements.txt
├── run.sh                       # One-command dev startup
├── frontend/
│   ├── src/
│   │   ├── lib/
│   │   │   ├── components/      # Svelte components
│   │   │   │   ├── GuidedTour.svelte        # Interactive onboarding
│   │   │   │   ├── CostDistributionChart.svelte  # Pie chart
│   │   │   │   ├── LogsIndexingCalculator.svelte # Log estimator
│   │   │   │   └── ui/          # shadcn-svelte components
│   │   │   ├── api.ts           # API client
│   │   │   └── utils.ts         # Utility functions
│   │   └── routes/
│   │       ├── +page.svelte     # Main calculator
│   │       ├── faq/             # FAQ page (markdown)
│   │       └── quote/[id]/      # Shared quote view
│   └── static/                  # Static assets
└── render.yaml               # Render deployment config
```

---

## 🛠️ Tech Stack

### Backend
- **[FastAPI](https://fastapi.tiangolo.com/)** — High-performance Python web framework
- **[Redis](https://redis.io/)** — In-memory data store (optional)
- **[Pydantic](https://pydantic.dev/)** — Data validation & serialization
- **[BeautifulSoup4](https://www.crummy.com/software/BeautifulSoup/)** — HTML parsing for price scraping
- **[APScheduler](https://apscheduler.readthedocs.io/)** — Background job scheduling

### Frontend
- **[SvelteKit](https://kit.svelte.dev/)** — Full-stack Svelte framework
- **[shadcn-svelte](https://www.shadcn-svelte.com/)** — Beautiful UI components
- **[Tailwind CSS](https://tailwindcss.com/)** — Utility-first CSS
- **[TypeScript](https://www.typescriptlang.org/)** — Type-safe JavaScript
- **[mode-watcher](https://github.com/svecosystem/mode-watcher)** — Dark mode support
- **[driver.js](https://driverjs.com/)** — Guided tour/onboarding
- **[layerchart](https://layerchart.com/)** — Charting library
- **[@datadog/browser-rum](https://docs.datadoghq.com/real_user_monitoring/)** — Real User Monitoring

### Deployment
- **[Render](https://render.com/)** — Cloud hosting platform
- Infrastructure as Code via `render.yaml`

---

## 🚢 Deployment

### Render (Recommended)

The project includes a `render.yaml` Blueprint for easy deployment:

1. Fork this repository
2. Connect to Render
3. Create a new Blueprint instance
4. Select your fork — services auto-configure

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `STORAGE_TYPE` | `redis` or `file` | `file` |
| `REDIS_URL` | Redis connection string | — |

#### Datadog OTLP Logging (Optional)

Ship application logs directly to Datadog without an agent:

| Variable | Description | Default |
|----------|-------------|---------|
| `DD_API_KEY` | Datadog API key (required for OTLP) | — |
| `DD_SITE` | Datadog site (`datadoghq.com`, `datadoghq.eu`, etc.) | `datadoghq.com` |
| `DD_SERVICE` | Service name in Datadog | `pricehound` |
| `DD_ENV` | Environment tag | `production` |
| `DD_VERSION` | Version tag | `1.0.0` |

If `DD_API_KEY` is not set, OTLP logging is disabled and logs only go to console.

#### Datadog RUM (Frontend)

| Variable | Description | Default |
|----------|-------------|---------|
| `PUBLIC_DD_ENV` | RUM environment tag (`dev` or `prod`) | `prod` |

RUM is pre-configured with the application ID and client token. Set `PUBLIC_DD_ENV=dev` for local development.

---

## 🧪 Development

### Running Tests

```bash
cd backend
source venv/bin/activate
pytest
```

The test suite covers:
- API endpoints (`test_main.py`)
- Quote operations (`test_quotes.py`)
- Pricing scraper (`test_scraper.py`)
- Allotment logic (`test_allotments.py`)

---

## 📄 License

MIT

---

## ⚠️ Disclaimer

This is an **unofficial tool** and is not affiliated with, endorsed by, or sponsored by Datadog, Inc. Pricing data is scraped from Datadog's public pricing page and may not reflect the most current or accurate pricing. Always verify pricing directly with Datadog for official quotes.

---

<p align="center">
  Made with ❤️ for the Datadog community
</p>
