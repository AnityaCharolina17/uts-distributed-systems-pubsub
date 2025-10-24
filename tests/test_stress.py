import pytest
import time
import tempfile
import os
from src.dedup_store import DedupStore
from src.consumer import IdempotentConsumer
from src.models import Event

@pytest.mark.asyncio
async def test_high_volume_with_duplicates():
    """Test: 5000 event dengan 20% duplikasi"""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as f:
        db_path = f.name
    
    store = DedupStore(db_path)
    consumer = IdempotentConsumer(store)
    
    total_events = 5000
    unique_events = 4000
    
    start_time = time.time()
    
    for i in range(total_events):
        if i < unique_events:
            event_id = f"evt_{i}"
        else:
            event_id = f"evt_{i % unique_events}"
        
        event = Event(
            topic="stress-test",
            event_id=event_id,
            timestamp="2025-10-24T10:00:00Z",
            source="stress",
            payload={"index": i}
        )
        
        await consumer._process_event(event)
    
    elapsed = time.time() - start_time
    
    assert consumer.stats["unique_processed"] == unique_events
    assert consumer.stats["duplicate_dropped"] == (total_events - unique_events)
    
    assert elapsed < 40.0

    
    print(f"\n Processed {total_events} events in {elapsed:.2f}s")
    print(f"   Throughput: {total_events/elapsed:.0f} events/sec")
    
    os.unlink(db_path)