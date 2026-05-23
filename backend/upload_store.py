#!/usr/bin/env python3
"""
Upload the enriched Yelp vector store to DigitalOcean Spaces.

Reads credentials from environment variables (loaded from .env automatically).
Progress is printed every ~100 MB.

Usage (from repo root):
    python -m backend.upload_store
"""
from __future__ import annotations

import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
import boto3
from botocore.config import Config

load_dotenv()

ENDPOINT_URL = os.environ["DO_SPACES_ENDPOINT"]          # https://lon1.digitaloceanspaces.com
BUCKET_NAME  = os.environ["DO_SPACES_BUCKET"]            # persona-space
OBJECT_KEY   = os.environ["DO_SPACES_VECTOR_STORE_KEY"]  # yelp_vector_store_200k.jsonl
ACCESS_KEY   = os.environ["DO_SPACES_KEY"]
SECRET_KEY   = os.environ["DO_SPACES_SECRET"]
LOCAL_PATH   = Path("backend/data/yelp_vector_store_200k.jsonl")
REGION       = os.environ.get("DO_SPACES_REGION", "lon1")

if not LOCAL_PATH.exists():
    sys.exit(f"ERROR: {LOCAL_PATH} not found")

total_bytes = LOCAL_PATH.stat().st_size
uploaded    = 0
last_report = 0
start       = time.time()
REPORT_EVERY = 100 * 1024 * 1024  # 100 MB


def progress(chunk: int) -> None:
    global uploaded, last_report
    uploaded += chunk
    if uploaded - last_report >= REPORT_EVERY or uploaded >= total_bytes:
        pct  = uploaded / total_bytes * 100
        mb   = uploaded / 1_048_576
        tot  = total_bytes / 1_048_576
        rate = uploaded / (time.time() - start) / 1_048_576
        print(f"  {pct:5.1f}%  {mb:,.0f} / {tot:,.0f} MB  ({rate:.1f} MB/s)", flush=True)
        last_report = uploaded


s3 = boto3.client(
    "s3",
    endpoint_url=ENDPOINT_URL,
    aws_access_key_id=ACCESS_KEY,
    aws_secret_access_key=SECRET_KEY,
    config=Config(signature_version="s3v4"),
    region_name=REGION,
)

print(f"Uploading {LOCAL_PATH} ({total_bytes / 1_048_576:,.0f} MB) → {BUCKET_NAME}/{OBJECT_KEY}")
s3.upload_file(str(LOCAL_PATH), BUCKET_NAME, OBJECT_KEY, Callback=progress)
print(f"\nDone in {time.time() - start:.0f}s")
