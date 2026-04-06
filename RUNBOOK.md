# AlphaGalleon Operations Runbook

## Quick Reference

**Startup:** `./start.sh [development|production|test]`  
**Monitoring:** `./monitor.sh`  
**Testing:** `bash test-deployment.sh`  
**Logs:** `docker-compose logs -f`  
**Status:** `docker-compose ps`  

---

## Daily Checklist

### Morning (Start of Shift)

- [ ] System is up: `docker-compose ps` shows all containers running
- [ ] Health check passes: `curl http://localhost:8000/health | head -c 100`
- [ ] No critical errors in overnight logs: `docker-compose logs --since 24h | grep ERROR`
- [ ] Database is connected: Health endpoint shows `"database":"connected"`
- [ ] API response times acceptable: `./monitor.sh --once | grep "Response Time"`

### Hourly

- [ ] Check system resources: `docker stats --no-stream | head -5`
- [ ] Verify no container restarts: Compare `docker ps` with previous check
- [ ] Sample API calls returning expected data
- [ ] No spike in error logs: `docker-compose logs --tail=100 | grep -c ERROR`

### Before Major Changes

- [ ] Back up current state: `docker-compose logs > logs-backup-$(date +%Y%m%d-%H%M%S).log`
- [ ] Stop non-essential services: `docker-compose stop frontend admin-dashboard`
- [ ] Verify changes locally first: Test in development environment
- [ ] Have rollback plan ready: Keep previous Docker image tag available

---

## Common Operations

### Starting AlphaGalleon

**Development Mode (Local):**
```bash
# Full setup with build
./start.sh development

# Or manual steps:
docker-compose build
docker-compose up -d
./monitor.sh --once
```

**Production Mode (AWS/GCP/Heroku):**
```bash
# Deploy with production config
./start.sh production

# Or manual:
docker-compose -f docker-compose.yml -f docker-compose.prod.yml up -d
sleep 10
bash test-deployment.sh
```

### Stopping Services

**Graceful shutdown (recommended):**
```bash
docker-compose down
# Waits for containers to stop (max 10 seconds)
# Removes containers but keeps volumes (data persists)
```

**Force shutdown (emergency only):**
```bash
docker-compose kill
# Immediately stops all containers
# May lose in-flight requests
```

### Viewing Logs

**All services:**
```bash
docker-compose logs -f
# Press Ctrl+C to stop following
```

**Specific service:**
```bash
docker-compose logs -f backend
docker-compose logs -f nginx
```

**Last N lines:**
```bash
docker-compose logs --tail=100
docker-compose logs --tail=50 backend
```

**Since specific time:**
```bash
docker-compose logs --since 2025-02-24T10:00:00
docker-compose logs --since 30m  # Last 30 minutes
```

**With timestamps:**
```bash
docker-compose logs --timestamps
```

### Scaling Services

**Run multiple backend instances (for high load):**
```bash
# Update docker-compose.yml:
# services:
#   backend:
#     deploy:
#       replicas: 3

docker-compose up -d --scale backend=3

# Verify
docker-compose ps
```

**Note:** With Docker Compose, replicas require load balancing via Nginx (configured in docker-compose.prod.yml)

### Database Recovery

**View current database status:**
```bash
docker-compose exec backend python -c "
import requests
convex_url = '$CONVEX_URL'
resp = requests.get(f'{convex_url}/_health', timeout=5)
print(f'Database Status: {resp.status_code}')
"
```

**Re-sync database schema (if corrupted):**
```bash
cd convex
npx convex deploy
cd ..

# Restart backend
docker-compose restart backend
```

**Clear and reset database (DESTRUCTIVE - erases all data):**
```bash
# In Convex dashboard:
# 1. Go to Settings
# 2. Click "Erase data" (WARNING: No undo)
# Then redeploy:
cd convex
npx convex deploy
```

---

## Incident Response

### Containers Keep Restarting

**Diagnosis:**
```bash
docker-compose logs backend | head -20  # Check error
docker-compose ps  # Check restart count
```

**Common causes and fixes:**

| Error | Solution |
|-------|----------|
| `ConnectionError` to Convex | Check `CONVEX_URL` in .env, verify it's accessible |
| `google.auth.exceptions.DefaultCredentialsError` | Check `GOOGLE_API_KEY` is set in .env |
| `Port XXX already in use` | Kill other process: `lsof -i :8000` then `kill -9 PID` |
| `Out of memory` | Increase Docker memory limit or reduce container count |
| `ModuleNotFoundError` | Rebuild: `docker-compose build --no-cache` |

### API Endpoints Returning 500

**Debug steps:**
```bash
# 1. Check backend logs for stack trace
docker-compose logs backend | grep -A20 "ERROR\|Traceback"

# 2. Test health endpoint
curl -v http://localhost:8000/health

# 3. Check specific endpoint
curl -v http://localhost:8000/api/v1/brain/status

# 4. If offline fallback, check API keys
grep "GOOGLE_API_KEY\|UPSTOX_API" .env | cut -d= -f1
```

**Common fixes:**
```bash
# Invalid environment variable
nano .env  # Edit and fix
docker-compose down && docker-compose up --build

# Database connection lost
docker-compose restart backend
# If persists, recreate: docker-compose down -v && docker-compose up --build

# Port already bound
  lsof -i :8000
kill -9 <PID>
docker-compose restart
```

### High CPU/Memory Usage

**Check what's consuming resources:**
```bash
docker stats --no-stream
```

**If backend is high:**
```bash
# Check logs for hot loops or excessive requests
docker-compose logs backend | tail -50

# Monitor in real-time during peak hours
watch -n 1 'docker stats --no-stream | grep backend'

# Restart backend to clear any memory leaks
docker-compose restart backend

# Scale horizontally if load is legitimate
docker-compose up -d --scale backend=2
```

**If nginx is high:**
```bash
# Check request logs
docker-compose logs nginx | tail -50

# Verify rate limiting is working
grep "limit_req" docker-compose.prod.yml

# May indicate DDoS attack - check IP origins
docker-compose logs nginx | grep -o '"[^"]*"' | sort | uniq -c | sort -rn | head
```

### Users Report "Connection Failed"

**Debug checklist:**
```bash
# 1. Verify backend is actually running
curl -v http://localhost:8000/health

# 2. Check CORS is configured
curl -X OPTIONS http://localhost:8000/api/v1/brain/memo \
  -H "Origin: http://localhost:3000" \
  -H "Access-Control-Request-Method: POST" -v | grep Access-Control

# 3. Check firewall
# AWS: Check security group allows port 8000
# GCP: Check firewall rules allow incoming 8000
# Azure: Check Network Security Group

# 4. Check DNS resolution
# For users: nslookup api.yourdomain.com
# For you: dig api.yourdomain.com +short

# 5. Test from user's IP (if possible)
curl -H "X-Forwarded-For: <user-ip>" http://localhost:8000/health
```

### Authentication Issues

**Users can't login/signup:**
```bash
# Test login endpoint
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"test123"}'

# Verify JWT_SECRET_KEY is set
grep JWT_SECRET .env

# Check password hashing is working
docker-compose exec backend python -c "
from app.auth import hash_password, verify_password
hashed = hash_password('test123')
print(f'Hash valid: {verify_password(\"test123\", hashed)}')
"
```

---

## Performance Optimization

### Response Time is Slow

**Measure baseline:**
```bash
./monitor.sh --once | grep "Response Time"
```

**Identify bottleneck:**
```bash
# Check API call latency
curl -w "Total: %{time_total}s\n" http://localhost:8000/api/v1/brain/memo \
  -X POST \
  -H "Content-Type: application/json" \
  -d '{"portfolio_data":{}}'

# Check database latency (Convex)
docker-compose logs backend | grep "convex\|database" | tail -10
```

**Optimizations:**
```bash
# Add response caching
# Edit alphagalleon-backend/app/main.py:
# from fastapi_cache2 import cached
# @cached(namespace="brain", expire=3600)

# Reduce batch size
# Edit scout.py: batch_size = 5 (instead of 50)

# Enable Gzip compression (already in Nginx config)

# Add database indexing in Convex
# Edit convex/schema.ts: .index("by_user_id", ["user_id"])
```

---

## Security Checks

### Daily Security Tasks

- [ ] No sensitive data in logs: `docker-compose logs | grep -i password`
- [ ] JWT tokens are random: Check JWT_SECRET_KEY is 32+ random characters
- [ ] CORS is restricted: Only allow trusted domains
- [ ] Rate limiting is active: Check Nginx config has `limit_req`
- [ ] HTTPS is enforced: All traffic goes through Nginx SSL/TLS
- [ ] API keys are rotated: Update GOOGLE_API_KEY, UPSTOX credentials monthly

### SSL Certificate Monitoring

**Check expiry:**
```bash
curl -s https://api.yourdomain.com --insecure -v 2>&1 | grep "expire date"
# or
openssl s_client -connect api.yourdomain.com:443 -brief | grep "expire"
```

**Renew if < 30 days to expiry:**
```bash
certbot renew --force-renewal

# Reload Nginx with new cert
docker-compose exec nginx nginx -s reload
```

---

## Monitoring Setup

### Real-time Monitoring

```bash
# Terminal 1: Service logs
docker-compose logs -f

# Terminal 2: Resource usage
watch -n 5 docker stats --no-stream

# Terminal 3: Health checks (runs every 5 seconds)
./monitor.sh
```

### Alert Thresholds

Set up alerts when:
- Container exits (non-zero exit code)
- CPU > 80% for > 5 minutes
- Memory > 80% for > 5 minutes
- Response time > 1 second (p95)
- Error rate > 1% of requests
- Health endpoint returns 500
- Certificate expires in < 7 days

### Metric Collection

**For external monitoring (Datadog, New Relic, etc.):**
```bash
# Export Docker metrics
docker-compose exec backend pip install prometheus-client

# Prometheus metrics available at:
# http://localhost:8000/metrics

# Collect and ship to monitoring service:
# curl -s http://localhost:8000/metrics | ship_to_monitoring_service()
```

---

## Backup and Recovery

### Backup Database

**Manual backup (before major changes):**
```bash
# Export users
curl -s http://localhost:8000/api/v1/admin/users > users-backup-$(date +%Y%m%d-%H%M%S).json

# Export activity log
curl -s http://localhost:8000/api/v1/admin/activity > activity-backup-$(date +%Y%m%d-%H%M%S).json

# Backup Docker volumes
docker run -v alphagalleon_convex_data:/data -v $(pwd):/backup \
  alpine tar czf /backup/convex-backup-$(date +%Y%m%d-%H%M%S).tar.gz -C / data
```

**Automated backup (daily via cron):**
```bash
# Add to crontab:
0 3 * * * /home/deploy/alphagalleon/scripts/backup.sh

# Create scripts/backup.sh:
#!/bin/bash
mkdir -p /backups
curl -s "http://localhost:8000/api/v1/admin/users" > \
  "/backups/users-$(date +\%Y\%m\%d-\%H\%M\%S).json"
# Keep only last 30 days
find /backups -type f -mtime +30 -delete
```

### Restore from Backup

**From Convex backup:**
```bash
# 1. Stop application
docker-compose down

# 2. Clear database (in Convex dashboard: Settings > Erase data)

# 3. Restart application
docker-compose up -d

# 4. Reimport data via SQL/API calls
# curl -X POST http://localhost:8000/api/v1/admin/restore \
#   -F "backup=@users-backup.json"
```

---

## Regular Maintenance

### Weekly Tasks

- [ ] Review logs for errors: `docker-compose logs --since 7d | grep ERROR | wc -l`
- [ ] Check disk space: `docker system df`
- [ ] Prune unused images: `docker image prune -a --force`
- [ ] Verify backups exist and are recent: `ls -lh /backups/ | head -5`
- [ ] Test failover/recovery procedure (if applicable)

### Monthly Tasks

- [ ] Rotate API keys (GOOGLE_API_KEY, UPSTOX credentials)
- [ ] Generate new JWT_SECRET_KEY: `openssl rand -hex 32`
- [ ] Review and update security rules (firewall, CORS)
- [ ] Update Docker base image: `docker pull python:3.10-slim`
- [ ] Test backup restoration process
- [ ] Review resource utilization and capacity planning
- [ ] Update runbook with any new procedures

### Quarterly Tasks

- [ ] Major version updates (Python, FastAPI, dependencies)
- [ ] Security audit (code review, dependency scan)
- [ ] Performance optimization
- [ ] Disaster recovery drill
- [ ] Capacity planning for next quarter

---

## Escalation Path

**Issue Resolution Levels:**

| Issue | Owner | Escalate If |
|-------|-------|-------------|
| Container restart loop | DevOps Engineer | >3 restarts in 1 hour |
| Slow API response | Backend Engineer | >1s p95 latency |
| Database unavailable | Database Admin | >5 minute outage |
| Certificate warning | SRE | <14 days to expiry |
| DDoS attack | Security Team | >10x normal traffic |
| Data corruption | Database Admin + CTO | Immediate |
| Security breach | CTO + Legal | Immediate |

**Contact Information:**
- DevOps Lead: Slack #devops-oncall
- Backend Lead: @backend-lead Slack
- Database Admin: @db-admin Slack
- On-Call Rotation: PagerDuty (check this week's schedule)

---

## Useful Commands Reference

```bash
# Status & Monitoring
docker-compose ps                          # View container status
docker-compose logs -f                     # Follow logs (all services)
docker-compose logs -f backend             # Follow backend logs only
docker stats --no-stream                   # One-shot resource usage
watch -n 5 'docker stats --no-stream'     # Monitor resources every 5 seconds
./monitor.sh                               # Run health monitoring script

# Starting/Stopping
docker-compose up -d                       # Start (detached/background)
docker-compose down                        # Stop and remove containers
docker-compose restart backend             # Restart single service
docker-compose kill                        # Force stop all containers

# Configuration
docker-compose config                      # Show effective config
nano .env                                  # Edit environment variables
docker-compose config --quiet              # Validate syntax

# Rebuilding
docker-compose build --no-cache             # Force rebuild (no cache)
docker-compose up --build                  # Build and start
docker system prune -a                     # Clean up all unused images

# Accessing Containers
docker-compose exec backend bash           # Open shell in backend
docker-compose exec backend python -c "..." # Run Python command
docker-compose exec backend pip list       # List installed packages

# Debugging
curl -v http://localhost:8000/health      # Test health endpoint (verbose)
curl -s http://localhost:8000/health | jq # Test health endpoint (pretty JSON)
bash test-deployment.sh                    # Run full test suite
bash -x test-deployment.sh                 # Run tests with debug output

# Maintenance
docker-compose logs > backup.log           # Backup current logs
docker image prune -a                      # Remove unused images
docker system df                           # Show Docker storage usage
docker logs <container-id> --since 1h      # View logs from last hour
```

---

## Document Updates

- **Last Updated:** 2025-02-24
- **AlphaGalleon Version:** 1.0.0-rc1  
- **Author:** Infrastructure Team
- **Review Schedule:** Monthly (first Monday of month)

For updates or questions, create an issue in the AlphaGalleon repository or contact the DevOps team.
