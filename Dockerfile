# =============================================================
# Multi-stage build — LoL 2024 AI API
#
# Prerequisites (run on the host before building):
#   make dvc   →  pulls models/ and metadata/ via DVC
#
# Build:
#   docker compose build
#   docker compose up
# =============================================================

# ──────────────────────────────────────────────
# Stage 1 – builder: install Python dependencies
# ──────────────────────────────────────────────
FROM python:3.11-slim AS builder

WORKDIR /build

# System deps needed only to compile wheels
RUN apt-get update && \
    apt-get install -y --no-install-recommends build-essential && \
    rm -rf /var/lib/apt/lists/*

# PyTorch CPU-only (separate layer — changes rarely, benefits from cache)
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

COPY backend/requirements.txt ./requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# ──────────────────────────────────────────────
# Stage 2 – production: lean runtime image
# ──────────────────────────────────────────────
FROM python:3.11-slim AS production

WORKDIR /app

# Runtime system dep: curl for the health-check probe
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    rm -rf /var/lib/apt/lists/*

# Copy installed packages from builder (avoids compiler toolchain in the final image)
COPY --from=builder /usr/local/lib/python3.11 /usr/local/lib/python3.11
COPY --from=builder /usr/local/bin /usr/local/bin

# Non-root user — UID 1001 matches the host user to avoid volume permission issues
RUN useradd -m -u 1001 appuser && \
    mkdir -p logs && \
    chown -R appuser:appuser /app

# Application source
COPY --chown=appuser:appuser backend/app/ ./app/

# Model artefacts — already pulled locally via `make dvc`
# Only the files the API actually loads at inference time are included:
#   models/  →  neural-net weights + pre-game Random Forest
#   metadata/  →  JSON files with feature lists, scaler params, label encoders
# Training data (data/) and notebooks are intentionally excluded.
COPY --chown=appuser:appuser models/ ./models/
COPY --chown=appuser:appuser metadata/ ./metadata/

USER appuser

EXPOSE 8000

# Model loading can take a few seconds on first request — give it enough start time
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl --fail http://localhost:8000/health || exit 1

CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"]

# ──────────────────────────────────────────────
# Stage 3 – test: run backend pytest suite
# ──────────────────────────────────────────────
FROM builder AS test

WORKDIR /app

COPY backend/app/ ./app/
COPY backend/tests/ ./backend/tests/
COPY models/ ./models/
COPY metadata/ ./metadata/

ENV PYTHONPATH=/app
ENV CSV_PATH=data/2024_LoL_esports_match_data_from_OraclesElixir1.csv
ENV MODEL_DIR=models
ENV METADATA_DIR=metadata
ENV DEPLOYMENT_CRITERIA=app/config/deployment_criteria.yaml
ENV NN_MODEL_PATH=models/neural_net_v2.pth
ENV NN_METADATA_PATH=metadata/nn_metadata_v2.json
ENV PREGAME_MODEL_PATH=models/pregame_rf_v2.pkl
ENV PREGAME_METADATA_PATH=metadata/pregame_metadata_v2.json

CMD ["pytest", "backend/tests", "-q"]
