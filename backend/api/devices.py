"""
Device monitoring API endpoints
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from typing import List, Optional
from backend.models.user import User
from backend.utils.security import get_current_active_user
from backend.services.mqtt_simulator import mqtt_simulator

router = APIRouter(prefix="/api/devices", tags=["Devices"])


@router.get("/summary")
async def get_dashboard_summary(current_user: User = Depends(get_current_active_user)):
    """Get overall dashboard summary"""
    return mqtt_simulator.get_dashboard_summary()


@router.get("/device/{device_id}")
async def get_device_telemetry(
    device_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get telemetry for a specific device"""
    telemetry = mqtt_simulator.get_device_telemetry(device_id)

    if "error" in telemetry:
        raise HTTPException(status_code=404, detail=telemetry["error"])

    return telemetry


@router.get("/site/{site_id}")
async def get_site_telemetry(
    site_id: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get aggregated telemetry for a site"""
    telemetry = mqtt_simulator.get_site_telemetry(site_id)

    if "error" in telemetry:
        raise HTTPException(status_code=404, detail=telemetry["error"])

    return telemetry


@router.get("/sites")
async def get_all_sites(current_user: User = Depends(get_current_active_user)):
    """Get summary for all sites"""
    return mqtt_simulator.get_all_sites_summary()


@router.get("/region/{region}")
async def get_region_status(
    region: str,
    current_user: User = Depends(get_current_active_user)
):
    """Get status for a specific region"""
    status = mqtt_simulator.get_region_status(region)

    if "error" in status:
        raise HTTPException(status_code=404, detail=status["error"])

    return status


@router.post("/failover")
async def simulate_failover(
    from_region: str = Query(..., description="Source region"),
    to_region: str = Query(..., description="Target region"),
    current_user: User = Depends(get_current_active_user)
):
    """Simulate failover between regions"""
    result = mqtt_simulator.simulate_failover(from_region, to_region)
    return result


@router.get("/search")
async def search_devices(
    device_type: Optional[str] = None,
    site_id: Optional[str] = None,
    region: Optional[str] = None,
    status: Optional[str] = None,
    limit: int = Query(100, le=1000),
    current_user: User = Depends(get_current_active_user)
):
    """Search devices by criteria"""
    from backend.services.mqtt_simulator import device_registry

    devices = list(device_registry.values())

    # Apply filters
    if device_type:
        devices = [d for d in devices if d.device_type == device_type]

    if site_id:
        devices = [d for d in devices if d.site_id == site_id]

    if region:
        devices = [d for d in devices if d.region == region]

    if status:
        devices = [d for d in devices if d.status.value == status]

    # Limit results
    devices = devices[:limit]

    return {
        "total": len(devices),
        "devices": [d.generate_telemetry() for d in devices]
    }


@router.post("/initialize")
async def initialize_devices(current_user: User = Depends(get_current_active_user)):
    """Initialize all IoT devices (call this once at startup)"""
    if len(mqtt_simulator.devices) == 0:
        mqtt_simulator.initialize_devices()
        return {
            "message": "Devices initialized successfully",
            "total_devices": len(mqtt_simulator.devices)
        }
    else:
        return {
            "message": "Devices already initialized",
            "total_devices": len(mqtt_simulator.devices)
        }
