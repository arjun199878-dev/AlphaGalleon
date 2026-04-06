from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.api import brain, market

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="AlphaGalleon Backend: The Brain (Gemini 2.5 Flash + Market Data)"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, replace with specific origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(brain.router, prefix="/api/v1/brain", tags=["brain"])
app.include_router(market.router, prefix="/api/v1/market", tags=["market"])

@app.get("/")
async def root():
    return {
        "system": "AlphaGalleon Brain",
        "status": "online",
        "version": settings.VERSION
    }

@app.get("/health")
async def health_check():
    return {"status": "healthy"}
