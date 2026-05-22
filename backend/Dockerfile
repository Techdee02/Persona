FROM python:3.12-slim

WORKDIR /app

# Copy requirements first so pip layer is cached unless dependencies change
COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy the full repo (build context is repo root)
COPY . .

ENV PYTHONUNBUFFERED=1

CMD ["uvicorn", "backend.app:app", "--host", "0.0.0.0", "--port", "8000"]
