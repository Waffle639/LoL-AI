<div align="center">
  <img width="420" alt="LoL AI Prediction" src="https://github.com/user-attachments/assets/7ba83f6d-afd9-4650-9b2d-4c2c87e7f01e" />

  <h1>League of Legends Esports - AI Match Prediction</h1>

  <p>
    From raw CSV to production API. Two ML models, a full data pipeline, DVC versioning,<br/>
    a React dashboard with a live champion picker, JWT auth, Stripe billing, all inside Docker.
  </p>

  <div>
    <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg" width="42" alt="Python"/>
    <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/pandas/pandas-original.svg" width="42" alt="Pandas"/>
    <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/numpy/numpy-original.svg" width="42" alt="NumPy"/>
    <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/pytorch/pytorch-original.svg" width="42" alt="PyTorch"/>
    <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/fastapi/fastapi-original.svg" width="42" alt="FastAPI"/>
    <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/react/react-original.svg" width="42" alt="React"/>
    <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/docker/docker-original.svg" width="42" alt="Docker"/>
    <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/sqlite/sqlite-original.svg" width="42" alt="SQLite"/>
  </div>
</div>

---

## Overview

This project is the result of an end-to-end machine learning workflow applied to **competitive League of Legends**.

I took a raw Kaggle dataset with 12,000+ player records, built a full **ETL pipeline**, trained and compared multiple models, wrapped the best two in a **FastAPI** service, and built a **React dashboard** where you can either paste live match stats or pick champions in a visual pre-game selector to get an instant win-probability prediction.

Everything is containerised with **Docker**, models are versioned with **DVC**, and the API ships with **JWT auth**, **API-key billing**, and **Stripe** credit top-ups.

---

## Tech Stack

| Layer | Technology |
|:---|:---|
| **API Framework** | FastAPI + Uvicorn |
| **ML Models** | scikit-learn (RandomForest), PyTorch Neural Network |
| **Data** | pandas, NumPy, Parquet |
| **Database** | SQLite / Supabase - users, API keys, credit ledger |
| **Auth** | JWT + hashed API keys + httpOnly refresh cookies |
| **Billing** | Stripe Checkout + Webhooks |
| **Model Versioning** | DVC + DagsHub |
| **Frontend** | React 18, Vite, anime.js, CSS Modules, Tailwind |
| **Container** | Docker multi-stage |
| **Orchestration** | GNU Make |

---

## Dataset

- **Source**: [League of Legends 2024 Competitive Game Dataset - Kaggle](https://www.kaggle.com/datasets/barthetur/league-of-legends-2024-competitive-game-dataset)
- **Rows**: 12,276 player records from professional matches
- **Teams**: 253 professional teams across all major regions
- **Players**: 1,305 unique pro players
- **Champions**: 147 different champions

---

## Screenshots

### Landing Page

Cinematic single-page experience with scroll-driven animations, HTML5 Canvas draft visualisation, and a dark esports aesthetic.

> [Insert landing page screenshot / GIF here]

### Dashboard - Predict Live

Fill 24 match fields (player identity + live stats) and get an instant win probability. Auto-fills historical performance when you select a team + player + champion.

> [Insert Predict Live screenshot here]

### Dashboard - Pre-Game

Visual champion selector inspired by the LoL client. Lock in 5 players per side, assign champions from a searchable grid with role filtering, and predict the winner before the match starts.

> [Insert Pre-Game screenshot here]

### Dashboard - Credits & Billing

Balance panel with animated progress bar, usage summary, and credit packs. Payments go through Stripe Checkout. On success, a webhook automatically updates your credit balance - no manual refresh needed.

> [Insert Billing screenshot here]

---

## Feature Engineering + Pipeline

Before training, I had to create a few extra historical features from the raw CSV to make the model more accurate, like `team_winrate`, `player_winrate`, `player_kda`, `champion_winrate`, and `player_champ_winrate`. The idea is simple: instead of relying only on the current match snapshot, the model also learns from past performance. Categoricals are encoded with sklearn LabelEncoders stored inside the model artifact.

**Data pipeline** (`backend/app/ml/pipeline.py`):

```
CSV (semicolon-separated)
  ↓
load_csv() → validation
  ↓
normalize_columns() → binary target
  ↓
create_splits() → stratified 60 / 20 / 20
  ↓
save_splits() → Parquet
```

**Why Parquet ?** Columnar, compressed, preserves types natively. Zero-friction hand-off via pandas + pyarrow.

---

## Models + Versioning

I trained and evaluated three model families. Two made it to production. Every training run produces a versioned pair (model file + JSON metadata). The script auto-increments versions by scanning the `models/` folder. Each JSON stores the full evaluation plus a `deployment_ready` flag.

Before reaching production, a model must pass `deployment_criteria.yaml`. If it fails, the version is saved but not promoted. When it passes, the script copies it to the production path and updates the metrics table in this README automatically.

### Neural Network - Live In-Game Prediction

24 features → 64 → 32 → 1, ReLU + Dropout(0.2), sigmoid output. Trained with BCELoss and Adam (lr 0.001) for 50 epochs, batch size 16. The checkpoint bundles weights, scaler, encoders, and feature names so inference is fully self-contained.

### Random Forest - Pre-Game Draft Prediction

200 trees, max depth 15, stratified 80/20 split. Uses only pre-game data (roster, champion picks, historical stats). The artifact stores the forest plus lookup tables so the pre-game endpoint resolves team names and retrieves winrates without touching the original CSV.

### Current Production Metrics

Updated automatically after each training run when the model passes the deployment quality gate.

<!-- METRICS_START -->
| Metric | Neural Network (v2) | Pre-Game RF (v2) |
|:---|:---:|:---:|
| Accuracy | 97.76% | 76.75% |
| F1 Score | 0.9781 | 0.7663 |
| ROC-AUC | 0.9968 | 0.8955 |
| Precision | 0.9731 | 0.7704 |
| Recall | 0.9832 | 0.7622 |
| Deployment Ready | ✅ | ✅ |

*Last updated: 2026-03-08*
<!-- METRICS_END -->

---

## DVC

The trained models, metadata, and raw data are versioned with DVC and stored in a DagsHub remote. That keeps the repo lightweight and makes the whole pipeline reproducible.

| File | Tracked by |
|:---|:---|
| `models/neural_net_vN.pth` | DVC → DagsHub |
| `models/pregame_rf_vN.pkl` | DVC → DagsHub |
| `metadata/*.json` | DVC → DagsHub |
| `data/*.csv` | DVC → DagsHub |

---

## Docker & DevEx

Multi-stage Dockerfile (builder → production → test). Only inference artefacts are copied into the production image; training data and notebooks are mounted as volumes or excluded.

```bash
make setup     # venv + deps
make dvc       # credentials + pull models
make start-all # API + landing + dashboard
make train     # both training pipelines
make docker-up # Docker Compose
```

---

## Quick Start

```bash
git clone <repo> && cd LoL-AI
dvc pull
cp .env.example .env
make setup
make start-all
```

Ports:
- API: `http://localhost:8000`
- Landing: `http://localhost:5173`
- Dashboard: `http://localhost:5174`

---

## Real Match Example

**G2 Esports vs MAD Lions KOI** - `LOLTMNT05_13119`

```
G2 ESPORTS (Blue side)          MAD LIONS KOI (Red side)
BrokenBlade - K'Sante (top)    Myrwn      - Gwen (top)
Yike        - Vi (jng)         Elyoya     - Viego (jng)
Caps        - Azir (mid)       Fresskowy  - Neeko (mid)
Hans Sama   - Varus (bot)      Supa       - Ashe (bot)
Mikyx       - Zyra (sup)       Alvaro     - Renata Glasc (sup)

→ Model prediction:  G2 77.8% - MAD 22.2%
→ Actual winner:     G2 Esports ✓
```

---

## Notebooks

The three Jupyter notebooks document the full ML experimentation behind the API models. Kept as the single source of truth for hyperparameters.

| Notebook | Model |
|:---|:---|
| `backend/notebooks/IA_LoL_Prediccion_Pre_Game.ipynb` | RandomForestClassifier - pre-game |
| `backend/notebooks/IA_LoL_NeuralNetwork.ipynb` | PyTorch Neural Network - in-game |
| `backend/notebooks/IA_LoL.ipynb` | SGDClassifier - early experimentation |

---

## Things You Might Miss

- **Auto-historical stats** - picking a team + player + champion auto-fills the form with real winrates from the 2024 dataset.
- **Canvas draft animation** - the landing page draws the draft UI on a 2D canvas with real champion icons from Riot Data Dragon.
- **Dual auth** - JWT for the dashboard, API keys for third-party scripts. Both coexist.
- **Secure refresh rotation** - refresh tokens in httpOnly cookies, rotated on every use. Revoke all sessions at once.
- **README that updates itself** - after `make train` the metrics table is rewritten from the production metadata JSONs.
- **Non-root Docker** - production container runs as UID 1001.
- **Rate limiting** - login attempts capped via slowapi.
- **Credit-aware** - every prediction costs 1 credit. Stripe webhooks auto-refill the ledger.

---

## License

MIT - feel free to fork, break, and rebuild.

> Built with PyTorch, FastAPI, React, and too many hours of watching LoL esports.
