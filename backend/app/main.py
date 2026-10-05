from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.models.database import init_db
from app.services.sensor_service import sensor_service
from app.api.routes import router as api_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup initialization
    print("Starting Urban Mind Backend Server...")
    init_db()
    # Seed initial sensor data tick if needed
    sensor_service.generate_sensor_tick("normal")
    print("Urban Mind Database & Initial Telemetry Ready.")
    yield
    print("Shutting down Urban Mind Backend Server.")

app = FastAPI(
    title="Urban Mind Backend API",
    description="AI-Powered Smart City Digital Twin REST API Service",
    version="1.0.0",
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
        "title": "Urban Mind API",
        "status": "Online",
        "version": "1.0.0",
        "docs_url": "/docs"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="127.0.0.1", port=8000, reload=True)
