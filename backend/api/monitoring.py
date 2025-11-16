"""
Monitoring and analytics API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query, UploadFile, File
from typing import Optional
import os
from backend.models.user import User
from backend.utils.security import get_current_active_user
from backend.services.log_analyzer import log_analyzer
from backend.services.cohere_service import cohere_service
from backend.core.config import settings

router = APIRouter(prefix="/api/monitoring", tags=["Monitoring"])


@router.get("/logs/analyze")
async def analyze_logs(
    log_file: Optional[str] = None,
    current_user: User = Depends(get_current_active_user)
):
    """Analyze log file and find top error IPs"""
    # Use provided log file or default
    file_path = log_file or settings.SAMPLE_LOG_PATH

    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404,
            detail=f"Log file not found: {file_path}"
        )

    analysis = log_analyzer.analyze_log_file(file_path)

    if "error" in analysis:
        raise HTTPException(status_code=500, detail=analysis["error"])

    return analysis


@router.get("/logs/ip/{ip_address}")
async def get_ip_details(
    ip_address: str,
    log_file: Optional[str] = None,
    current_user: User = Depends(get_current_active_user)
):
    """Get detailed information about a specific IP"""
    file_path = log_file or settings.SAMPLE_LOG_PATH

    if not os.path.exists(file_path):
        raise HTTPException(
            status_code=404,
            detail=f"Log file not found: {file_path}"
        )

    details = log_analyzer.get_ip_details(file_path, ip_address)

    if "error" in details:
        raise HTTPException(status_code=500, detail=details["error"])

    return details


@router.post("/logs/generate-sample")
async def generate_sample_log(
    num_lines: int = Query(1000, le=100000),
    current_user: User = Depends(get_current_active_user)
):
    """Generate a sample log file for testing"""
    result = log_analyzer.generate_sample_log(
        output_path=settings.SAMPLE_LOG_PATH,
        num_lines=num_lines
    )

    return {"message": result, "file_path": settings.SAMPLE_LOG_PATH}


@router.post("/ai/analyze-image")
async def analyze_image(
    image_name: str = Query(..., description="Image filename in images/ folder"),
    query: str = Query("Analyze this device image", description="Analysis query"),
    current_user: User = Depends(get_current_active_user)
):
    """Analyze a device image using Cohere AI"""
    image_path = os.path.join("images", image_name)

    if not os.path.exists(image_path):
        raise HTTPException(
            status_code=404,
            detail=f"Image not found: {image_path}"
        )

    analysis = cohere_service.analyze_image(image_path, query)

    return analysis


@router.post("/ai/query")
async def natural_language_query(
    query: str = Query(..., description="Natural language query"),
    include_context: bool = Query(True, description="Include system context"),
    current_user: User = Depends(get_current_active_user)
):
    """Process natural language queries about the system"""
    context = None

    if include_context:
        # Get current system state as context
        from backend.services.mqtt_simulator import mqtt_simulator
        context = mqtt_simulator.get_dashboard_summary()

    response = cohere_service.natural_language_query(query, context)

    return response


@router.post("/ai/summarize-metrics")
async def summarize_metrics(
    current_user: User = Depends(get_current_active_user)
):
    """Generate AI summary of current metrics"""
    from backend.services.mqtt_simulator import mqtt_simulator

    metrics = mqtt_simulator.get_dashboard_summary()
    summary = cohere_service.summarize_metrics(metrics)

    return {
        "summary": summary,
        "metrics": metrics
    }


@router.post("/ai/device-health")
async def analyze_device_health(
    device_id: str = Query(..., description="Device ID to analyze"),
    current_user: User = Depends(get_current_active_user)
):
    """Analyze device health using AI"""
    from backend.services.mqtt_simulator import mqtt_simulator

    device_data = mqtt_simulator.get_device_telemetry(device_id)

    if "error" in device_data:
        raise HTTPException(status_code=404, detail=device_data["error"])

    health_analysis = cohere_service.analyze_device_health(device_data)

    return {
        "device_id": device_id,
        "health_analysis": health_analysis,
        "current_metrics": device_data
    }


@router.get("/metrics/export")
async def export_metrics(
    format: str = Query("json", regex="^(json|csv)$"),
    current_user: User = Depends(get_current_active_user)
):
    """Export current metrics in various formats"""
    from backend.services.mqtt_simulator import mqtt_simulator
    import json
    import csv
    from io import StringIO

    metrics = mqtt_simulator.get_dashboard_summary()

    if format == "json":
        return metrics
    elif format == "csv":
        # Convert to CSV
        output = StringIO()
        writer = csv.writer(output)

        # Write headers
        writer.writerow(["Metric", "Value"])

        # Write data
        for key, value in metrics.items():
            if not isinstance(value, (dict, list)):
                writer.writerow([key, value])

        return {"csv_data": output.getvalue()}


@router.get("/health")
async def health_check():
    """Health check endpoint (no auth required)"""
    from backend.services.mqtt_simulator import mqtt_simulator

    return {
        "status": "healthy",
        "devices_initialized": len(mqtt_simulator.devices) > 0,
        "total_devices": len(mqtt_simulator.devices)
    }
