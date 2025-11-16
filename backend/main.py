"""
Main FastAPI application for SRE Tier-0 Monitoring Dashboard
"""
from fastapi import FastAPI, Request
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
import os
import logging
from backend.core.config import settings
from backend.api import auth, devices, monitoring
from backend.services.mqtt_simulator import mqtt_simulator

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Enterprise SRE Tier-0 Monitoring Dashboard for IoT Devices",
    docs_url="/api/docs",
    redoc_url="/api/redoc"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="frontend/static"), name="static")

# Templates
templates = Jinja2Templates(directory="frontend/templates")

# Include routers
app.include_router(auth.router)
app.include_router(devices.router)
app.include_router(monitoring.router)


@app.on_event("startup")
async def startup_event():
    """Initialize services on startup"""
    logger.info(f"Starting {settings.APP_NAME} v{settings.APP_VERSION}")
    logger.info(f"Environment: {settings.ENVIRONMENT}")

    # Initialize MQTT simulator with devices
    if len(mqtt_simulator.devices) == 0:
        logger.info("Initializing IoT devices...")
        mqtt_simulator.initialize_devices()
        logger.info(f"✓ Initialized {len(mqtt_simulator.devices)} devices")

    logger.info("✓ Application startup complete")


@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup on shutdown"""
    logger.info("Shutting down application...")


@app.get("/", response_class=HTMLResponse)
async def root(request: Request):
    """Serve the main dashboard page"""
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/login", response_class=HTMLResponse)
async def login_page(request: Request):
    """Serve the login page"""
    return templates.TemplateResponse("login.html", {"request": request})


@app.get("/api")
async def api_info():
    """API information endpoint"""
    return {
        "name": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "docs": "/api/docs",
        "endpoints": {
            "authentication": "/api/auth",
            "devices": "/api/devices",
            "monitoring": "/api/monitoring"
        }
    }


@app.get("/api/status")
async def system_status():
    """System status endpoint"""
    return {
        "status": "operational",
        "services": {
            "mqtt_simulator": len(mqtt_simulator.devices) > 0,
            "redis": settings.USE_REDIS,
            "cohere_ai": bool(settings.COHERE_API_KEY)
        },
        "metrics": {
            "total_devices": len(mqtt_simulator.devices),
            "total_sites": settings.NUM_SITES,
            "device_types": settings.DEVICE_TYPES
        }
    }


if __name__ == "__main__":
    import uvicorn

    # Ensure directories exist
    os.makedirs("data/logs", exist_ok=True)
    os.makedirs("images", exist_ok=True)

    uvicorn.run(
        "backend.main:app",
        host=settings.HOST,
        port=settings.PORT,
        reload=settings.DEBUG,
        log_level=settings.LOG_LEVEL.lower()
    )
