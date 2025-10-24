import pytest
import os
import tempfile
from src.dedup_store import DedupStore
from src.models import Event
from src.consumer import IdempotentConsumer

@pytest.fixture
def temp_dedup_store():
    """Buat temporary database untuk testing"""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as f:
        db_path = f.name

    store = DedupStore(db_path)
    yield store

    import time
    time.sleep(0.1)
    try:
        os.unlink(db_path)
    except PermissionError:
        pass 


def test_dedup_detects_duplicate(temp_dedup_store):
    """Test: event yang sama dikirim 2x, hanya diproses 1x"""
    store = temp_dedup_store
    
    # First event: should be processed
    assert not store.is_duplicate("login", "evt_123")
    assert store.mark_processed("login", "evt_123")
    
    # Same event again: should be detected as duplicate
    assert store.is_duplicate("login", "evt_123")
    assert not store.mark_processed("login", "evt_123")

@pytest.mark.asyncio
async def test_consumer_idempotency(temp_dedup_store):
    """Test: consumer skip event duplikat"""
    consumer = IdempotentConsumer(temp_dedup_store)
    
    event = Event(
        topic="test",
        event_id="evt_xyz",
        timestamp="2025-10-24T10:00:00Z",
        source="test",
        payload={"msg": "hello"}
    )
    
    # Send event 3 times
    await consumer._process_event(event)
    await consumer._process_event(event)
    await consumer._process_event(event)
    
    # Should only process once
    assert consumer.stats["unique_processed"] == 1
    assert consumer.stats["duplicate_dropped"] == 2

def test_different_topics_same_event_id(temp_dedup_store):
    """Test: event_id sama tapi topic beda = bukan duplikat"""
    store = temp_dedup_store
    
    store.mark_processed("login", "evt_123")
    store.mark_processed("logout", "evt_123")
    
    assert store.get_total_processed() == 2