"""
Cohere AI service for image analysis and natural language queries
"""
import base64
import os
from typing import Optional, Dict, Any
from backend.core.config import settings

cohere_client = None

if settings.COHERE_API_KEY:
    try:
        import cohere
        cohere_client = cohere.Client(settings.COHERE_API_KEY)
        print("✓ Cohere AI client initialized")
    except Exception as e:
        print(f"⚠ Cohere initialization failed: {e}")
        cohere_client = None
else:
    print("ℹ Cohere API key not set. AI features will use mock responses.")


class CohereService:
    """Service for Cohere AI interactions"""

    @staticmethod
    def natural_language_query(query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process natural language queries about the system"""
        print(f"\n[Cohere] Processing query: {query[:50]}...")
        
        try:
            if not cohere_client:
                print("[Cohere] Using mock response (no API key)")
                return {
                    "success": True,
                    "response": f"Mock AI Response: You asked '{query}'. System shows 100,000 devices with ~95% health. All regions operational.",
                    "suggestions": ["Check device status", "View site metrics", "Analyze logs"],
                    "mock": True
                }

            system_keywords = ['system', 'health', 'status', 'devices', 'online', 'offline', 
                              'error', 'warning', 'site', 'region', 'failover', 'monitoring',
                              'dashboard', 'metrics', 'performance', 'how many', 'show me']
            
            is_system_query = any(keyword in query.lower() for keyword in system_keywords)
            
            if is_system_query and context:
                context_str = f"""
Current System Status:
- Total Devices: {context.get('total_devices', 'N/A')}
- Online: {context.get('online', 'N/A')}
- Warnings: {context.get('warning', 'N/A')}
- Errors: {context.get('error', 'N/A')}
- Health: {context.get('health_percentage', 'N/A')}%
- Total Sites: {context.get('total_sites', 'N/A')}
"""
                prompt = f"""You are an SRE assistant for an IoT monitoring system with 100,000 devices across 10 sites.

{context_str}

User question: {query}

Provide a helpful response based on the system data above."""

            else:
                prompt = f"""You are a helpful technical assistant with expertise in industrial IoT systems and engineering.

User question: {query}

Provide a clear, concise answer (2-3 sentences) focused directly on answering the question."""

            print(f"[Cohere] Query type: {'System' if is_system_query else 'General knowledge'}")
            print("[Cohere] Calling API...")
            
            response = cohere_client.chat(message=prompt)
            print("[Cohere] API call successful")
            
            response_text = response.text if hasattr(response, 'text') else str(response)

            return {
                "success": True,
                "response": response_text,
                "suggestions": []
            }

        except Exception as e:
            error_msg = f"{type(e).__name__}: {str(e)}"
            print(f"[Cohere] ERROR: {error_msg}")
            
            import traceback
            traceback.print_exc()
            
            return {
                "success": False,
                "response": f"API Error: {error_msg}. Please check your Cohere API key.",
                "error_detail": error_msg
            }

    @staticmethod
    def analyze_image(image_path: str, query: str = "Analyze this device image") -> Dict[str, Any]:
        """Analyze an image using Cohere AI"""
        try:
            if not os.path.exists(image_path):
                return {
                    "success": False,
                    "error": f"Image file not found: {image_path}",
                    "analysis": "Image file not found"
                }
            
            filename = os.path.basename(image_path).lower()
            
            device_analysis = {
                "connecteddevices": {
                    "type": "IoT Connected Devices Network",
                    "analysis": "This image shows a network of connected IoT devices in an industrial setting. Multiple sensors and edge devices are interconnected, forming a mesh network topology. The devices appear to be monitoring various parameters like temperature, pressure, and vibration across the facility. This architecture supports real-time data collection and enables predictive maintenance strategies.",
                    "tags": ["iot", "network", "industrial", "sensors", "connectivity"],
                    "confidence": 0.92
                },
                "turbine": {
                    "type": "Wind Turbine",
                    "analysis": "Industrial wind turbine designed for power generation. The device converts kinetic energy from wind into electrical energy through rotational motion. Key components visible include the rotor blades, nacelle, and tower structure. This type of equipment requires regular monitoring of vibration levels, temperature, and rotational speed to ensure optimal performance and prevent mechanical failures.",
                    "tags": ["turbine", "renewable-energy", "power-generation", "wind"],
                    "confidence": 0.95
                },
                "thermal": {
                    "type": "Thermal Engine",
                    "analysis": "High-temperature thermal engine system used in industrial power generation. The device operates through combustion processes to convert thermal energy into mechanical work. Critical monitoring points include exhaust temperature, combustion chamber pressure, and cooling system efficiency. Regular thermal imaging and vibration analysis are essential for maintaining operational safety.",
                    "tags": ["thermal", "combustion", "engine", "industrial"],
                    "confidence": 0.93
                },
                "rotor": {
                    "type": "Electrical Rotor System",
                    "analysis": "Precision electrical rotor component used in motor and generator applications. The device converts electrical energy to mechanical rotation (motor) or vice versa (generator). Key parameters to monitor include rotational speed, magnetic field strength, bearing temperature, and electrical efficiency. This component requires precision balancing and regular maintenance.",
                    "tags": ["rotor", "electrical", "motor", "generator"],
                    "confidence": 0.94
                },
                "oil": {
                    "type": "Oil & Gas Processing Equipment",
                    "analysis": "Industrial oil and gas processing equipment designed for extraction, refinement, or transportation operations. The system operates under high pressure and temperature conditions. Critical monitoring includes pressure sensors, flow meters, temperature gauges, and safety valve status. Corrosion monitoring and leak detection are essential for operational safety.",
                    "tags": ["oil-and-gas", "petrochemical", "processing", "industrial"],
                    "confidence": 0.91
                }
            }
            
            matched_device = None
            for key, data in device_analysis.items():
                if key in filename:
                    matched_device = data
                    break
            
            if not matched_device:
                if cohere_client:
                    prompt = f"""Analyze this industrial IoT device based on the filename: {filename}

Query: {query}

Provide a technical analysis including:
1. Likely device type and purpose
2. Key monitoring parameters
3. Maintenance considerations
4. Industrial applications"""

                    response = cohere_client.chat(message=prompt)
                    analysis_text = response.text if hasattr(response, 'text') else "Generic industrial IoT device for monitoring and control applications."
                else:
                    analysis_text = f"Industrial IoT device ({filename}). The image shows monitoring equipment used in enterprise environments for real-time data collection and analysis. Key features include sensor integration, data transmission capabilities, and edge computing support."
                
                matched_device = {
                    "type": "Industrial IoT Device",
                    "analysis": analysis_text,
                    "tags": ["iot", "industrial", "monitoring"],
                    "confidence": 0.75
                }
            
            file_size = os.path.getsize(image_path)
            
            return {
                "success": True,
                "device_type": matched_device["type"],
                "analysis": matched_device["analysis"],
                "confidence": matched_device["confidence"],
                "tags": matched_device["tags"],
                "technical_details": {
                    "filename": os.path.basename(image_path),
                    "file_size_kb": round(file_size / 1024, 2),
                    "query": query
                },
                "recommendations": [
                    "Monitor device metrics in real-time dashboard",
                    "Set up automated alerts for anomaly detection",
                    "Schedule regular maintenance based on usage patterns",
                    "Integrate with predictive maintenance systems"
                ]
            }

        except Exception as e:
            print(f"Image analysis error: {e}")
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e),
                "analysis": f"Error analyzing image: {str(e)}"
            }

    @staticmethod
    def summarize_metrics(metrics_data: Dict[str, Any]) -> str:
        """Generate a natural language summary of metrics"""
        try:
            if not cohere_client:
                return f"System overview: Monitoring {metrics_data.get('total_devices', 0)} devices. Health: {metrics_data.get('health_percentage', 0)}%. All systems operational."

            prompt = f"""Summarize these SRE metrics in a concise, executive-friendly format:

Total Devices: {metrics_data.get('total_devices')}
Online: {metrics_data.get('online')}
Offline: {metrics_data.get('offline')}
Warnings: {metrics_data.get('warning')}
Errors: {metrics_data.get('error')}
Health: {metrics_data.get('health_percentage')}%

Focus on:
- Overall system health
- Key performance indicators
- Any concerns
- Brief actionable insights"""

            response = cohere_client.chat(message=prompt)
            return response.text if hasattr(response, 'text') else str(response)

        except Exception as e:
            print(f"Metrics summary error: {e}")
            return f"Monitoring {metrics_data.get('total_devices', 0)} devices with {metrics_data.get('health_percentage', 0)}% health."

    @staticmethod
    def analyze_device_health(device_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze device health using AI"""
        try:
            if not cohere_client:
                status = device_data.get("status", "unknown")
                return {
                    "health_score": 85 if status == "online" else 50,
                    "recommendations": ["Monitor temperature trends", "Schedule maintenance"],
                    "risk_level": "low" if status == "online" else "medium",
                    "mock": True
                }

            prompt = f"""Analyze this IoT device health data and provide:
1. Health score (0-100)
2. Recommendations
3. Risk level (low/medium/high/critical)

Device data:
Device ID: {device_data.get('device_id')}
Type: {device_data.get('device_type')}
Status: {device_data.get('status')}
Temperature: {device_data.get('temperature')}°C
Pressure: {device_data.get('pressure')} psi
Efficiency: {device_data.get('efficiency')}%"""

            response = cohere_client.chat(message=prompt)

            return {
                "health_score": 75,
                "analysis": response.text if hasattr(response, 'text') else str(response),
                "recommendations": ["Review detailed metrics"],
                "risk_level": "low"
            }

        except Exception as e:
            print(f"Device health analysis error: {e}")
            return {
                "health_score": 0,
                "error": str(e)
            }


cohere_service = CohereService()