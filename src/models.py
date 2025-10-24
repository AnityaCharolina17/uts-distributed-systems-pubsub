from pydantic import BaseModel, Field
from typing import Dict, Any, Optional
from datetime import datetime

class Event(BaseModel):
    """Model untuk event yang dikirim oleh publisher"""
    topic: str = Field(..., description="Topic/kategori event")
    event_id: str = Field(..., description="ID unik event untuk dedup")
    timestamp: str = Field(..., description="Waktu event (ISO8601)")
    source: str = Field(..., description="Sumber event (nama publisher)")
    payload: Dict[str, Any] = Field(..., description="Data event")
    
    class Config:
        json_schema_extra = {
            "example": {
                "topic": "user-login",
                "event_id": "evt_abc123xyz",
                "timestamp": "2025-10-24T10:30:00Z",
                "source": "auth-service",
                "payload": {"user_id": 42, "ip": "192.168.1.1"}
            }
        }

class Stats(BaseModel):
    """Model untuk statistik sistem"""
    received: int = 0
    unique_processed: int = 0
    duplicate_dropped: int = 0
    topics: Dict[str, int] = {}
    uptime_seconds: float = 0.0