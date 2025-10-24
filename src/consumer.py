import asyncio
import logging
from typing import Any, Dict, List, Optional
from src.models import Event
from src.dedup_store import DedupStore

logger = logging.getLogger(__name__)

class IdempotentConsumer:
    """
    Consumer yang memproses event dengan idempotency guarantee
    Event yang sama (topic + event_id) hanya diproses sekali
    """
    
    def __init__(self, dedup_store: DedupStore):
        self.dedup_store = dedup_store
        self.queue: asyncio.Queue = asyncio.Queue()
        self.processed_events: List[Event] = []
        self.stats = {
            "received": 0,
            "unique_processed": 0,
            "duplicate_dropped": 0
        }
    
    async def enqueue(self, event: Event):
        """Masukkan event ke queue untuk diproses"""
        await self.queue.put(event)
        self.stats["received"] += 1
    
    async def process_loop(self):
        """
        Background task yang terus memproses event dari queue
        Ini jalan terus selama aplikasi hidup
        """
        logger.info("Consumer started, waiting for events...")
        
        while True:
            try:
                # Ambil event dari queue 
                event = await self.queue.get()
                
                # Proses event dengan idempotency check
                await self._process_event(event)
                
                self.queue.task_done()
                
            except Exception as e:
                logger.error(f"Error processing event: {e}")
    
    async def _process_event(self, event: Event):
        """
        Proses satu event dengan deduplication
        """
        # Cek apakah event ini duplikat
        if self.dedup_store.is_duplicate(event.topic, event.event_id):
            logger.warning(
                f"🔁 Duplicate detected! topic={event.topic}, "
                f"event_id={event.event_id} - SKIPPED"
            )
            self.stats["duplicate_dropped"] += 1
            return
        
        # Event baru
        success = self.dedup_store.mark_processed(event.topic, event.event_id)
        
        if not success:
            # Race condition: event sudah di-mark oleh thread lain
            logger.warning(f"Race condition detected for event {event.event_id}")
            self.stats["duplicate_dropped"] += 1
            return
        
        # Simpan event ke memory (untuk GET /events endpoint)
        self.processed_events.append(event)
        self.stats["unique_processed"] += 1
        
        logger.info(
            f"✅ Processed: topic={event.topic}, "
            f"event_id={event.event_id}, source={event.source}"
        )
        
        await asyncio.sleep(0)


    
    def get_events(self, topic: Optional[str] = None) -> List[Event]:
        """Get processed events, optionally filtered by topic"""
        if topic:
            return [e for e in self.processed_events if e.topic == topic]
        return self.processed_events