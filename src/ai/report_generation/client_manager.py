from typing import Dict, Any
from .base import ReportGenerationClient
from .factories.groq_factory import GroqClientFactory

def get_report_generation_client(config: Dict[str, Any]) -> ReportGenerationClient:
    factories = {
        'groq': GroqClientFactory(),
        # Add other factories here
    }
    provider = config['provider']
    if provider not in factories:
        raise ValueError(f"Unsupported AI provider: {provider}")
    return factories[provider].create_client(config)