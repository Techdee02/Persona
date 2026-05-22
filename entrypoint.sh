#!/usr/bin/env bash
# Persona API entrypoint — downloads vector store from DO Spaces if absent, then starts uvicorn.
set -euo pipefail

# ── Vector store: download from DO Spaces when path is set but file is missing ──
if [ -n "${DO_SPACES_BUCKET:-}" ] && [ -n "${VECTOR_STORE_PATH:-}" ] && [ ! -f "${VECTOR_STORE_PATH}" ]; then
    echo "INFO  Vector store not found at ${VECTOR_STORE_PATH}; downloading from DO Spaces ..."
    mkdir -p "$(dirname "${VECTOR_STORE_PATH}")"

    python3 - <<'PYEOF'
import boto3, os, sys

required = ["DO_SPACES_ENDPOINT", "DO_SPACES_KEY", "DO_SPACES_SECRET", "DO_SPACES_BUCKET"]
missing  = [v for v in required if not os.environ.get(v)]
if missing:
    print(f"ERROR  Missing DO Spaces env vars: {', '.join(missing)}", file=sys.stderr)
    sys.exit(1)

client = boto3.client(
    "s3",
    endpoint_url=os.environ["DO_SPACES_ENDPOINT"],
    aws_access_key_id=os.environ["DO_SPACES_KEY"],
    aws_secret_access_key=os.environ["DO_SPACES_SECRET"],
    region_name=os.environ.get("DO_SPACES_REGION", "nyc3"),
)

bucket = os.environ["DO_SPACES_BUCKET"]
key    = os.environ.get("DO_SPACES_VECTOR_STORE_KEY", "yelp_vector_store.json")
dest   = os.environ["VECTOR_STORE_PATH"]

size_mb = client.head_object(Bucket=bucket, Key=key)["ContentLength"] / 1_048_576
print(f"INFO  Downloading s3://{bucket}/{key} ({size_mb:.0f} MB) → {dest}", flush=True)

client.download_file(bucket, key, dest)
print("INFO  Download complete.", flush=True)
PYEOF

elif [ -n "${VECTOR_STORE_PATH:-}" ] && [ ! -f "${VECTOR_STORE_PATH}" ]; then
    echo "WARNING  VECTOR_STORE_PATH=${VECTOR_STORE_PATH} does not exist and DO_SPACES_BUCKET is not set."
    echo "WARNING  API will start with an empty vector store."
fi

# ── Start API ──
exec uvicorn backend.app:app --host 0.0.0.0 --port 8000 --workers 1
