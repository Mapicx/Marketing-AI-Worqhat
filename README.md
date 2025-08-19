# TechNeeti

A hybrid AI platform for **personalized marketing, promotions, and loyalty**—from audience research to predictive analytics—backed by a workflow‑driven AI automation layer and classic ML models. It ships with a FastAPI backend, a modern React (Vite + TS + Tailwind) frontend, and opinionated workflows for image/slogan generation, report automation, and campaign forecasting.

> **Why it matters**: Teams can **research, simulate, A/B test, and forecast** campaign performance before spending a rupee—while staying mindful of **privacy, explainability, and edge cases**.

---

## 🔑 Problem Statement → Solution Mapping

| Rubric Item | How TechNeeti Addresses It |
| --- | --- |
| **Start with research** (identify target audiences & patterns) | `marketing_ai/data_loader.py` + `data_analysis.py` mine **campaign_history.csv, customers.csv, interactions.csv, products.csv**; cohorts & RFM‑style segments; intent and channel‑affinity discovery. |
| **Design data models for personalization** | `personalization_models.py` builds clustering (segmentation_model.pkl), feature scaling (scaler.pkl), and response‑propensity models (response_prediction_model.pkl). |
| **Simulate & A/B test ideas before launch** | `campaign_simulation.py` runs **counterfactual simulations** and **A/B variants** with uplift estimation; `edge_cases.py` stress‑tests atypical patterns. |
| **Predictive analytics (success metrics, ROI)** | `predictive_analytics.py` and `roi_forecast_model.pkl` generate **response lift, CPA/CAC, CLV deltas**, and **ROI forecasts**; visualizations exported to `/reports`. |
| **Address edge cases (privacy, atypical buying)** | Guardrails in `edge_cases.py`: privacy modes (PII minimization, hashing), anomaly handling, leakage checks, fairness checks across segments. |
| **Success metric: Business Creativity Thought Process Report** | `report_generator.py` renders a **Business Creativity Thought Process Report** highlighting methodical audience research & predictive modeling, and noting privacy considerations when missing. |

---

## 🏗️ Architecture Overview

```text
FastAPI (Backend)  ⇄  React/Vite (Frontend)
         ↓
Workflow‑driven AI APIs (generation, speech, document)  +  Local ML models (segmentation, response, ROI)
         ↓
RAG over YouTube transcripts for campaign insights
```

**Backend**
- **FastAPI** app (`backend/App/main.py`) exposes REST endpoints under `/api/*`.
- **Marketing AI** package (`backend/App/marketing_ai/*`) for data prep, simulation, analytics, reporting.
- **RAG** module (`backend/App/rag/youtube_rag.py`) extracts YouTube transcripts and builds a **LangChain** RAG index for Q&A.
- **Predictive models** live in `/models` and `backend/models` (PKL artifacts).

**Frontend**
- **React + Vite + TypeScript** with Tailwind; pages for **Dashboard, Forecast, Image Generator, Slogan Generator, YouTube Q&A**.

**Automation/Workflows Layer**
- Abstracted **AI workflows** for:
  1. **Image generation** for campaign creatives
  2. **Slogan generation** for ad copy
  3. **HTML → PDF** business reports
  4. **Text‑to‑Speech** for call automation *(future scope)*
  5. **Email automation** with multilingual support *(future scope)*
  6. **Containerized deployment** via Docker

> *Note*: The project leans heavily on a **composable workflow engine**—kept intentionally vendor‑agnostic here—so you can swap providers without changing product logic.

---

## 📂 Project Structure

```
TechNeeti/
├── requirements.txt
├── backend/
│   ├── App/
│   │   ├── main.py
│   │   ├── api/               # thin adapters for generation/report endpoints
│   │   ├── marketing_ai/      # data, simulation, analytics, reporting
│   │   ├── rag/               # YouTube transcript → RAG with LangChain
│   │   └── routes/            # FastAPI routers (img, slogan, predictive, rag)
│   ├── models/                # serialized pkl artifacts
│   └── reports/               # ready‑made visualizations & exports
├── data/                      # CSVs: customers, interactions, products, campaign history
├── frontend/                  # React + Vite + Tailwind UI
├── models/                    # shared model artifacts (CI/CD friendly)
└── reports/                   # generated reports & charts (html, pdf, png)
```

---

## 🔮 Core Capabilities

### 1) Audience Research & Insights
- Cohort discovery, RFM‑style scoring, channel‑affinity metrics
- Time‑series trends & seasonalities (response, conversion, ROI)
- Attribution‑aware KPIs (CTR, CVR, AOV, CAC, CLV proxy)

### 2) Personalization Models
- **Segmentation** (unsupervised clustering)
- **Response propensity** model for uplift targeting
- **Feature scaling/selection** pipelines baked into artifacts

### 3) Simulation & A/B Testing
- Run **multi‑variant** experiments pre‑launch
- **Counterfactual simulations** under budget and frequency caps
- **Edge case harness**: outliers, cold‑start, sparse categories

### 4) Predictive Analytics & ROI Forecasts
- Budget → **expected responses, revenue, profit, ROI**
- Sensitivity analysis; uncertainty bands
- Visual outputs to `/backend/reports` and `/reports`

### 5) Creative & Messaging Workflows
- **Image generation** for product/category campaigns
- **Slogan generation** (short/long‑form variants, tones, languages)
- **HTML → PDF**: one‑click **Business Creativity Thought Process Report**
- **TTS** & **Email automation** ready as plug‑ins *(behind feature flags)*

### 6) Knowledge‑Infused Assistant (RAG)
- **YouTube transcript ingestion** → chunking → embeddings
- **LangChain** index + FastAPI endpoint → **YouTubeQA** page in UI

---

## 🧪 Business Creativity Thought Process Report

The system autogenerates a report that:
- **Highlights**: methodical audience research, segmentation rigor, uplift/predictive modeling
- **Calls‑out**: if privacy handling wasn’t configured early enough (e.g., missing hashing/PII minimization)
- **Includes**: A/B setup, success metrics, forecast visuals, and edge‑case notes

Outputs are saved to:
- `backend/reports/business_creativity_report.html`
- `backend/reports/business_creativity_report.pdf`

---

## 🚦 Privacy, Safety & Edge‑Case Handling
- **Data minimization**: restrict PII, hash identifiers, drop free‑text PII by regex
- **Leakage checks**: strict train/test/temporal splits
- **Fairness & outliers**: per‑segment checks and robust scalers
- **Explainability**: feature importances and per‑segment diagnostics in reports
- **Governance**: config‑gated use of external AI APIs; audit logs for generation calls

---

## 🔌 API Surface (selected)

> Base: `http://localhost:8000`

| Endpoint | Method | Purpose |
| --- | --- | --- |
| `/api/slogan` | POST | Generate ad slogans (tone, language, length) |
| `/api/img` | POST | Generate promotional images |
| `/api/predictive/forecast` | POST | ROI & response forecasts |
| `/api/rag/youtube` | POST | RAG over YouTube transcripts & Q&A |

*(See `backend/App/routes/*` and `backend/App/api/*` for request/response schemas.)*

---

## 🖥️ Frontend Pages
- **Dashboard**: KPIs, segment summaries, latest forecasts
- **Forecast**: run predictive scenarios & view charts
- **Image Generator**: create creatives from prompts
- **Slogan Generator**: craft ad copy variants
- **YouTubeQA**: ask questions over campaign‑relevant videos

---

## ⚙️ Setup & Run

### Prerequisites
- Python 3.11+
- Node 18+ (or Bun), Docker (optional)

### 1) Backend
```bash
cd backend
python -m venv .venv && source .venv/bin/activate  # Windows: .venv\\Scripts\\activate
pip install -r ../requirements.txt
uvicorn App.main:app --host 0.0.0.0 --port 8000 --reload
```

### 2) Frontend
```bash
cd frontend
# with bun
bun install
bun dev
# or with npm
# npm install
# npm run dev
```

### 3) Environment Variables (example)
Create `.env` files where appropriate.
```
# Backend
GENERATION_API_KEY=xxxxxxxxxxxxxxxx
REPORT_WORKFLOW_URL=https://...
EMAIL_AUTOMATION_WEBHOOK=https://...   # future
TTS_WORKFLOW_URL=https://...            # future
MODEL_DIR=../models
```

---

## 🐳 Docker

Build and run the stack in containers:
```bash
# from project root
docker build -t techneeti-backend -f Dockerfile.backend ./backend
docker build -t techneeti-frontend -f Dockerfile.frontend ./frontend

docker run -d --name techneeti-api -p 8000:8000 \
  -e GENERATION_API_KEY=$GENERATION_API_KEY \
  techneeti-backend

docker run -d --name techneeti-web -p 5173:5173 techneeti-frontend
```
> Provide Dockerfiles as needed. The app is structured to be **12‑factor** friendly with env‑based config.

---

## ✅ Demo Flow (Suggested)
1. Upload or use provided CSVs in `/data` → run **Audience Research**.
2. Generate **segments** and **propensity scores**.
3. Use **Slogan** and **Image** workflows to create creatives.
4. Run **A/B simulation** with budget and frequency caps.
5. Generate **ROI forecast** and analyze sensitivity.
6. Export the **Business Creativity Thought Process Report** (HTML → PDF) and share.

---

## 📈 What Sets TechNeeti Apart
- **End‑to‑end**: research → simulate → decide → auto‑generate assets → report
- **Workflow‑first**: plug‑and‑play generation capabilities (images, text, documents, speech, email)
- **Measurable**: ROI & uplift forecasts with uncertainty bands
- **Responsible**: privacy‑first defaults, explainability, segment‑wise fairness checks
- **Practical**: RAG over real‑world video content for rapid domain grounding
- **Portable**: Dockerized, vendor‑agnostic workflows, clean FastAPI/React codebase

---

## 🛣️ Roadmap
- Enable **Text‑to‑Speech** for call automation
- **Multilingual email automation**& personalization
- Online **bandit‑style optimization** for live A/B rollouts
- Data‑source connectors (CDP, CRM, Ads platforms)

---

## 🤝 Contributing
PRs welcome. Please keep modules testable and deterministic. Avoid vendor lock‑in in core logic; add new workflow providers via adapters.

---

## License
MIT (or project‑specific) — update as required.

