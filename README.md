<div align="center">
  <img width="400" alt="LoL AI Prediction" src="https://github.com/user-attachments/assets/7ba83f6d-afd9-4650-9b2d-4c2c87e7f01e" />

  <h1>League of Legends Esports — AI Match Prediction API</h1>

  <p>
    REST API powered by machine learning that predicts the outcome of professional League of Legends matches using 2024 competitive data.<br/>
    Includes user authentication, API key management, credit billing via Stripe, and full ML pipeline infrastructure.
  </p>

  <img src="https://img.shields.io/badge/Python-3.13+-blue?logo=python&logoColor=white"/>
  <img src="https://img.shields.io/badge/FastAPI-0.115+-green?logo=fastapi&logoColor=white"/>
  <img src="https://img.shields.io/badge/PyTorch-2.x-orange?logo=pytorch&logoColor=white"/>
  <img src="https://img.shields.io/badge/Stripe-Billing-635BFF?logo=stripe&logoColor=white"/>
  <img src="https://img.shields.io/badge/SQLite-Database-003B57?logo=sqlite&logoColor=white"/>
</div>

---

## Overview

This project exposes a production-ready API that allows any client to send a match snapshot — either pre-game or mid-game — and receive a win probability prediction in real time. It handles the full lifecycle: user registration, API key generation, prediction requests, and credit consumption tracked per call. Payments and credit top-ups are managed via Stripe Checkout.

The ML backend combines three models trained on 12,000+ rows of professional play: a Random Forest for pre-game composition analysis, a PyTorch neural network for deep pre-game prediction, and an SGD classifier for live in-game state.

---

## Tech Stack

<div align="center">
  <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg" width="48" alt="Python"/>
  <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/pandas/pandas-original.svg" width="48" alt="Pandas"/>
  <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/numpy/numpy-original.svg" width="48" alt="NumPy"/>
  <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/matplotlib/matplotlib-original.svg" width="48" alt="Matplotlib"/>
  <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/scikitlearn/scikitlearn-original.svg" width="48" alt="scikit-learn"/>
  <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/pytorch/pytorch-original.svg" width="48" alt="PyTorch"/>
  <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/fastapi/fastapi-original.svg" width="48" alt="FastAPI"/>
  <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/sqlite/sqlite-original.svg" width="48" alt="SQLite"/>
  <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/jupyter/jupyter-original.svg" width="48" alt="Jupyter"/>
</div>

<br/>
<div align="center">

| Layer | Technology |
|:---|:---|
| **API Framework** | FastAPI + Uvicorn |
| **ML Models** | scikit-learn (RandomForest, SGD), PyTorch |
| **Data** | pandas, NumPy |
| **Visualization** | Matplotlib, Seaborn |
| **Database** | SQLite — users, API keys, credit ledger |
| **Auth** | Hashed API keys (bcrypt / SHA-256) |
| **Billing** | Stripe Checkout + Webhooks |
| **Environment** | Python 3.13+, Jupyter Notebooks |

</div>

---
## Dataset

- **Source**: [League of Legends 2024 Competitive Game Dataset — Kaggle](https://www.kaggle.com/datasets/barthetur/league-of-legends-2024-competitive-game-dataset)
- **Rows**: 12,276 player records from professional matches
- **Teams**: 253 professional teams across all major regions
- **Players**: 1,305 unique players
- **Champions**: 147 different champions

Each row represents one player's performance in one game, containing pre-game metadata (team, champion, side, position) and in-game outcomes (kills, gold, objectives, towers).

---

## API Endpoints

### Authentication — `POST /account/register` · `POST /account/login`

Create an account or log in to retrieve your API key. All prediction and billing endpoints require the key in the `X-API-Key` header.

<div align="center">
  <img width="600" alt="Register and Login UI" src="https://github.com/user-attachments/assets/06b54187-152f-4e12-b69a-0e1a5415f445" />
</div>

---
### Prediction — `POST /predict`

Send a full player/team snapshot and receive a win probability. Each successful call consumes 1 credit.
```http
POST /predict
X-API-Key: lol_xxxxxxxxxxxx
Content-Type: application/json

{
  "team_encoded": 42,
  "player_encoded": 130,
  "champion_encoded": 7,
  "side_encoded": 0,
  "position_encoded": 2,
  "team_winrate": 0.65,
  "player_winrate": 0.58,
  "player_kda": 3.2,
  "champion_winrate": 0.52,
  "player_champ_winrate": 0.71,
  "kills": 5, "deaths": 2, "assists": 8,
  "teamkills": 25, "teamdeaths": 10,
  "dragons": 3, "opp_dragons": 1,
  "elders": 1, "opp_elders": 0,
  "barons": 2, "opp_barons": 0,
  "towers": 9, "opp_towers": 3,
  "totalgold": 15000
}
```
```json
{
  "result_label": "Victory",
  "prediction": 1,
  "probability": 0.8732,
  "model_version": "1.0.0",
  "credits_remaining": 19
}
```

---

### Credits — `GET /billing/credits`

Check how many prediction credits remain on your account.
```http
GET /billing/credits
X-API-Key: lol_xxxxxxxxxxxx
```
```json
{
  "name": "username",
  "credits_remaining": 18
}
```

---
### Top-Up — `GET /billing/checkout`

Redirects to a Stripe Checkout session to purchase additional credit bundles. On payment success, a webhook automatically credits the account.
```http
GET /billing/checkout
X-API-Key: lol_xxxxxxxxxxxx
```
```json
{
  "checkout_url": "https://checkout.stripe.com/pay/cs_live_..."
}
```

---
### Payment Success — `GET /success`

Landing page shown after completed Stripe payment confirming credits have been added.

<div align="center">
  <img width="500" alt="Payment success page" src="https://github.com/user-attachments/assets/f597886a-4e1c-4ca9-8126-e2108563656e" />
</div>

---
## Quick Start
```bash
pip install -r requirements.txt

# Train models
py -m app.train

# Start API
uvicorn app.api:app --reload
```

---

## Real Match Example

**G2 Esports vs MAD Lions KOI** · `LOLTMNT05_13119`
```
G2 ESPORTS (Blue side)          MAD LIONS KOI (Red side)
BrokenBlade  — K'Sante (top)    Myrwn      — Gwen (top)
Yike         — Vi (jng)         Elyoya     — Viego (jng)
Caps         — Azir (mid)       Fresskowy  — Neeko (mid)
Hans Sama    — Varus (bot)      Supa       — Ashe (bot)
Mikyx        — Zyra (sup)       Alvaro     — Renata Glasc (sup)

→ Model prediction:  G2 77.8% — MAD 22.2%
→ Actual winner:     G2 Esports ✓
```

---

## Notebooks

The three Jupyter notebooks document the full ML experimentation behind the API models.

| Notebook | Model | Description |
|---|---|---|
| `IA_LoL_Prediccion_Pre_Game.ipynb` | RandomForestClassifier | Pre-game prediction using team winrates, player KDA, champion mastery. 200 trees, max_depth 15. |
| `IA_LoL_NeuralNetwork.ipynb` | PyTorch Neural Network | Pre-game via deep learning. Architecture 24→64→32→1, dropout 0.2, Adam optimizer. |
| `IA_LoL.ipynb` | SGDClassifier | In-game prediction from live stats: kills, gold, objectives, towers. 70/30 split. |
