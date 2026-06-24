import os
import requests

def test_supportflow_health_endpoint_is_available():
    baseUrl = os.environ['SUPPORTFLOW_BASE_URL'].rstrip("/")
    response = requests.get(
                f"{baseUrl}",
    )
    assert response.status_code == 200