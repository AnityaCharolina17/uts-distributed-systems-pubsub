import pytest
import os
import tempfile
from src.dedup_store import DedupStore

def test_dedup_survives_restart():
    """Test: database tetap ada setelah restart"""
    with tempfile.NamedTemporaryFile(delete=False, suffix=".db") as f:
        db_path = f.name
    
    # Session 1: mark some events
    store1 = DedupStore(db_path)
    store1.mark_processed("login", "evt_100")
    store1.mark_processed("login", "evt_101")
    del store1  # Simulasi shutdown
    
    # Session 2: create new instance (simulasi restart)
    store2 = DedupStore(db_path)
    
    # Data harus masih ada
    assert store2.is_duplicate("login", "evt_100")
    assert store2.is_duplicate("login", "evt_101")
    assert store2.get_total_processed() == 2
    
    # Cleanup
    os.unlink(db_path)