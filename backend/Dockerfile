FROM python:3.12-slim

WORKDIR /app

# Install curl for the health-check probe
RUN apt-get update && apt-get install -y --no-install-recommends curl && rm -rf /var/lib/apt/lists/*

# Build context is the repo root (docker-compose sets context: .)
# Copy requirements first so pip layer is cached unless deps change.
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Bake the embedding model into the image so it loads instantly at runtime
# instead of downloading from HuggingFace on every cold start.
RUN python -c "from sentence_transformers import SentenceTransformer; SentenceTransformer('all-MiniLM-L6-v2')"

# Copy the full repo
COPY . .

# Make the startup entrypoint executable
RUN chmod +x /app/entrypoint.sh

ENV PYTHONUNBUFFERED=1

ENTRYPOINT ["/app/entrypoint.sh"]
