from abc import ABC, abstractmethod
from typing import Dict, Any

class ReportGenerationClient(ABC):
    @abstractmethod
    def generate_report(self, prompt: str) -> str:
        pass

class ReportGenerationClientFactory(ABC):
    @abstractmethod
    def create_client(self, config: Dict[str, Any]) -> ReportGenerationClient:
        pass