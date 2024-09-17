from typing import Dict, Any
from ..base import ReportGenerationClientFactory
from ..clients.groq_client import GroqClient

class GroqClientFactory(ReportGenerationClientFactory):
    def create_client(self, config: Dict[str, Any]) -> GroqClient:
        return GroqClient(config['api_key'])