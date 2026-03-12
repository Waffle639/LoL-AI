# Multi-stage build for LoL 2024 AI API

# ==================== BASE STAGE ====================
FROM python:3.11-slim AS base

WORKDIR /app

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends curl && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Install PyTorch CPU-only first (large package, kept in its own layer)
# CPU-only variant is ~700 MB lighter than the default CUDA build
RUN pip install --no-cache-dir torch --index-url https://download.pytorch.org/whl/cpu

# Install remaining Python dependencies (separate layer for caching)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create non-root user with standard UID 1000
RUN useradd -m -u 1000 appuser && \
    mkdir -p data logs && \
    chown -R appuser:appuser /app

# ==================== PRODUCTION STAGE ====================
FROM base AS production

# DagsHub credentials passed at build time (never stored in final image)
ARG DAGSHUB_USER
ARG DAGSHUB_TOKEN

# Copy application code (includes app/config/deployment_criteria.yaml)
# --chown is required because COPY always runs as root, regardless of any USER instruction.
COPY --chown=appuser:appuser app/ ./app/

# Pull models and metadata from DagsHub via DVC
COPY .dvc/config .dvc/config
COPY models.dvc metadata.dvc ./
RUN dvc remote modify dagshub --local user "${DAGSHUB_USER}" && \
    dvc remote modify dagshub --local password "${DAGSHUB_TOKEN}" && \
    dvc pull models.dvc metadata.dvc && \
    rm -f .dvc/config.local && \
    chown -R appuser:appuser models/ metadata/

# Switch to non-root user
USER appuser

# Container always uses port 8000 internally
EXPOSE 8000

# Health check — model loading can take a few seconds, so start-period is generous
HEALTHCHECK --interval=30s --timeout=10s --start-period=30s --retries=3 \
    CMD curl --fail http://localhost:8000/health || exit 1

# Run application
CMD ["uvicorn", "app.api:app", "--host", "0.0.0.0", "--port", "8000"]
