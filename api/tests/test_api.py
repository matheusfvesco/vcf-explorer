from ..api.serve import app
from fastapi.testclient import TestClient

client = TestClient(app)

def test_variants():
    response = client.get('/variants')
    assert response.status_code == 200
    # Check whatever you want to check
    assert b'Hello, World!' in response.data