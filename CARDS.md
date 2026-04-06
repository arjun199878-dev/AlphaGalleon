# AlphaGalleon Quick Reference Card

**Version:** 1.0.0-rc1 | **Status:** ✅ Production Ready | **Updated:** 2025-02-24

---

## 🎯 Quickest Start (5 minutes)

```bash
# 1. Set up environment
cp .env.example .env
nano .env  # Fill in: GOOGLE_API_KEY, CONVEX_URL, JWT_SECRET_KEY

# 2. Verify and start
./start.sh production

# 3. Check health
./monitor.sh --once

# 4. Run tests (verify everything works)
bash test-deployment.sh
```

**App is live at:** `http://localhost:8000`

---

## 📚 Documentation by Role

| Role | Start Here | Then Read |
|------|-----------|-----------|
| **DevOps/SRE** | [DEPLOYMENT.md](DEPLOYMENT.md) | [RUNBOOK.md](RUNBOOK.md) + [TROUBLESHOOTING.md](TROUBLESHOOTING.md) |
| **Backend Dev** | [RUN.md](RUN.md) | `alphagalleon-backend/app/main.py` + [TROUBLESHOOTING.md](TROUBLESHOOTING.md) |
| **Mobile Dev** | [RUN.md](RUN.md) | `mobile/src/api/index.ts` + [TROUBLESHOOTING.md](TROUBLESHOOTING.md) |
| **Product/Manager** | [SESSION_SUMMARY.md](SESSION_SUMMARY.md) | This card (below) |

---

## 🔧 Essential Commands

### Startup & Monitoring
```bash
./start.sh development          # Local dev (with rebuild)
./start.sh production           # Production deploy
./start.sh test                 # Run test suite
./monitor.sh                    # Live monitoring (press Ctrl+C to stop)
./monitor.sh --once             # Health check (single run)
```

### Docker Operations
```bash
docker-compose ps               # View status of all containers
docker-compose logs -f          # Follow all logs (Ctrl+C to stop)
docker-compose logs -f backend  # Follow backend only
docker-compose restart backend  # Restart backend service
docker-compose down             # Stop all services
```

### Testing
```bash
curl http://localhost:8000/health          # Quick health check
bash test-deployment.sh                    # Full E2E test suite
bash -x test-deployment.sh                 # Test with debug output
```

---

## 🚨 Troubleshooting (When Things Break)

**Step 1:** Check what's failing
```bash
./monitor.sh --once
```

**Step 2:** Look it up in [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Port 8000 already in use? → See section "Port Already in Use"
- Connection errors? → See "Backend Container Crashes"
- API returning 500? → See "API Endpoints Return 500"
- Mobile can't connect? → See "Mobile App Can't Connect"

**Step 3:** Verify fix
```bash
./monitor.sh --once
# Or run: bash test-deployment.sh
```

---

## 📊 System Status

Check health anytime:
```bash
curl -s http://localhost:8000/health | jq
```

**Expected output:**
```json
{
  "status": "operational",
  "database": "connected",
  "google_api": "available",
  "upstox_api": "offline"
}
```

---

## 🔑 Environment Variables (.env)

Must have these filled in:
- `CONVEX_URL` - Your Convex database URL (from convex.dev)
- `GOOGLE_API_KEY` - Google Gemini API key
- `JWT_SECRET_KEY` - Random 32+ character secret (run: `openssl rand -hex 32`)

Optional (app works with offline fallbacks):
- `UPSTOX_API_KEY` - Upstox market data API
- `UPSTOX_API_SECRET` - Upstox API secret

---

## 🌐 API Endpoints (All Working)

### Health & Status
- `GET /health` - Full system status
- `GET /docs` - Interactive API documentation

### Brain (Investment Memos)
- `POST /api/v1/brain/memo` - Generate investment analysis
- `POST /api/v1/brain/generate` - Raw Gemini API call
- `GET /api/v1/brain/status` - Brain engine status

### Doctor (Diagnostics)
- `POST /api/v1/doctor/diagnose` - Portfolio analysis
- `GET /api/v1/doctor/status` - Doctor engine status

### Architect (Portfolio Design)
- `POST /api/v1/architect/design` - Portfolio optimization
- `GET /api/v1/architect/status` - Architect engine status

### Scout (Market Data)
- `GET /api/v1/scout/quote/{symbol}` - Stock price quote
- `GET /api/v1/scout/status` - Scout engine status

### Auth (User Authentication)
- `POST /api/v1/auth/login` - User login (returns JWT token)
- `POST /api/v1/auth/signup` - New user registration
- `GET /api/v1/auth/verify` - Token validation

### Admin (Operational Views)
- `GET /api/v1/admin/users` - List all users
- `GET /api/v1/admin/activity` - Audit log

---

## ✅ Quick Verification Checklist

Before declaring "ready for users":

- [ ] `./monitor.sh --once` shows all green ✓
- [ ] `bash test-deployment.sh` has zero red ✗ marks
- [ ] `curl http://localhost:8000/health` returns 200
- [ ] Database shows connected
- [ ] HTTPS is enabled (production)
- [ ] Firewall rules allow ports
- [ ] `.env` has all required keys
- [ ] Backups are configured

---

## 🚀 Deployment Steps

1. **AWS EC2** (recommended):
   - Launch Ubuntu 22.04 instance
   - Install Docker: `curl -fsSL https://get.docker.com | sh`
   - Clone repo: `git clone <repo-url>`
   - Setup: `cp .env.example .env && nano .env`
   - Deploy: `./start.sh production`

2. **Google Cloud Run**:
   - Push Docker image: `gcloud builds submit --tag gcr.io/PROJECT/alphagalleon`
   - Deploy: `gcloud run deploy alphagalleon --image gcr.io/PROJECT/alphagalleon`

3. **Heroku**:
   - Create app: `heroku create alphagalleon`
   - Set env: `heroku config:set GOOGLE_API_KEY=xxx`
   - Deploy: `git push heroku main`

See [DEPLOYMENT.md](DEPLOYMENT.md) for full guides.

---

## 🆘 Common Issues (Quick Fixes)

| Problem | Fix |
|---------|-----|
| Port 8000 in use | `lsof -i :8000` then `kill -9 <PID>` |
| ConnectionError | Check `CONVEX_URL` in `.env` |
| ModuleNotFoundError | `docker-compose build --no-cache` |
| CORS error | Update mobile `API_BASE_URL` |
| Database unavailable | Verify `CONVEX_URL` is correct |
| Memory spike | `docker-compose logs backend \| tail -20` |

**For more issues:** [TROUBLESHOOTING.md](TROUBLESHOOTING.md)

---

## 📞 Getting Help

1. **Known issues?** → [TROUBLESHOOTING.md](TROUBLESHOOTING.md) (12 scenarios)
2. **Deploy help?** → [DEPLOYMENT.md](DEPLOYMENT.md)
3. **Daily ops?** → [RUNBOOK.md](RUNBOOK.md)
4. **Setup help?** → [RUN.md](RUN.md)
5. **What's done?** → [SESSION_SUMMARY.md](SESSION_SUMMARY.md)

---

## 💡 Pro Tips

- Keep `./monitor.sh` running in a terminal window
- `docker-compose logs -f` shows real-time issues
- `curl -v <endpoint>` shows request/response details
- `docker stats --no-stream` shows resource usage
- Consult [TROUBLESHOOTING.md](TROUBLESHOOTING.md) first

---

**Status:** ✅ READY TO DEPLOY  
**Version:** 1.0.0-rc1  
**Last Updated:** 2025-02-24  

Print this card and keep it handy. 📌
