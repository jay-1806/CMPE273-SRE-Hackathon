"""
Configuration management for the SRE Dashboard
"""
import os
from typing import List
from dotenv import load_dotenv

# Load environment variables
load_dotenv()


class Settings:
    """Application settings"""

    # Application
    APP_NAME: str = os.getenv("APP_NAME", "SRE Tier-0 Monitoring Dashboard")
    APP_VERSION: str = os.getenv("APP_VERSION", "1.0.0")
    ENVIRONMENT: str = os.getenv("ENVIRONMENT", "development")
    DEBUG: bool = os.getenv("DEBUG", "True").lower() == "true"

    # Server
    HOST: str = os.getenv("HOST", "0.0.0.0")
    PORT: int = int(os.getenv("PORT", "8000"))

    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", "hackathon-secret-key-change-in-production")
    ALGORITHM: str = os.getenv("ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "30"))

    # Redis
    REDIS_HOST: str = os.getenv("REDIS_HOST", "localhost")
    REDIS_PORT: int = int(os.getenv("REDIS_PORT", "6379"))
    REDIS_DB: int = int(os.getenv("REDIS_DB", "0"))
    REDIS_PASSWORD: str = os.getenv("REDIS_PASSWORD", "")
    USE_REDIS: bool = os.getenv("USE_REDIS", "false").lower() == "true"

    # MQTT
    MQTT_BROKER_HOST: str = os.getenv("MQTT_BROKER_HOST", "localhost")
    MQTT_BROKER_PORT: int = int(os.getenv("MQTT_BROKER_PORT", "1883"))
    MQTT_USERNAME: str = os.getenv("MQTT_USERNAME", "")
    MQTT_PASSWORD: str = os.getenv("MQTT_PASSWORD", "")
    MQTT_TOPIC_PREFIX: str = os.getenv("MQTT_TOPIC_PREFIX", "iot/devices")

    # Cohere AI
    COHERE_API_KEY: str = os.getenv("COHERE_API_KEY", "")
    COHERE_MODEL: str = os.getenv("COHERE_MODEL", "command-r-plus")

    # IoT Device Simulation
    NUM_SITES: int = int(os.getenv("NUM_SITES", "10"))
    DEVICES_PER_SITE: int = int(os.getenv("DEVICES_PER_SITE", "10000"))
    TOTAL_DEVICES: int = int(os.getenv("TOTAL_DEVICES", "100000"))
    DEVICE_TYPES: List[str] = os.getenv("DEVICE_TYPES", "Turbine,ThermalEngine,ElectricalRotor,OilAndGas").split(",")

    # Regions
    PRIMARY_REGION: str = os.getenv("PRIMARY_REGION", "region1")
    SECONDARY_REGION: str = os.getenv("SECONDARY_REGION", "region2")
    FAILOVER_THRESHOLD_MS: int = int(os.getenv("FAILOVER_THRESHOLD_MS", "5000"))

    # Monitoring
    METRICS_INTERVAL_SECONDS: int = int(os.getenv("METRICS_INTERVAL_SECONDS", "5"))
    LOG_LEVEL: str = os.getenv("LOG_LEVEL", "INFO")
    ENABLE_METRICS: bool = os.getenv("ENABLE_METRICS", "true").lower() == "true"

    # Logging
    LOG_FILE_PATH: str = os.getenv("LOG_FILE_PATH", "data/logs/app.log")
    SAMPLE_LOG_PATH: str = os.getenv("SAMPLE_LOG_PATH", "sample_log.txt")


settings = Settings()
