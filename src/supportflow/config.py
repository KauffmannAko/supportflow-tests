import os
from dataclasses import dataclass


@dataclass(frozen=True)
class Settings:
    base_url: str
    timeout_seconds: float = 10.0
       
def load_settings() -> Settings:
     base_url = os.environ["SUPPORTFLOW_BASE_URL"].rstrip("/")

     return Settings(base_url=base_url)
