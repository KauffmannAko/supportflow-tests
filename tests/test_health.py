from supportflow.client import SupportFlowClient

def test_supportflow_health_endpoint_is_available(
        api_client:SupportFlowClient
) -> None:
    response = api_client.get_health()
    
    response_body = response.json()

    assert response.status_code == 200
    assert response_body["status"] == "ok"