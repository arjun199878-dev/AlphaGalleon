# AlphaGalleon Production Deployment Guide

## Prerequisites

- Docker & Docker Compose installed
- Node.js 18+ (for frontend builds)
- Git for version control
- Domain name (for HTTPS setup)
- API keys for: Google Gemini, Upstox, Telegram Bot (optional)

## Local Development Setup

### 1. Clone and Setup

```bash
git clone <repository-url>
cd AlphaGalleon--main\ 2
cp .env.example .env
```

### 2. Configure Environment Variables

Edit `.env` with your API keys:

```bash
# Backend API keys
GOOGLE_API_KEY=<your-key>
UPSTOX_API_KEY=<your-key>
UPSTOX_API_SECRET=<your-secret>
JWT_SECRET_KEY=$(openssl rand -hex 32)  # Generate random secret
CONVEX_URL=https://vibrant-spoonbill-564.eu-west-1.convex.cloud
```

### 3. Start Local Development

```bash
# Using Docker Compose
docker-compose up

# Or direct Python (if Docker not available)
cd alphagalleon-backend
pip install -r requirements.txt
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

### 4. Verify Backend is Running

```bash
# Check health endpoint
curl http://localhost:8000/health

# Test response should be:
# {"status": "healthy", "services": {...}}
```

---

## Production Deployment (Docker)

### 1. Build Production Image

```bash
# Build with production Dockerfile
docker build -t alphagalleon-backend:latest -f Dockerfile .

# Or with Docker Compose
docker-compose build --no-cache
```

### 2. Deploy to Cloud

#### Option A: AWS EC2

```bash
# 1. Launch EC2 instance (t3.medium or larger)
# 2. Install Docker
curl -fsSL https://get.docker.com -o get-docker.sh && sh get-docker.sh

# 3. Pull and run container
docker pull alphagalleon-backend:latest
docker run -d \
  --name alphagalleon \
  -p 8000:8000 \
  --env-file .env \
  --restart always \
  alphagalleon-backend:latest
```

#### Option B: Google Cloud Run

```bash
# 1. Enable Container Registry
gcloud services enable containerregistry.googleapis.com

# 2. Build and push image
gcloud builds submit --tag gcr.io/PROJECT-ID/alphagalleon-backend

# 3. Deploy
gcloud run deploy alphagalleon-backend \
  --image gcr.io/PROJECT-ID/alphagalleon-backend \
  --platform managed \
  --region us-central1 \
  --set-env-vars=GOOGLE_API_KEY=<key>,JWT_SECRET_KEY=<secret> \
  --allow-unauthenticated
```

#### Option C: Heroku

```bash
# 1. Login to Heroku
heroku login

# 2. Create app
heroku create alphagalleon-backend

# 3. Set environment variables
heroku config:set GOOGLE_API_KEY=<key>
heroku config:set JWT_SECRET_KEY=<secret>
heroku config:set CONVEX_URL=<url>

# 4. Deploy
git push heroku main
```

---

## Production Architecture

```
┌─────────────────────────────────────┐
│  Mobile App / Admin Dashboard       │
│  (React Native / React)             │
└────────────────┬────────────────────┘
                 │
┌────────────────▼────────────────────┐
│  Nginx Reverse Proxy                │
│  (SSL/TLS Termination)              │
└────────────────┬────────────────────┘
                 │
┌────────────────▼────────────────────┐
│  FastAPI Backend (Port 8000)        │
│  (Brain, Doctor, Architect, Scout)  │
└────────────────┬────────────────────┘
                 │
     ┌───────────┼───────────┐
     │           │           │
┌────▼──┐  ┌────▼──┐  ┌────▼──┐
│Convex │  │Google │  │Upstox │
│(DB)   │  │Gemini │  │(Data) │
└───────┘  └───────┘  └───────┘
```

---

## Security Checklist

- [ ] Change `JWT_SECRET_KEY` to random 32+ character string
- [ ] Use HTTPS with valid SSL certificate
- [ ] Enable CORS only for trusted domains
- [ ] Implement rate limiting on auth endpoints
- [ ] Add firewall rules for port 8000 (backend only)
- [ ] Enable database backups (Convex handles this)
- [ ] Use environment-specific secrets (AWS Secrets Manager / Google Secret Manager)
- [ ] Enable VPC/network isolation
- [ ] Set up monitoring and alerting
- [ ] Regular dependency updates and security patches

---

## Nginx Configuration (Production)

```nginx
upstream backend {
    server localhost:8000;
}

server {
    listen 443 ssl http2;
    server_name api.alphagalleon.com;

    ssl_certificate /etc/letsencrypt/live/api.alphagalleon.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/api.alphagalleon.com/privkey.pem;

    # Security headers
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Content-Type-Options "nosniff" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-XSS-Protection "1; mode=block" always;

    # CORS headers
    add_header Access-Control-Allow-Origin "*";
    add_header Access-Control-Allow-Methods "GET, POST, PUT, DELETE, OPTIONS";
    add_header Access-Control-Allow-Headers "Content-Type, Authorization";

    # Gzip compression
    gzip on;
    gzip_types text/plain application/json;
    gzip_min_length 1000;

    location / {
        proxy_pass http://backend;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_connect_timeout 60s;
        proxy_send_timeout 60s;
        proxy_read_timeout 60s;
    }
}

# Redirect HTTP to HTTPS
server {
    listen 80;
    server_name api.alphagalleon.com;
    return 301 https://$server_name$request_uri;
}
```

---

## Monitoring & Health Checks

### Health Endpoint
```bash
GET /health

Response:
{
  "status": "healthy",
  "services": {
    "brain": "operational",
    "doctor": "operational",
    "architect": "operational",
    "scout": "operational",
    "convex": "operational"
  }
}
```

### Logging
- Set `LOG_LEVEL=INFO` in production
- Collect logs via Docker (use `docker logs`)
- Consider ELK Stack / CloudWatch for centralized logging

### Performance Optimization
- Enable Redis caching for market data
- Implement request rate limiting
- Use CDN for static frontend assets
- Monitor API response times via APM tools

---

## Rollback Procedure

```bash
# If deployment fails, rollback to previous version
docker run -d \
  --name alphagalleon-backup \
  -p 8000:8000 \
  --env-file .env \
  alphagalleon-backend:previous-version

# Switch traffic back to old container
docker stop alphagalleon
docker rename alphagalleon-backup alphagalleon
```

---

## Support & Troubleshooting

### Backend not starting?
```bash
# Check logs
docker logs alphagalleon-backend

# Check environment variables
docker inspect alphagalleon-backend
```

### API returning 500 errors?
- Verify Convex URL is accessible
- Check API keys are valid
- Review backend logs for specific error

### Slow performance?
- Check backend logs for slow queries
- Monitor Convex query usage
- Consider caching strategy

---

## Next Steps After Deployment

1. **Run E2E Tests** — Test signup → login → generate memo flow
2. **Load Testing** — Use k6 or JMeter to test at scale
3. **DKIM/SPF Setup** — If sending emails (future feature)
4. **Analytics** — Add Mixpanel/Segment for user tracking
5. **Error Tracking** — Set up Sentry for production errors
6. **Auto-scaling** — Configure auto-scale policies
7. **CI/CD Pipeline** — GitHub Actions / Jenkins for automated deployments

---

## Production Checklist

- [ ] SSL Certificate installed
- [ ] Environment variables set
- [ ] Database backups enabled
- [ ] Monitoring & alerting configured
- [ ] Rate limiting enabled
- [ ] CORS whitelist configured
- [ ] Health checks verified
- [ ] Load testing passed
- [ ] Security audit completed
- [ ] Team trained on deployment process
