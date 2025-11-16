"""
Device models for IoT monitoring
"""
from pydantic import BaseModel
from typing import Optional, Dict, Any
from datetime import datetime
from enum import Enum


class DeviceType(str, Enum):
    """Device types"""
    TURBINE = "Turbine"
    THERMAL_ENGINE = "ThermalEngine"
    ELECTRICAL_ROTOR = "ElectricalRotor"
    OIL_AND_GAS = "OilAndGas"


class DeviceStatus(str, Enum):
    """Device status"""
    ONLINE = "online"
    OFFLINE = "offline"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"


class Device(BaseModel):
    """Device model"""
    device_id: str
    device_type: DeviceType
    site_id: str
    region: str
    status: DeviceStatus
    temperature: Optional[float] = None
    pressure: Optional[float] = None
    vibration: Optional[float] = None
    power_output: Optional[float] = None
    efficiency: Optional[float] = None
    last_updated: datetime
    metadata: Optional[Dict[str, Any]] = {}


class DeviceMetrics(BaseModel):
    """Device metrics model"""
    device_id: str
    timestamp: datetime
    cpu_usage: Optional[float] = None
    memory_usage: Optional[float] = None
    network_latency: Optional[float] = None
    error_count: int = 0
    warning_count: int = 0


class SiteMetrics(BaseModel):
    """Site-level aggregated metrics"""
    site_id: str
    region: str
    total_devices: int
    online_devices: int
    offline_devices: int
    warning_devices: int
    error_devices: int
    avg_temperature: Optional[float] = None
    avg_pressure: Optional[float] = None
    avg_efficiency: Optional[float] = None
    last_updated: datetime


class RegionStatus(BaseModel):
    """Region status model"""
    region: str
    is_active: bool
    total_sites: int
    total_devices: int
    healthy_devices: int
    unhealthy_devices: int
    avg_latency_ms: float
    last_failover: Optional[datetime] = None
