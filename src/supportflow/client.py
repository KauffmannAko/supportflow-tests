from typing import Any
import requests
from supportflow.config import Settings


class SupportFlowClient:
    def __init__(self, settings:Settings) -> None:
        self.settings = settings

    def get(self, path: str, **kwargs: Any) -> requests.Response:
        return requests.get(
            f"{self.settings.base_url}{path}",
            timeout=self.settings.timeout_seconds,
            **kwargs,
        )
    
    def get_health(self) -> requests.Response:
        return self.get("/health")
