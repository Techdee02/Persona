# Deployment Guide

Owner: Backend/DevOps  
Last updated: 2026-05-23

This guide covers deploying the full Persona stack (FastAPI backend + Nginx) to a
DigitalOcean Droplet with a free DuckDNS subdomain and Let's Encrypt SSL certificate.
The Vercel-hosted frontend talks to this backend over HTTPS.

---

## Architecture

```
Browser
  │
  ▼
Vercel (React frontend — HTTPS)
  │  VITE_API_URL
  ▼
https://personabackend.duckdns.org   ← DuckDNS free subdomain → 188.166.149.75
  │
  ▼
Nginx (port 443 → HTTP/2 → proxy_pass)
  │
  ▼
FastAPI / Uvicorn (port 8000, internal Docker network)
  │
  ▼
Vector store — /data/yelp_vector_store_200k.jsonl (Docker named volume)
  │  first boot only
  ▼
DigitalOcean Spaces (persona-space / lon1)
```

---

## Prerequisites

- DigitalOcean account with a **2 GB RAM droplet** (Ubuntu 22.04)
- DigitalOcean Spaces bucket containing `yelp_vector_store_200k.jsonl`
- Spaces API key with **Read** access
- OpenAI API key (`ENABLE_LLM=true` path)
- DuckDNS account (free at duckdns.org)
- Vercel project for the frontend

---

## Step 1 — Create the Droplet

1. Go to DigitalOcean → Create → Droplets
2. Image: **Ubuntu 22.04 LTS**
3. Size: **Basic → Regular → 2 GB RAM / 1 vCPU** (~$12/month)
4. Region: match your Spaces region (e.g. London `lon1`)
5. Authentication: paste your SSH public key
   ```bash
   # Generate one if you don't have it:
   ssh-keygen -t ed25519 -C "persona-deploy"
   cat ~/.ssh/id_ed25519.pub   # copy this into DigitalOcean
   ```
6. Create droplet — note the public IPv4 address

---

## Step 2 — DuckDNS (free HTTPS subdomain)

1. Go to [duckdns.org](https://www.duckdns.org) and sign in with GitHub
2. Enter a subdomain name (e.g. `personabackend`) and click **add domain**
3. Set the IP to your droplet's IPv4 address and click **update ip**
4. Your domain is now `personabackend.duckdns.org` → your droplet IP

DNS propagates within seconds.

---

## Step 3 — Connect and Install Docker

```bash
ssh root@<your-droplet-ip>
curl -fsSL https://get.docker.com | sh
```

---

## Step 4 — Clone the Repo

```bash
git clone https://github.com/Techdee1/Persona.git
cd Persona
```

---

## Step 5 — Configure Environment

Write `.env` directly (replace placeholder values):

```bash
cat > .env << 'ENVEOF'
DATASET_YELP_PATH=
DATASET_AMAZON_PATH=
DATASET_GOODREADS_PATH=
DETERMINISTIC_MODE=false
PROFILE_CACHE_TTL_SECONDS=3600
PROFILE_CACHE_MAX_SIZE=1000
ENABLE_LLM=true
OPENAI_API_KEY=<your-openai-api-key>
OPENAI_MODEL=gpt-4o
VECTOR_STORE_PATH=/data/yelp_vector_store_200k.jsonl
VECTOR_STORE_PATH_YELP=
VECTOR_STORE_PATH_AMAZON=
VECTOR_STORE_PATH_GOODREADS=
DO_SPACES_ENDPOINT=https://lon1.digitaloceanspaces.com
DO_SPACES_REGION=lon1
DO_SPACES_BUCKET=persona-space
DO_SPACES_KEY=<your-spaces-access-key>
DO_SPACES_SECRET=<your-spaces-secret-key>
DO_SPACES_VECTOR_STORE_KEY=yelp_vector_store_200k.jsonl
ALLOWED_ORIGINS=https://your-frontend.vercel.app
ENVEOF
```

**Never commit `.env` to git.** It is in `.gitignore`.

---

## Step 6 — SSL Certificate (Certbot)

Certbot needs nginx to be serving port 80 with the ACME challenge path before it
can issue a certificate. Do this in two steps.

### 6a. Write the temporary HTTP-only nginx config

```bash
cat > nginx/nginx.conf << 'EOF'
events { worker_connections 1024; }
http {
    upstream persona_api { server api:8000; keepalive 32; }
    server {
        listen 80;
        server_name personabackend.duckdns.org;
        location /.well-known/acme-challenge/ {
            root /var/www/certbot;
        }
        location / {
            proxy_pass http://persona_api;
            proxy_http_version 1.1;
            proxy_set_header Host $host;
            proxy_set_header X-Real-IP $remote_addr;
        }
    }
}
EOF
```

### 6b. Start the stack and issue the certificate

```bash
docker compose up -d
docker compose --profile certbot run --rm certbot certonly --webroot \
  -w /var/www/certbot -d personabackend.duckdns.org \
  --email your@email.com --agree-tos --non-interactive
```

Expected output:
```
Successfully received certificate.
Certificate is saved at: /etc/letsencrypt/live/personabackend.duckdns.org/fullchain.pem
This certificate expires on 2026-08-21.
```

### 6c. Write the full SSL nginx config

```bash
cat > nginx/nginx.conf << 'EOF'
events { worker_connections 1024; }
http {
    client_max_body_size 20M;
    proxy_read_timeout 120s;
    proxy_send_timeout 120s;
    keepalive_timeout 65s;
    upstream persona_api { server api:8000; keepalive 32; }
    server {
        listen 80;
        server_name personabackend.duckdns.org;
        location /.well-known/acme-challenge/ { root /var/www/certbot; }
        location / { return 301 https://$host$request_uri; }
    }
    server {
        listen 443 ssl;
        http2 on;
        server_name personabackend.duckdns.org;
        ssl_certificate     /etc/letsencrypt/live/personabackend.duckdns.org/fullchain.pem;
        ssl_certificate_key /etc/letsencrypt/live/personabackend.duckdns.org/privkey.pem;
        ssl_protocols       TLSv1.2 TLSv1.3;
        ssl_ciphers         ECDHE-ECDSA-AES128-GCM-SHA256:ECDHE-RSA-AES128-GCM-SHA256:ECDHE-ECDSA-AES256-GCM-SHA384:ECDHE-RSA-AES256-GCM-SHA384;
        ssl_prefer_server_ciphers off;
        ssl_session_cache   shared:SSL:10m;
        ssl_session_timeout 1d;
        location / {
            proxy_pass         http://persona_api;
            proxy_http_version 1.1;
            proxy_set_header   Host              $host;
            proxy_set_header   X-Real-IP         $remote_addr;
            proxy_set_header   X-Forwarded-For   $proxy_add_x_forwarded_for;
            proxy_set_header   X-Forwarded-Proto $scheme;
        }
    }
}
EOF
```

### 6d. Reload nginx

```bash
docker compose restart nginx
```

### 6e. Test

```bash
curl https://personabackend.duckdns.org/health
# Expected: {"status":"ok"}
```

---

## Step 7 — Point the Frontend at the Backend

In your Vercel project → **Settings → Environment Variables**:

```
VITE_API_URL = https://personabackend.duckdns.org
```

Then redeploy: **Deployments → three dots on latest → Redeploy**.

---

## Operational Commands

### Check status

```bash
cd Persona
docker compose ps
```

### View live logs

```bash
docker compose logs -f api          # API logs (requests, vector store load, errors)
docker compose logs -f nginx        # Nginx access logs
docker compose logs --tail=50 api   # Last 50 lines only
```

### Restart services

```bash
docker compose restart api      # Restart API only (fast, no rebuild)
docker compose restart nginx    # Reload nginx config
docker compose restart          # Restart all services
```

### Deploy a code update

```bash
cd Persona
git pull
docker compose up -d --build    # Rebuilds image, restarts containers
```

The vector store volume (`vector_data`) persists across rebuilds — it is NOT
re-downloaded unless the volume is deleted or the file is absent.

### Stop the stack

```bash
docker compose down             # Stops and removes containers (volume preserved)
docker compose down -v          # Also deletes volumes (vector store will re-download)
```

### Check disk usage

```bash
df -h                           # Overall disk
docker system df                # Docker image/volume usage
```

---

## First Boot Behaviour

On the very first `docker compose up`, `entrypoint.sh` checks whether
`VECTOR_STORE_PATH` exists on disk. If it doesn't, it downloads the file from
your DO Spaces bucket before starting Uvicorn.

Expected startup sequence in logs:

```
INFO  Vector store not found at /data/yelp_vector_store_200k.jsonl; downloading from DO Spaces ...
INFO  Downloading s3://persona-space/yelp_vector_store_200k.jsonl (1631 MB) → /data/yelp_vector_store_200k.jsonl
INFO  Download complete.
INFO  Loaded vector store from /data/yelp_vector_store_200k.jsonl (200192 items)
INFO  Application startup complete.
```

First boot takes ~3–5 minutes (download + load). Subsequent boots take ~30 seconds
(load only, file already on the volume).

---

## SSL Certificate Renewal

Let's Encrypt certificates expire after 90 days. Renew manually:

```bash
docker compose --profile certbot run --rm certbot renew
docker compose restart nginx
```

To automate, add a cron job on the droplet:

```bash
crontab -e
# Add:
0 3 1 * * cd /root/Persona && docker compose --profile certbot run --rm certbot renew && docker compose restart nginx
```

---

## Troubleshooting

| Symptom | Likely cause | Fix |
|---|---|---|
| `ERR_CONNECTION_REFUSED` on 443 | Certbot not run / nginx loaded bad config | Run Certbot steps 6a–6d |
| Mixed content error in browser | Frontend HTTPS calling HTTP backend | Ensure `VITE_API_URL` starts with `https://` |
| CORS error | `ALLOWED_ORIGINS` doesn't include frontend URL | Update `.env`, `docker compose restart api` |
| Vector store loads 0 items | `VECTOR_STORE_PATH` wrong or file missing | Check `.env`; run `docker compose logs api` |
| API container keeps restarting | OOM (not enough RAM) or startup error | Check `docker compose logs api`; need 2 GB+ RAM |
| 502 Bad Gateway from nginx | API container not healthy yet | Wait for vector store to load (~30s after download) |
