# Troubleshooting Guide for AlphaGalleon

## Quick Start Checklist

Before troubleshooting, verify you've completed these steps:

- [ ] Docker and Docker Compose installed (`docker --version`, `docker-compose --version`)
- [ ] `.env` file created from `.env.example`
- [ ] All required API keys filled in:
  - [ ] `GOOGLE_API_KEY` for Gemini API
  - [ ] `CONVEX_URL` for database
  - [ ] `UPSTOX_API_KEY` and `UPSTOX_API_SECRET` (optional for offline mode)
  - [ ] `JWT_SECRET_KEY` generated (should be random 32+ chars)
- [ ] Port 8000/8080 not used by other services
- [ ] At least 2GB free disk space for Docker images

## Common Issues and Solutions

### 1. Docker Image Build Fails

**Error:** `failed to build image` or `permission denied`

**Solutions:**
```bash
# Clean up Docker resources
docker system prune -a

# Rebuild with verbose output
docker-compose build --no-cache --progress=plain

# Check Docker daemon is running (macOS/Windows)
docker ps

# On Linux, ensure your user is in docker group
sudo usermod -aG docker $USER
newgrp docker
```

### 2. Port Already in Use

**Error:** `bind: address already in use` or `Ports: 8000:8000`

**Solutions:**
```bash
# Find what's using port 8000
lsof -i :8000

# Kill process using port
kill -9 <PID>

# Use different port
PORT=8001 docker-compose up

# Or stop existing containers
docker-compose down
docker ps -a  # see all containers
docker stop <container_id>
```

### 3. Backend Container Crashes on Start

**Error:** Container exits immediately or logs show `ConnectionError`

**Solutions:**
```bash
# Check container logs
docker-compose logs backend

# Check if environment variables are set
cat .env | grep -E "GOOGLE_API_KEY|CONVEX_URL|JWT_SECRET"

# Verify API keys are valid
# - GOOGLE_API_KEY: Get from Google Cloud Console
# - CONVEX_URL: Get from Convex dashboard
# - UPSTOX_API_KEY: Get from Upstox developer platform

# Restart with fresh state
docker-compose down -v  # Remove volumes
docker-compose up --build
```

### 4. Health Check Endpoint Returns Error

**Error:** `HTTP 500` or connection refused on `http://localhost:8000/health`

**Solutions:**
```bash
# Check backend logs for stack trace
docker-compose logs --tail=50 backend

# Common causes:
# 1. Missing environment variables
# 2. Invalid API keys
# 3. Convex database not accessible
# 4. Port already bound to another process

# Test connectivity to backend
curl -v http://localhost:8000/health

# Check if backend is even running
docker-compose ps
docker logs $(docker-compose ps -q backend)
```

### 5. Authentication (Login/Signup) Fails

**Error:** `POST /api/v1/auth/signup` returns 500 or connection error

**Solutions:**
```bash
# Check JWT_SECRET_KEY is set
grep JWT_SECRET .env

# Regenerate if missing or empty
openssl rand -hex 32  # Copy output to .env JWT_SECRET_KEY

# Check password hashing dependencies
docker-compose exec backend pip list | grep bcrypt

# Test auth endpoint directly
curl -X POST http://localhost:8000/api/v1/auth/signup \
  -H "Content-Type: application/json" \
  -d '{
    "email": "test@example.com",
    "password": "test123",
    "name": "Test User",
    "risk_profile": "moderate"
  }'

# Check Convex database is connected
curl http://localhost:8000/health | grep -i database
```

### 6. Mobile App Can't Connect to Backend

**Error:** Network error, timeout, or blank screens

**Solutions:**
```bash
# 1. Verify backend is running
curl http://localhost:8000/health

# 2. Check mobile API_BASE_URL
# File: mobile/src/api/index.ts
# Should match your backend URL:
# - Local development: http://localhost:8000
# - Production: https://your-api-domain.com

# 3. Test CORS is working
curl -X OPTIONS http://localhost:8000/api/v1/brain/memo \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -v

# 4. Check firewall isn't blocking port 8000
# macOS
sudo lsof -i :8000

# 5. Use ngrok to test from physical device
brew install ngrok
ngrok http 8000
# Update mobile API_BASE_URL to ngrok URL
```

### 7. Admin Dashboard Not Loading Data

**Error:** Tables are empty, API calls return 401/403

**Solutions:**
```bash
# 1. Verify admin endpoints are accessible
curl http://localhost:8000/api/v1/admin/users

# 2. Check admin authentication
# Admin dashboard needs valid JWT token from /auth/login endpoint

# 3. Ensure Convex database has test data
# Check convex/users.ts and convex/portfolios.ts are properly synced

# 4. Check admin-dashboard API client
# File: admin-dashboard/src/api/client.ts
# Verify baseURL matches your backend:
const baseURL = 'http://localhost:8000' // development
const baseURL = 'https://api.yourdomain.com' // production

# 5. Test admin endpoint with auth
TOKEN=$(curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"admin123"}' | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

curl http://localhost:8000/api/v1/admin/users \
  -H "Authorization: Bearer $TOKEN"
```

### 8. Database/Convex Connection Issues

**Error:** `ConnectionError`, `DatabaseUnavailable`, or 503 responses

**Solutions:**
```bash
# 1. Verify CONVEX_URL is correct and accessible
curl https://your-convex-url.com/_health 2>/dev/null || echo "URL invalid"

# 2. Check Convex dashboard
# - Log in to https://console.convex.dev
# - Verify your deployment is active
# - Check database tables are created (users, portfolios, activities, memos)

# 3. Test Convex connectivity from backend
docker-compose exec backend python -c "
import requests
url = '$CONVEX_URL'
resp = requests.get(f'{url}/_health', timeout=5)
print(f'Convex Status: {resp.status_code}')
"

# 4. Check API key/URL in .env
grep CONVEX .env

# 5. Redeploy Convex schema if needed
cd convex
npx convex deploy
```

### 9. API Endpoints Return 404 (Not Found)

**Error:** `POST /api/v1/brain/memo` returns `404 Not Found`

**Solutions:**
```bash
# 1. Check backend is running and listening
curl http://localhost:8000/docs  # FastAPI auto-docs

# 2. Verify endpoint exists in main.py
grep -n "api/v1/brain/memo" alphagalleon-backend/app/main.py

# 3. Check uvicorn config
# FastAPI should be listening on 0.0.0.0:8000

# 4. Test with verbose curl
curl -v http://localhost:8000/api/v1/brain/memo

# 5. Check FastAPI route registration
docker-compose logs backend | grep -i route

# 6. Ensure main.py has imports
grep "from app.brain" alphagalleon-backend/app/main.py
```

### 10. High Memory Usage or Crashes

**Error:** Container OOMKilled, slow response times, crashes after minutes

**Solutions:**
```bash
# 1. Check memory usage
docker stats

# 2. Increase Docker memory limit
# Edit docker-compose.yml:
# services:
#   backend:
#     deploy:
#       resources:
#         limits:
#           memory: 2G

# 3. Check for memory leaks in logs
docker-compose logs backend | grep -i memory

# 4. Reduce request payload size
# Instead of sending whole portfolio, send subset

# 5. Enable request caching
# Add response caching to minimize API calls

# 6. Profile memory usage
docker-compose exec backend pip install memory-profiler
docker-compose exec backend python -m memory_profiler app/main.py
```

### 11. CORS Errors (Mobile/Admin Can't Call Backend)

**Error:** `CORS error`, `No 'Access-Control-Allow-Origin'`, origin blocked

**Solutions:**
```bash
# 1. Check CORS is enabled in main.py
grep -A5 "CORSMiddleware" alphagalleon-backend/app/main.py

# 2. Verify CORS origins match your domains
# Should include:
# - http://localhost:3000 (admin local)
# - http://localhost:8081 (mobile local)
# - Your production domains

# 3. Test CORS with preflight request
curl -X OPTIONS http://localhost:8000/api/v1/brain/memo \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" \
  -v

# 4. Check response headers
curl -i http://localhost:8000/api/v1/brain/memo

# 5. In production, ensure HTTPS and domains match exactly
# Update CORS origins in main.py before deploying
```

### 12. Tests Fail with "Connection Refused"

**Error:** `test-deployment.sh` shows all red X's

**Solutions:**
```bash
# 1. Start backend first
docker-compose up -d backend
sleep 5  # Wait for startup

# 2. Run tests with verbose output
bash -x test-deployment.sh

# 3. Check health manually
curl -v http://localhost:8000/health

# 4. Use monitor script to debug
bash monitor.sh --once

# 5. Check backend logs during tests
docker-compose logs -f backend &
bash test-deployment.sh

# 6. Test individual endpoints
API_URL=http://localhost:8000 bash test-deployment.sh 2>&1 | head -50
```

## Deployment-Specific Issues

### Production Docker Build Fails

**Error:** Build succeeds locally but fails in CI/CD

**Solutions:**
```bash
# 1. Check build context
docker build -f Dockerfile -t alphagalleon:latest .

# 2. Verify all files exist
ls -la Dockerfile
ls -la alphagalleon-backend/requirements.txt

# 3. Test build in clean environment
docker system prune -a
docker build --no-cache -t alphagalleon:latest .

# 4. Check for platform-specific issues
# macOS/Windows: Ensure line endings are LF not CRLF
dos2unix Dockerfile
dos2unix alphagalleon-backend/requirements.txt
```

### SSL/TLS Certificate Issues

**Error:** `ERR_SSL_PROTOCOL_ERROR`, certificate invalid, mixed content

**Solutions:**
```bash
# 1. Verify certificate is valid
openssl x509 -in /path/to/cert.pem -text -noout

# 2. Check certificate expiry
openssl x509 -in /path/to/cert.pem -noout -dates

# 3. Renew with Let's Encrypt (free)
certbot certonly --standalone -d your-domain.com

# 4. Test HTTPS connection
curl -v https://your-domain.com/health

# 5. Check Nginx is terminating SSL properly
docker-compose exec nginx nginx -t

# 6. Update Nginx config with correct cert paths
# Edit docker-compose.prod.yml ssl_certificate paths
```

## Performance Tuning

### Slow Response Times

```bash
# 1. Check server load
docker stats

# 2. Enable response caching
# Add to main.py:
from fastapi_cache2 import FastAPICache2
from fastapi_cache2.backends.redis import RedisBackend
# Configure cache with Redis

# 3. Reduce database queries
# Check Brain/Doctor/Architect for N+1 queries

# 4. Enable Gzip compression
# Already in DEPLOYMENT.md Nginx config

# 5. Add CDN for static assets
# Serve from CloudFront or Cloudflare

# 6. Profile endpoints
docker-compose exec backend pip install py-spy
docker-compose exec backend py-spy record -o profile.svg python -m uvicorn app.main:app
```

### High CPU Usage

```bash
# 1. Check CPU % with docker stats
docker stats --no-stream

# 2. Profile CPU usage
docker top $(docker-compose ps -q backend)

# 3. Check for tight loops or blocking operations
grep -n "while True" alphagalleon-backend/app/*.py

# 4. Optimize AI API calls
# - Reduce token generation length
# - Cache responses when possible
# - Use streaming where available

# 5. Implement request rate limiting
from slowapi import Limiter
limiter = Limiter(key_func=get_remote_address)
```

## Getting Help

### Useful Debug Commands

```bash
# View all logs
docker-compose logs -f

# View specific service logs
docker-compose logs -f backend
docker-compose logs -f nginx

# Execute command in container
docker-compose exec backend python -c "print('Hello from container')"

# View running processes in container
docker-compose exec backend ps aux

# Test API endpoint
curl -v http://localhost:8000/api/v1/brain/status

# Check environment variables
docker-compose exec backend env | grep -E "CONVEX|GOOGLE|JWT"

# View docker-compose config
docker-compose config

# Validate docker-compose file
docker-compose config --quiet && echo "✓ Valid"
```

### Health Indicators

When debugging, check these indicators:

**Healthy System:**
- `docker-compose ps` shows all containers `Up`
- `curl http://localhost:8000/health` returns `{"status":"operational"}`
- `curl http://localhost:8000/health` includes `"database":"connected"`
- Backend logs show no errors
- Response times < 500ms (under load)

**Unhealthy System:**
- Containers exited or restarting
- Health check returns 500 or connection refused
- Logs contain `ERROR`, `CRITICAL`, or stack traces
- Response times > 2000ms consistently
- Memory usage > 80% of available

### When to Restart vs Rebuild

| Issue | Solution |
|-------|----------|
| Container crashed | `docker-compose restart backend` |
| Code changes | `docker-compose down && docker-compose up --build` |
| Environment changed | `docker-compose down -v && docker-compose up` (removes volumes) |
| Port conflict | `docker-compose down && docker-compose up` (after killing other process) |
| Stuck process | `docker-compose kill && docker-compose up` |
| Database corruption | `docker-compose down -v && docker-compose up --build` ⚠️ Erases data |

### Support Resources

- **FastAPI Docs:** https://fastapi.tiangolo.com
- **Docker Docs:** https://docs.docker.com
- **Convex Docs:** https://docs.convex.dev
- **Upstox API:** https://upstox.com/developer/documentation
- **Google Gemini:** https://ai.google.dev
- **AlphaGalleon Repo:** https://github.com/your-org/alphagalleon

---

**Last Updated:** 2025-02-24
**AlphaGalleon Version:** 1.0.0-rc1
