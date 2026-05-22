# Persona Backend — DigitalOcean Deployment Guide

This guide covers deploying the Persona FastAPI backend on a DigitalOcean Droplet with:
- Docker Compose (API + Nginx)
- Let's Encrypt SSL (via Certbot)
- Vector store auto-download from DigitalOcean Spaces on first boot
- Embedding model baked into the Docker image (no HuggingFace download at runtime)

The frontend is deployed separately on Vercel and calls this API over HTTPS.

---

## Prerequisites

- A DigitalOcean account
- A domain name with DNS pointing to the Droplet IP (e.g. `api.yourapp.com`)
- The 50k Yelp vector store file (`yelp_vector_store.json`, 408 MB) built locally
- SSH key added to your DO account

---

## 1. Create a DigitalOcean Space (object storage)

The vector store is too large to include in the Docker image. It lives in DO Spaces and is
downloaded to a persistent Docker volume on first boot.

1. Go to **Spaces Object Storage** in the DO dashboard → **Create a Space**
2. Choose a region (e.g. `nyc3`). Note the endpoint: `https://nyc3.digitaloceanspaces.com`
3. Set the Space to **Private**
4. Go to **API → Spaces Keys** → **Generate New Key**
   - Save the **Access Key** and **Secret Key** — you will need them in `.env`
5. Upload the vector store:

```bash
# Install s3cmd or use the DO dashboard uploader
s3cmd --access_key=YOUR_KEY --secret_key=YOUR_SECRET \
      --host=nyc3.digitaloceanspaces.com \
      --host-bucket='%(bucket)s.nyc3.digitaloceanspaces.com' \
      put data/yelp_vector_store.json s3://YOUR_BUCKET_NAME/yelp_vector_store.json
```

Or use the **Upload** button in the DO Spaces dashboard.

---

## 2. Create a Droplet

**Recommended specs** (handles 50k-item vector store + embedding model in memory):

| Field | Value |
|---|---|
| Image | Ubuntu 22.04 LTS x64 |
| Plan | **Basic — 4 GB RAM / 2 vCPU / 80 GB SSD** (~$24/mo) |
| Region | Same region as your DO Space (e.g. nyc3) |
| Authentication | SSH Key (add your public key) |
| Monitoring | Enable |

> 4 GB RAM is the minimum. The vector store alone occupies ~1.5 GB in memory after loading.

Note the Droplet's **public IPv4 address**.

---

## 3. Point your domain to the Droplet

In your DNS provider, create an **A record**:

```
api.yourapp.com  →  DROPLET_IP
```

Wait for DNS propagation (usually 5–30 minutes) before running Certbot.

---

## 4. Initial server setup

SSH into the Droplet:

```bash
ssh root@DROPLET_IP
```

### Install Docker

```bash
apt-get update && apt-get upgrade -y
apt-get install -y ca-certificates curl gnupg

install -m 0755 -d /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg
chmod a+r /etc/apt/keyrings/docker.gpg

echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu $(. /etc/os-release && echo "$VERSION_CODENAME") stable" \
  | tee /etc/apt/sources.list.d/docker.list > /dev/null

apt-get update
apt-get install -y docker-ce docker-ce-cli containerd.io docker-compose-plugin

# Verify
docker --version
docker compose version
```

### Configure firewall

```bash
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

---

## 5. Clone the repository

```bash
cd /opt
git clone https://github.com/Techdee1/Persona.git
cd Persona
```

---

## 6. Configure environment variables

```bash
cp .env.example .env
nano .env
```

Fill in every value:

```env
# LLM
ENABLE_LLM=true
OPENAI_API_KEY=sk-...
OPENAI_MODEL=gpt-4o

# Vector store — the entrypoint will download it to /data/ on first boot
VECTOR_STORE_PATH=/data/yelp_vector_store.json

# DigitalOcean Spaces — where the vector store file lives
DO_SPACES_ENDPOINT=https://nyc3.digitaloceanspaces.com
DO_SPACES_REGION=nyc3
DO_SPACES_BUCKET=your-bucket-name
DO_SPACES_KEY=your-spaces-access-key
DO_SPACES_SECRET=your-spaces-secret-key
DO_SPACES_VECTOR_STORE_KEY=yelp_vector_store.json

# CORS — your Vercel frontend URL (no trailing slash)
ALLOWED_ORIGINS=https://yourapp.vercel.app
```

---

## 7. SSL certificate setup (first time only)

Getting the cert requires nginx to serve the ACME challenge over HTTP first.

### Step A — Start with the HTTP-only nginx config

```bash
cp nginx/nginx.conf nginx/nginx.conf.bak
cp nginx/nginx.http.conf nginx/nginx.conf
```

Edit `nginx/nginx.conf` and replace `YOUR_DOMAIN` with your actual domain:

```bash
sed -i 's/YOUR_DOMAIN/api.yourapp.com/g' nginx/nginx.conf
```

### Step B — Build the image and start services (HTTP only)

```bash
docker compose build
docker compose up -d api nginx
```

Verify the API is reachable (this will also trigger the first vector store download):

```bash
# Watch startup — vector store download takes ~60-90s on first boot
docker compose logs -f api
# Once you see "Loaded vector store from ... (50000 items)", the API is ready
curl http://api.yourapp.com/health
# Expected: {"status":"ok"}
```

### Step C — Issue the certificate

```bash
docker compose --profile certbot run --rm certbot certonly \
  --webroot --webroot-path=/var/www/certbot \
  --email your@email.com --agree-tos --no-eff-email \
  -d api.yourapp.com
```

### Step D — Switch to the full HTTPS nginx config

```bash
cp nginx/nginx.conf.bak nginx/nginx.conf
sed -i 's/YOUR_DOMAIN/api.yourapp.com/g' nginx/nginx.conf
docker compose restart nginx
```

Verify HTTPS:

```bash
curl https://api.yourapp.com/health
# Expected: {"status":"ok"}
```

---

## 8. Verify the full deployment

```bash
# Health check
curl https://api.yourapp.com/health

# Task A — review simulation
curl -s -X POST https://api.yourapp.com/task-a/simulate \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "u1",
    "records": [{"item_id": "r1", "rating": 5.0, "review_text": "Incredible jollof rice!", "timestamp": "2024-01-01"}],
    "target_item": {"name": "Lagos Kitchen", "category": "Nigerian"}
  }' | python3 -m json.tool

# Task B — recommendations (real Yelp results via vector store)
curl -s -X POST https://api.yourapp.com/task-b/recommend \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "u1",
    "records": [{"item_id": "r1", "rating": 5.0, "review_text": "Incredible jollof rice!", "timestamp": "2024-01-01"}],
    "query_text": "Nigerian food Lagos pepper soup",
    "top_k": 5
  }' | python3 -m json.tool
```

---

## 9. Configure the Vercel frontend

In your Vercel project settings, add an environment variable:

```
NEXT_PUBLIC_API_URL=https://api.yourapp.com
```

(Or whatever the frontend framework uses for the API base URL.)

The backend already has CORS configured for the origin set in `ALLOWED_ORIGINS`.

---

## 10. Certificate auto-renewal

Add a cron job to renew the cert automatically:

```bash
crontab -e
```

Add this line:

```
0 3 * * * cd /opt/Persona && docker compose --profile certbot run --rm certbot renew --quiet && docker compose restart nginx
```

---

## 11. Ongoing operations

### View logs

```bash
docker compose logs -f api        # API logs (includes trace IDs)
docker compose logs -f nginx      # Nginx access/error logs
```

### Update to a new version

```bash
cd /opt/Persona
git pull origin main
docker compose build
docker compose up -d --no-deps api   # rolls API only, nginx stays up
```

### Restart services

```bash
docker compose restart api
docker compose restart nginx
```

### Stop everything

```bash
docker compose down
```

> The `vector_data` Docker volume persists between `down`/`up` cycles — the vector store
> is **not** re-downloaded unless you explicitly remove the volume (`docker volume rm persona_vector_data`).

---

## Architecture on the Droplet

```
Internet
    │  HTTPS (443)
    ▼
nginx:1.25-alpine
    │  HTTP (8000, internal Docker network)
    ▼
Persona API (FastAPI / uvicorn)
    │  reads
    ▼
vector_data volume  ←  downloaded from DO Spaces on first boot
    +
Embedding model     ←  baked into the Docker image at build time
```

---

## Environment variable reference

| Variable | Required | Description |
|---|---|---|
| `ENABLE_LLM` | Yes (prod) | Set `true` to enable OpenAI review generation |
| `OPENAI_API_KEY` | When LLM=true | OpenAI secret key |
| `OPENAI_MODEL` | No | Defaults to `gpt-4o` |
| `VECTOR_STORE_PATH` | Yes | Local path inside the container (e.g. `/data/yelp_vector_store.json`) |
| `DO_SPACES_ENDPOINT` | For auto-download | e.g. `https://nyc3.digitaloceanspaces.com` |
| `DO_SPACES_REGION` | For auto-download | e.g. `nyc3` |
| `DO_SPACES_BUCKET` | For auto-download | Spaces bucket name |
| `DO_SPACES_KEY` | For auto-download | Spaces access key |
| `DO_SPACES_SECRET` | For auto-download | Spaces secret key |
| `DO_SPACES_VECTOR_STORE_KEY` | No | Object key in bucket (default: `yelp_vector_store.json`) |
| `ALLOWED_ORIGINS` | Yes (prod) | Comma-separated Vercel/frontend URLs for CORS |
| `PROFILE_CACHE_TTL_SECONDS` | No | Profile cache TTL (default 3600) |
| `PROFILE_CACHE_MAX_SIZE` | No | Max cached profiles (default 1000) |
