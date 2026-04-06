# AlphaGalleon - Documentation Index

**Quick Links for Everything**

---

## 🚀 Get Started Now (5 minutes)

**Just want to run it?**
```bash
cp .env.example .env          # Fill in your API keys
./start.sh production         # Deploy
./monitor.sh --once           # Check health
```

👉 Then read: [SESSION_SUMMARY.md](SESSION_SUMMARY.md)

---

## 📚 Full Documentation

### For First-Time Visitors
1. **[README.md](README.md)** - Project overview + quick start
2. **[SESSION_SUMMARY.md](SESSION_SUMMARY.md)** - What was completed this session
3. **[CARDS.md](CARDS.md)** - Quick reference card (print this!)

### For DevOps/SRE Team
1. **[DEPLOYMENT.md](DEPLOYMENT.md)** - Deploy to AWS/GCP/Heroku
2. **[RUNBOOK.md](RUNBOOK.md)** - Daily operations + incident response
3. **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Common issues (12 scenarios)

### For Developers
1. **[RUN.md](RUN.md)** - Local development setup
2. **[TROUBLESHOOTING.md](TROUBLESHOOTING.md)** - Common issues
3. **Code:** See `alphagalleon-backend/app/main.py` (13 endpoints documented)

### For Product/Leadership
1. **[SESSION_SUMMARY.md](SESSION_SUMMARY.md)** - What's done (5 min read)
2. **[CARDS.md](CARDS.md)** - Quick reference + checklist
3. **[DEPLOYMENT.md](DEPLOYMENT.md)** - Timeline + resources needed

---

## 🛠️ Automation Scripts

| Script | Purpose | Usage |
|--------|---------|-------|
| **start.sh** | Start AlphaGalleon | `./start.sh [development\|production\|test]` |
| **monitor.sh** | Real-time health monitoring | `./monitor.sh` or `./monitor.sh --once` |
| **test-deployment.sh** | E2E testing (7 categories, 15+ tests) | `bash test-deployment.sh` |

---

## 📖 Documentation by Topic

### Deployment & Operations
| Topic | Document | Read Time |
|-------|----------|-----------|
| How to deploy? | [DEPLOYMENT.md](DEPLOYMENT.md) | 15 min |
| Daily operations? | [RUNBOOK.md](RUNBOOK.md) | 20 min |
| Something broke? | [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | 5+ min |
| Quick reference? | [CARDS.md](CARDS.md) | 3 min |

### Development
| Topic | Document | Read Time |
|-------|----------|-----------|
| Setup locally? | [RUN.md](RUN.md) | 10 min |
| API endpoints? | [README.md](README.md#-api-endpoints-13-total) | 2 min |
| Issues? | [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | 5+ min |

### Project Status
| Topic | Document | Read Time |
|-------|----------|-----------|
| What's done? | [SESSION_SUMMARY.md](SESSION_SUMMARY.md) | 5 min |
| Project overview? | [README.md](README.md) | 10 min |
| Architecture? | [DEPLOYMENT.md](#architecture-diagram) | 3 min |

---

## 🎯 By Use Case

### "I want to deploy this to production"
1. Read: [DEPLOYMENT.md](DEPLOYMENT.md) (15 min)
2. Copy: `.env.example → .env` (fill in keys)
3. Deploy: `./start.sh production`
4. Test: `bash test-deployment.sh`
5. Monitor: `./monitor.sh`
6. Plan: Keep [RUNBOOK.md](RUNBOOK.md) open

### "I want to set up local development"
1. Read: [RUN.md](RUN.md) (10 min)
2. Setup: Follow the steps
3. Run: `./start.sh development`
4. Test: `bash test-deployment.sh`
5. Reference: [TROUBLESHOOTING.md](TROUBLESHOOTING.md) if issues

### "Something is broken, help!"
1. Check: `./monitor.sh --once`
2. Look up: [TROUBLESHOOTING.md](TROUBLESHOOTING.md) (find your error)
3. Follow: The solution steps
4. Verify: `./monitor.sh --once` or `bash test-deployment.sh`

### "I need to understand what's been done"
1. Read: [SESSION_SUMMARY.md](SESSION_SUMMARY.md) (5 min)
2. Check: The completion status table
3. Review: What's in each folder (see [README.md](README.md#-project-structure))

### "I'm managing the product/team"
1. Read: [SESSION_SUMMARY.md](SESSION_SUMMARY.md) (5 min)
2. Print: [CARDS.md](CARDS.md) (quick reference)
3. Bookmark: [DEPLOYMENT.md](DEPLOYMENT.md) (for resource planning)
4. Share: [RUNBOOK.md](RUNBOOK.md) with your ops team

---

## 📋 Quick Answers

**Q: Is this production-ready?**  
A: Yes! 90% complete. See [SESSION_SUMMARY.md](SESSION_SUMMARY.md).

**Q: How do I deploy?**  
A: See [DEPLOYMENT.md](DEPLOYMENT.md) (AWS EC2, GCP, or Heroku).

**Q: How long to get running?**  
A: 5 minutes with `./start.sh production`. Full setup takes ~30 minutes.

**Q: What if something breaks?**  
A: Check [TROUBLESHOOTING.md](TROUBLESHOOTING.md) (covers 12 common issues).

**Q: How do I monitor it?**  
A: Run `./monitor.sh` in a terminal. It continuously checks health.

**Q: What APIs does this call?**  
A: Google Gemini, Upstox (optional), Convex. See [README.md](README.md).

**Q: Is there a guide for daily operations?**  
A: Yes, see [RUNBOOK.md](RUNBOOK.md) (maintenance, incidents, monitoring).

**Q: What are the API endpoints?**  
A: 13 total. See [README.md](README.md#-api-endpoints-13-total).

**Q: How do I backup the database?**  
A: See [RUNBOOK.md](RUNBOOK.md) under "Backup and Recovery".

**Q: What should I check before going live?**  
A: See [CARDS.md](CARDS.md) "Production Checklist" section.

---

## 📊 Status at a Glance

| Component | Status | Doc |
|-----------|--------|-----|
| Backend (13 endpoints) | ✅ Complete | [README.md](README.md) |
| Mobile (5 screens) | ✅ Complete | [README.md](README.md) |
| Admin Dashboard (3 pages) | ✅ Complete | [README.md](README.md) |
| Authentication | ✅ Complete | [README.md](README.md) |
| Docker & Deployment | ✅ Complete | [DEPLOYMENT.md](DEPLOYMENT.md) |
| CI/CD Pipeline | ✅ Complete | [DEPLOYMENT.md](DEPLOYMENT.md) |
| Testing (E2E) | ✅ Complete | [README.md](README.md) |
| Documentation | ✅ Complete | This page |

**Overall: 90% Complete (Production Ready)**

---

## 🗂️ File Structure

```
AlphaGalleon/
├── 📖 Documentation (Start here)
│   ├── README.md                    ← Project overview
│   ├── SESSION_SUMMARY.md           ← What was done
│   ├── DEPLOYMENT.md                ← How to deploy
│   ├── RUNBOOK.md                   ← Daily operations
│   ├── TROUBLESHOOTING.md           ← Common issues (12 scenarios)
│   ├── RUN.md                       ← Local development
│   ├── CARDS.md                     ← Quick reference card
│   └── INDEX.md                     ← You are here
│
├── 🚀 Automation Scripts
│   ├── start.sh                     ← Startup automation
│   ├── monitor.sh                   ← Health monitoring
│   └── test-deployment.sh           ← E2E testing
│
├── 🏗️ Backend API
│   ├── alphagalleon-backend/
│   │   ├── app/main.py              ← 13 REST endpoints
│   │   ├── app/brain.py             ← AI memo generation
│   │   ├── app/doctor.py            ← Portfolio diagnostics
│   │   ├── app/architect.py         ← Portfolio optimization
│   │   ├── app/scout.py             ← Market data
│   │   └── app/auth.py              ← JWT authentication
│   └── requirements.txt
│
├── 📱 Mobile Frontend
│   └── mobile/src/                  ← 5 screens + API client
│
├── 💼 Admin Dashboard
│   └── admin-dashboard/src/         ← 3 pages + API client
│
├── 🗄️ Database Schema
│   └── convex/                      ← Serverless DB
│
├── 🐳 Docker & Deployment
│   ├── Dockerfile                   ← Container image
│   ├── docker-compose.yml           ← Dev config
│   ├── docker-compose.prod.yml      ← Production config
│   ├── .env.example                 ← Config template
│   └── .github/workflows/ci-cd.yml  ← GitHub Actions
│
└── 📝 Config Files
    ├── package.json                 ← Node dependencies
    └── [other configs]
```

---

## 🔍 Finding What You Need

**By Department:**
- **Engineering:** [README.md](README.md) → [RUN.md](RUN.md) → [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **DevOps/SRE:** [DEPLOYMENT.md](DEPLOYMENT.md) → [RUNBOOK.md](RUNBOOK.md) → [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- **Product:** [SESSION_SUMMARY.md](SESSION_SUMMARY.md) → [CARDS.md](CARDS.md)
- **Leadership:** [SESSION_SUMMARY.md](SESSION_SUMMARY.md) → [DEPLOYMENT.md](DEPLOYMENT.md) (Resources section)

**By Activity:**
- Deploying? → [DEPLOYMENT.md](DEPLOYMENT.md)
- Running locally? → [RUN.md](RUN.md)
- Something's broken? → [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Daily operations? → [RUNBOOK.md](RUNBOOK.md)
- Want a printable reference? → [CARDS.md](CARDS.md)

---

## ⏱️ Reading Time Estimates

| Document | Time | Best For |
|----------|------|----------|
| [SESSION_SUMMARY.md](SESSION_SUMMARY.md) | 5 min | Everyone - status update |
| [CARDS.md](CARDS.md) | 3 min | Quick reference |
| [README.md](README.md) | 10 min | Project overview |
| [RUN.md](RUN.md) | 10 min | Local setup |
| [DEPLOYMENT.md](DEPLOYMENT.md) | 15 min | Before deploying |
| [RUNBOOK.md](RUNBOOK.md) | 20 min | Ops team training |
| [TROUBLESHOOTING.md](TROUBLESHOOTING.md) | 5+ min | When debugging |

**Total onboarding:** ~30 minutes for a new team member.

---

## ✅ Completion Checklist

Before opening to users:

- [ ] Read [SESSION_SUMMARY.md](SESSION_SUMMARY.md) (5 min)
- [ ] Run `./start.sh production` (5 min)
- [ ] Run `bash test-deployment.sh` (2 min)
- [ ] Verify `./monitor.sh --once` is all green (1 min)
- [ ] Share [DEPLOYMENT.md](DEPLOYMENT.md) with DevOps
- [ ] Share [RUNBOOK.md](RUNBOOK.md) with Ops team
- [ ] Print [CARDS.md](CARDS.md) for quick reference
- [ ] Setup monitoring dashboard
- [ ] Document team's custom procedures
- [ ] ✅ Ready to go live!

---

## 🔗 Quick Links

**Essential Docs:**
- Main project README: [README.md](README.md)
- Session summary: [SESSION_SUMMARY.md](SESSION_SUMMARY.md)
- Quick reference: [CARDS.md](CARDS.md)

**Setup & Deployment:**
- Local development: [RUN.md](RUN.md)
- Production deployment: [DEPLOYMENT.md](DEPLOYMENT.md)
- Operations guide: [RUNBOOK.md](RUNBOOK.md)

**Troubleshooting:**
- Common issues: [TROUBLESHOOTING.md](TROUBLESHOOTING.md)
- Operations runbook: [RUNBOOK.md](RUNBOOK.md)

**Automation:**
- Startup script: `./start.sh`
- Monitoring script: `./monitor.sh`
- Testing script: `bash test-deployment.sh`

---

**Status:** ✅ Documentation Complete  
**Version:** 1.0.0-rc1  
**Last Updated:** 2025-02-24  

**Next Step:** Pick your role (DevOps/Developer/Product) and follow the appropriate documentation above.
