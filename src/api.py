from fastapi import FastAPI, HTTPException
from typing import List, Optional
import time
from src.models import Event, Stats
from src.consumer import IdempotentConsumer

class AggregatorAPI:
    """FastAPI application untuk log aggregator"""
    
    def __init__(self, consumer: IdempotentConsumer):
        self.app = FastAPI(
            title="Pub-Sub Log Aggregator",
            description="Idempotent consumer dengan deduplication",
            version="1.0.0"
        )
        self.consumer = consumer
        self.start_time = time.time()
        
        # Register routes
        self._setup_routes()
    
    def _setup_routes(self):
        """Setup semua API endpoints"""
        
        @self.app.post("/publish", status_code=202)
        async def publish_event(event: Event):
            """
            Endpoint untuk publisher mengirim event
            202 Accepted: event diterima dan akan diproses
            """
            await self.consumer.enqueue(event)
            return {
                "status": "accepted",
                "event_id": event.event_id,
                "topic": event.topic
            }
        
        @self.app.post("/publish/batch", status_code=202)
        async def publish_batch(events: List[Event]):
            """
            Endpoint untuk mengirim banyak event sekaligus
            Berguna untuk testing
            """
            for event in events:
                await self.consumer.enqueue(event)
            
            return {
                "status": "accepted",
                "count": len(events)
            }
        
        @self.app.get("/events")
        async def get_events(topic: Optional[str] = None):
            """
            Get daftar event yang sudah diproses
            Query param: ?topic=nama_topic (opsional)
            """
            events = self.consumer.get_events(topic)
            return {
                "count": len(events),
                "topic_filter": topic,
                "events": events
            }
        
        @self.app.get("/stats")
        async def get_stats():
            """
            Get statistik sistem:
            - received: total event diterima
            - unique_processed: event unik yang diproses
            - duplicate_dropped: duplikat yang di-skip
            - topics: breakdown per topic
            - uptime: waktu sistem jalan
            """
            uptime = time.time() - self.start_time
            topics = self.consumer.dedup_store.get_topics()
            
            return Stats(
                received=self.consumer.stats["received"],
                unique_processed=self.consumer.stats["unique_processed"],
                duplicate_dropped=self.consumer.stats["duplicate_dropped"],
                topics=topics,
                uptime_seconds=round(uptime, 2)
            )
        
        @self.app.get("/health")
        async def health_check():
            """Health check endpoint"""
            return {"status": "healthy", "service": "pub-sub-aggregator"}