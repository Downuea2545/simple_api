from app import app
import pytest

@pytest.fixture
def client():
    with app.test_client() as client:
        yield client

def test_plus_method(client):
    # Test case 1: 5 + 6 = 11
    response = client.get('/plus/5/6')
    assert response.status_code == 200
    assert response.json['result'] == 11

    # Test case 2: -1 + 1 = 0
    response = client.get('/plus/-1/1')
    assert response.status_code == 200
    assert response.json['result'] == 0

    # Test case 3: 100 + 200 = 300
    response = client.get('/plus/100/200')
    assert response.status_code == 200
    assert response.json['result'] == 300
