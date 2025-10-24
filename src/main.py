import asyncio
import logging
import uvicorn
from src.dedup_store import DedupStore
from src.consumer import IdempotentConsumer
from src.api import AggregatorAPI

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

async def main():
    """Main function untuk start semua komponen"""
    logger.info("🚀 Starting Pub-Sub Log Aggregator...")
    
    # 1. Init dedup store
    dedup_store = DedupStore()
    logger.info("✅ Dedup store initialized")
    
    # 2. Init consumer
    consumer = IdempotentConsumer(dedup_store)
    logger.info("✅ Idempotent consumer initialized")
    
    # 3. Init API
    api = AggregatorAPI(consumer)
    logger.info("✅ API initialized")
    
    # 4. Start consumer background task
    asyncio.create_task(consumer.process_loop())
    logger.info("✅ Consumer loop started")
    
    # 5. Start FastAPI server
    config = uvicorn.Config(
        api.app,
        host="0.0.0.0",
        port=8080,
        log_level="info"
    )
    server = uvicorn.Server(config)
    
    logger.info("🌐 Server running on http://0.0.0.0:8080")
    logger.info("📚 API docs available at http://0.0.0.0:8080/docs")
    
    await server.serve()

if __name__ == "__main__":
    asyncio.run(main())