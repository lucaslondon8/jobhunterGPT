# JobHunterGPT

> **AI‑powered job search assistant** that analyzes your CV, scrapes fresh roles, ranks them by fit, and spits out tailored cover‑letters—all with a single command.

---

## Table of Contents

1. [Features](#features)
2. [Quick Start](#quick-start)
3. [Configuration](#configuration)
4. [Directory Layout](#directory-layout)
5. [API Reference](#api-reference)
6. [Frontend Dashboard](#frontend-dashboard)
7. [Roadmap](#roadmap)
8. [Contributing](#contributing)
9. [License](#license)

---

## Features

|  Area                       |  What it does                                                                                 |
| --------------------------- | --------------------------------------------------------------------------------------------- |
| **CV Analysis**             | Parses any résumé (plain‑text or PDF) and extracts skills, seniority, industries & keywords.  |
| **Job Discovery**           | Dynamic scrapers paginate job searches across multiple sites, while dedicated modules in `scraper/` target platforms like LinkedIn and Indeed. |
| **Adaptive Matching**       | Scores each job against the extracted CV profile to surface the strongest leads.              |
| **Cover‑Letter Generation** | Uses Cohere Llama‑3 via API — with a rate‑limited wrapper and Markdown templates as fallback. |
| **REST API**                | FastAPI server (`server.py`) exposes endpoints for stats, recent jobs, and pipeline triggers. |
| **React Dashboard**         | `frontend/` provides a lightweight Next.js UI: start scans, browse matches, track metrics.    |

---

## Quick Start

### 1 · Clone & install

```bash
# clone
git clone https://github.com/lucaslondon8/jobhunterGPT.git
cd jobhunterGPT

# create virtual env (Python 3.9 +)
python -m venv .venv
source .venv/bin/activate

# install backend deps
pip install -r requirements.txt
```

### 2 · Set secrets

Create a `.env` in the project root:

```env
COHERE_API_KEY=your‑cohere‑key
```

(Add any other keys your custom scrapers need.)

### 3 · Add your CV

Drop a plain‑text résumé into ``. PDF? Copy/paste the raw text for now.

### 4 · Run the pipeline

```bash
python main.py            # CLI mode – scrape → match → generate → CSV
```

Results land in `output/jobs.csv` and `output/cover_letters/`.
Each run gathers up to `max_jobs` postings per site, following pagination when available.

### 5 · Spin up the API (optional)

```bash
uvicorn server:app --reload  # http://localhost:8000/docs
```

### 6 · Launch the dashboard (optional)

```bash
cd frontend
npm install
npm run dev                 # http://localhost:3000
```

---

## Configuration

All knobs live in ``:

```python
Config.scraper_config     # pages, timeouts, headers…
Config.matcher_config     # scoring weights
Config.email_config       # SMTP details if you automate outreach
Config.api_limits         # Cohere rate‑limits & caps
```

You can also override paths (output, logs, etc.) or point to a different résumé file.

---

## Directory Layout

```
jobhunterGPT/
├── api/                # (optional) REST helpers & auth
├── assets/             # sample CVs, images, prompts
├── frontend/           # React / Next.js dashboard
├── matcher/            # TF‑IDF + rule‑based matchers
├── scraper/            # dynamic & site-specific scrapers
├── output/             # CSVs, cover letters, logs
├── main.py             # orchestrates the full pipeline
├── server.py           # FastAPI entry‑point
├── requirements.txt    # Python deps
└── config.py           # central config object
```

---

## API Reference

Start the server and open `` for interactive Swagger. Key endpoints:

|  Method  |  Path                  |  Description                                     |
| -------- | ---------------------- | ------------------------------------------------ |
| `GET`    | `/api/stats`           | Dashboard KPIs (apps sent, response‑rate …).     |
| `GET`    | `/api/jobs?limit=20`   | Top‑ranked jobs with match scores.               |
| `POST`   | `/api/start-scan`      | Kick off the scrape → match → generate pipeline. |
| `GET`    | `/api/pipeline-status` | Poll for long‑running scan status.               |
| `POST`   | `/api/apply-job/{id}`  | Mark a job as applied (updates CSV).             |

---

## Frontend Dashboard

The React app polls the API and visualises:

- Real‑time pipeline progress
- Match score histograms
- Cover‑letter previews

> **Prod deploy tip:** add your domain to CORS in `server.py` and create a Vercel/Netlify build for the `frontend/` directory.

---

## Roadmap

-

---

## Contributing

Pull requests welcome! Please:

1. Fork → feature branch → PR.
2. Follow `black` & `ruff` linting.
3. Describe your change and link the related issue.

---

## License

[MIT](LICENSE) © 2025 Lucas Rizzo

