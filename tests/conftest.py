import pytest

from supportflow.client import SupportFlowClient
from supportflow.config import load_settings

@pytest.fixture
def api_client()-> SupportFlowClient:
    settings = load_settings()
    
    return SupportFlowClient(settings)