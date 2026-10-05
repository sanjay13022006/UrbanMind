from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.models.database import init_db
from app.services.data_ingestion_service import data_ingestion_service
from app.api.routes import router as api_router
from app import config

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("=" * 60)
    print("Starting UrbanTwin AI Smart City Digital Twin Backend...")
    print(f"Configured City: {config.CITY_NAME} ({config.LATITUDE}, {config.LONGITUDE})")
    init_db()
    
    print("Ingesting initial real-time telemetry from external APIs...")
    try:
        data_ingestion_service.ingest_data(force_refresh=True)
        sources = data_ingestion_service.get_data_sources_status()
        for s in sources:
            print(f"  • {s['name']}: {s.get('status', 'connected').upper()} [{s.get('coverage', '')}]")
    except Exception as e:
        print(f"Warning during initial data ingestion: {e}")

    print("UrbanTwin AI Database & Real API Telemetry Online.")
    print("=" * 60)
    yield
    print("Shutting down UrbanTwin AI Backend Server.")

app = FastAPI(
    title="UrbanTwin AI Backend API",
    description="Real API-Integrated Smart City Digital Twin REST API Service",
    version="2.0.0",
    lifespan=lifespan
)

# Enable CORS for React Vite frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router, prefix="/api")

@app.get("/")
def root():
    return {
        "title": "UrbanTwin AI API",
        "city": config.CITY_NAME,
        "mode": data_ingestion_service.app_mode,
        "status": "Online",
        "version": "2.0.0",
        "docs_url": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
