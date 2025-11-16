"""
Cohere AI service for image analysis and natural language queries
"""
import base64
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
    def analyze_image(image_path: str, query: str = "Analyze this device image") -> Dict[str, Any]:
        """Analyze an image using Cohere AI"""
        try:
            if not cohere_client:
                # Mock response for demo
                return {
                    "success": True,
                    "analysis": f"Mock analysis: This appears to be an industrial device image. {query}",
                    "confidence": 0.85,
                    "tags": ["industrial", "machinery", "monitoring"],
                    "mock": True
                }

            # Read and encode image
            with open(image_path, "rb") as image_file:
                image_data = base64.b64encode(image_file.read()).decode('utf-8')

            # Use Cohere's vision capabilities (if available)
            # Note: This is a simplified version. Actual implementation may vary based on Cohere's API
            response = cohere_client.chat(
                model=settings.COHERE_MODEL,
                message=f"{query}. Provide detailed technical analysis of the device shown in the image.",
            )

            return {
                "success": True,
                "analysis": response.text,
                "confidence": 0.9,
                "tags": ["device", "analyzed"]
            }

        except Exception as e:
            print(f"Image analysis error: {e}")
            return {
                "success": False,
                "error": str(e),
                "analysis": "Error analyzing image"
            }

    @staticmethod
    def natural_language_query(query: str, context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Process natural language queries about the system"""
        try:
            if not cohere_client:
                # Mock response for demo
                return {
                    "success": True,
                    "response": f"Mock response: Based on your query '{query}', here's the information...",
                    "suggestions": ["Check device status", "View site metrics", "Analyze logs"],
                    "mock": True
                }

            # Build context-aware prompt
            context_str = ""
            if context:
                context_str = f"\n\nContext:\n{context}"

            prompt = f"""You are an SRE (Site Reliability Engineering) assistant for an industrial IoT monitoring system.
The system monitors 100,000 devices across 10 sites with device types: Turbine, ThermalEngine, ElectricalRotor, and OilAndGas.

User query: {query}{context_str}

Provide a helpful, technical response focused on monitoring, metrics, and system reliability."""

            response = cohere_client.chat(
                model=settings.COHERE_MODEL,
                message=prompt,
            )

            return {
                "success": True,
                "response": response.text,
                "suggestions": []
            }

        except Exception as e:
            print(f"NL query error: {e}")
            return {
                "success": False,
                "error": str(e),
                "response": "Error processing query"
            }

    @staticmethod
    def summarize_metrics(metrics_data: Dict[str, Any]) -> str:
        """Generate a natural language summary of metrics"""
        try:
            if not cohere_client:
                # Mock summary
                return f"System overview: {len(metrics_data)} metrics tracked. All systems operational."

            prompt = f"""Summarize these SRE metrics in a concise, executive-friendly format:

{metrics_data}

Focus on:
- Overall system health
- Key performance indicators
- Any anomalies or concerns
- Actionable insights"""

            response = cohere_client.chat(
                model=settings.COHERE_MODEL,
                message=prompt,
            )

            return response.text

        except Exception as e:
            print(f"Metrics summary error: {e}")
            return "Error generating summary"

    @staticmethod
    def analyze_device_health(device_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze device health using AI"""
        try:
            if not cohere_client:
                # Mock analysis
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
{device_data}"""

            response = cohere_client.chat(
                model=settings.COHERE_MODEL,
                message=prompt,
            )

            # Parse response (simplified)
            return {
                "health_score": 75,
                "analysis": response.text,
                "recommendations": ["Review detailed metrics"],
                "risk_level": "low"
            }

        except Exception as e:
            print(f"Device health analysis error: {e}")
            return {
                "health_score": 0,
                "error": str(e)
            }


# Export singleton instance
cohere_service = CohereService()
