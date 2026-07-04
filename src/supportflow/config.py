import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    base_url: str
    timeout_seconds: float = 10.0
       
def load_settings() -> Settings:
     base_url = os.getenv("SUPPORTFLOW_BASE_URL")

     if not base_url:
          raise RuntimeError(
               "Missing required environment variable: SUPPORTFLOW_BASE_URL"
          )

     return Settings(base_url=base_url.rstrip("/"))
