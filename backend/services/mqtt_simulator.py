"""
MQTT simulator for 100,000 IoT devices across 10 sites
"""
import json
import random
import time
from datetime import datetime
from typing import Dict, Any, List
from backend.core.config import settings
from backend.models.device import DeviceType, DeviceStatus

# In-memory device registry
device_registry = {}
site_metrics = {}
region_status = {
    settings.PRIMARY_REGION: {"is_active": True, "latency_ms": 50},
    settings.SECONDARY_REGION: {"is_active": False, "latency_ms": 75}
}


class DeviceSimulator:
    """Simulates IoT device behavior"""

    def __init__(self, device_id: str, device_type: str, site_id: str, region: str):
        self.device_id = device_id
        self.device_type = device_type
        self.site_id = site_id
        self.region = region
        self.status = DeviceStatus.ONLINE

        # Initialize baseline metrics based on device type
        self.metrics = self._initialize_metrics()

    def _initialize_metrics(self) -> Dict[str, float]:
        """Initialize device-specific baseline metrics"""
        baselines = {
            "Turbine": {
                "temperature": 75.0,
                "pressure": 120.0,
                "vibration": 0.5,
                "power_output": 2500.0,
                "efficiency": 92.0,
            },
            "ThermalEngine": {
                "temperature": 450.0,
                "pressure": 200.0,
                "vibration": 0.8,
                "power_output": 5000.0,
                "efficiency": 88.0,
            },
            "ElectricalRotor": {
                "temperature": 60.0,
                "pressure": 50.0,
                "vibration": 0.3,
                "power_output": 1500.0,
                "efficiency": 95.0,
            },
            "OilAndGas": {
                "temperature": 90.0,
                "pressure": 300.0,
                "vibration": 1.0,
                "power_output": 3500.0,
                "efficiency": 85.0,
            }
        }
        return baselines.get(self.device_type, baselines["Turbine"]).copy()

    def generate_telemetry(self) -> Dict[str, Any]:
        """Generate realistic telemetry data"""
        # Add random variations (±5%)
        telemetry = {}
        for key, value in self.metrics.items():
            variation = random.uniform(-0.05, 0.05)
            telemetry[key] = round(value * (1 + variation), 2)

        # Randomly introduce anomalies (5% chance)
        if random.random() < 0.05:
            self.status = random.choice([DeviceStatus.WARNING, DeviceStatus.ERROR])
            # Spike in temperature or pressure
            if random.random() < 0.5:
                telemetry["temperature"] *= 1.3
            else:
                telemetry["pressure"] *= 1.2
        else:
            self.status = DeviceStatus.ONLINE

        # Occasionally simulate offline devices (1% chance)
        if random.random() < 0.01:
            self.status = DeviceStatus.OFFLINE

        return {
            "device_id": self.device_id,
            "device_type": self.device_type,
            "site_id": self.site_id,
            "region": self.region,
            "status": self.status.value,
            "timestamp": datetime.now().isoformat(),
            **telemetry
        }


class MQTTSimulator:
    """MQTT simulator for managing all IoT devices"""

    def __init__(self):
        self.devices: List[DeviceSimulator] = []
        self.is_running = False
        self.message_count = 0

    def initialize_devices(self):
        """Initialize all 100,000 devices across 10 sites"""
        print(f"Initializing {settings.TOTAL_DEVICES} devices across {settings.NUM_SITES} sites...")

        device_id_counter = 1
        for site_num in range(1, settings.NUM_SITES + 1):
            site_id = f"site-{site_num:02d}"
            region = settings.PRIMARY_REGION if site_num <= 5 else settings.SECONDARY_REGION

            # Distribute devices evenly across device types
            devices_per_type = settings.DEVICES_PER_SITE // len(settings.DEVICE_TYPES)

            for device_type in settings.DEVICE_TYPES:
                for _ in range(devices_per_type):
                    device_id = f"device-{device_id_counter:06d}"
                    device = DeviceSimulator(device_id, device_type, site_id, region)
                    self.devices.append(device)

                    # Register in global registry
                    device_registry[device_id] = device

                    device_id_counter += 1

        print(f"✓ Initialized {len(self.devices)} devices")
        self._update_site_metrics()

    def _update_site_metrics(self):
        """Update aggregated site metrics"""
        site_data = {}

        for device in self.devices:
            if device.site_id not in site_data:
                site_data[device.site_id] = {
                    "site_id": device.site_id,
                    "region": device.region,
                    "devices": [],
                    "online": 0,
                    "offline": 0,
                    "warning": 0,
                    "error": 0,
                }

            site_data[device.site_id]["devices"].append(device)

            if device.status == DeviceStatus.ONLINE:
                site_data[device.site_id]["online"] += 1
            elif device.status == DeviceStatus.OFFLINE:
                site_data[device.site_id]["offline"] += 1
            elif device.status == DeviceStatus.WARNING:
                site_data[device.site_id]["warning"] += 1
            elif device.status in [DeviceStatus.ERROR, DeviceStatus.CRITICAL]:
                site_data[device.site_id]["error"] += 1

        global site_metrics
        site_metrics = site_data

    def get_device_telemetry(self, device_id: str) -> Dict[str, Any]:
        """Get telemetry for a specific device"""
        if device_id in device_registry:
            return device_registry[device_id].generate_telemetry()
        return {"error": "Device not found"}

    def get_site_telemetry(self, site_id: str) -> Dict[str, Any]:
        """Get aggregated telemetry for a site"""
        if site_id not in site_metrics:
            return {"error": "Site not found"}

        site_data = site_metrics[site_id]
        devices = site_data["devices"]

        # Calculate averages
        avg_temp = sum(d.metrics.get("temperature", 0) for d in devices) / len(devices)
        avg_pressure = sum(d.metrics.get("pressure", 0) for d in devices) / len(devices)
        avg_efficiency = sum(d.metrics.get("efficiency", 0) for d in devices) / len(devices)

        return {
            "site_id": site_id,
            "region": site_data["region"],
            "total_devices": len(devices),
            "online_devices": site_data["online"],
            "offline_devices": site_data["offline"],
            "warning_devices": site_data["warning"],
            "error_devices": site_data["error"],
            "avg_temperature": round(avg_temp, 2),
            "avg_pressure": round(avg_pressure, 2),
            "avg_efficiency": round(avg_efficiency, 2),
            "last_updated": datetime.now().isoformat()
        }

    def get_all_sites_summary(self) -> List[Dict[str, Any]]:
        """Get summary for all sites"""
        self._update_site_metrics()
        return [self.get_site_telemetry(site_id) for site_id in site_metrics.keys()]

    def get_region_status(self, region: str) -> Dict[str, Any]:
        """Get status for a specific region"""
        if region not in region_status:
            return {"error": "Region not found"}

        # Count devices in this region
        region_devices = [d for d in self.devices if d.region == region]
        healthy = sum(1 for d in region_devices if d.status == DeviceStatus.ONLINE)

        # Count sites in this region
        region_sites = set(d.site_id for d in region_devices)

        return {
            "region": region,
            "is_active": region_status[region]["is_active"],
            "total_sites": len(region_sites),
            "total_devices": len(region_devices),
            "healthy_devices": healthy,
            "unhealthy_devices": len(region_devices) - healthy,
            "avg_latency_ms": region_status[region]["latency_ms"],
            "last_failover": None
        }

    def simulate_failover(self, from_region: str, to_region: str) -> Dict[str, Any]:
        """Simulate failover between regions"""
        print(f"Simulating failover from {from_region} to {to_region}...")

        # Update region status
        region_status[from_region]["is_active"] = False
        region_status[to_region]["is_active"] = True
        region_status[to_region]["latency_ms"] = random.randint(100, 200)

        # Simulate device reconnection (in reality, devices would reconnect to new region)
        failover_time = datetime.now()

        return {
            "success": True,
            "from_region": from_region,
            "to_region": to_region,
            "failover_time": failover_time.isoformat(),
            "affected_devices": len([d for d in self.devices if d.region == from_region]),
            "new_active_region": to_region
        }

    def get_dashboard_summary(self) -> Dict[str, Any]:
        """Get comprehensive dashboard summary"""
        self._update_site_metrics()

        total_online = sum(1 for d in self.devices if d.status == DeviceStatus.ONLINE)
        total_offline = sum(1 for d in self.devices if d.status == DeviceStatus.OFFLINE)
        total_warning = sum(1 for d in self.devices if d.status == DeviceStatus.WARNING)
        total_error = sum(1 for d in self.devices if d.status in [DeviceStatus.ERROR, DeviceStatus.CRITICAL])

        return {
            "total_devices": len(self.devices),
            "online": total_online,
            "offline": total_offline,
            "warning": total_warning,
            "error": total_error,
            "health_percentage": round(total_online / len(self.devices) * 100, 2) if self.devices else 0,
            "total_sites": settings.NUM_SITES,
            "regions": {
                settings.PRIMARY_REGION: self.get_region_status(settings.PRIMARY_REGION),
                settings.SECONDARY_REGION: self.get_region_status(settings.SECONDARY_REGION)
            },
            "device_type_distribution": {
                dtype: len([d for d in self.devices if d.device_type == dtype])
                for dtype in settings.DEVICE_TYPES
            },
            "last_updated": datetime.now().isoformat()
        }


# Global simulator instance
mqtt_simulator = MQTTSimulator()
