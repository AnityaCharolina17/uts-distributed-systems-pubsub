import pytest
from fastapi.testclient import TestClient
import tempfile
import os
from src.dedup_store import DedupStore
from src.consumer import IdempotentConsumer
from src.api import AggregatorAPI

@pytest.fixture
def test_client():
    """Setup test client dengan temp database"""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as f:
        db_path = f.name
    
    store = DedupStore(db_path)
    consumer = IdempotentConsumer(store)
    api = AggregatorAPI(consumer)
    
    client = TestClient(api.app)
    yield client
    
    os.unlink(db_path)

def test_publish_endpoint(test_client):
    """Test POST /publish endpoint"""
    event = {
        "topic": "user-login",
        "event_id": "evt_test_001",
        "timestamp": "2025-10-24T10:00:00Z",
        "source": "auth-service",
        "payload": {"user_id": 42}
    }
    
    response = test_client.post("/publish", json=event)
    
    assert response.status_code == 202
    assert response.json()["status"] == "accepted"
    assert response.json()["event_id"] == "evt_test_001"

def test_stats_endpoint(test_client):
    """Test GET /stats endpoint"""
    # Send some events
    for i in range(5):
        test_client.post("/publish", json={
            "topic": "test",
            "event_id": f"evt_{i}",
            "timestamp": "2025-10-24T10:00:00Z",
            "source": "test",
            "payload": {}
        })
    
    import time
    time.sleep(0.1)  # Wait for processing
    
    response = test_client.get("/stats")
    assert response.status_code == 200
    
    stats = response.json()
    assert stats["received"] == 5

def test_get_events_with_filter(test_client):
    """Test GET /events dengan filter topic"""
    # Send events dengan topic berbeda
    test_client.post("/publish", json={
        "topic": "login",
        "event_id": "evt_1",
        "timestamp": "2025-10-24T10:00:00Z",
        "source": "test",
        "payload": {}
    })
    
    test_client.post("/publish", json={
        "topic": "logout",
        "event_id": "evt_2",
        "timestamp": "2025-10-24T10:00:00Z",
        "source": "test",
        "payload": {}
    })
    
    import time
    time.sleep(0.1)
    
    # Filter by topic
    response = test_client.get("/events?topic=login")
    assert response.status_code == 200