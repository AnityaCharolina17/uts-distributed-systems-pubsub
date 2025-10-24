import requests
import time
import random
import os
from datetime import datetime

AGGREGATOR_URL = os.getenv("AGGREGATOR_URL", "http://localhost:8080")

def generate_event(event_id, topic="test-topic"):
    """Generate random event"""
    return {
        "topic": topic,
        "event_id": event_id,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "source": "publisher-service",
        "payload": {
            "message": f"Event {event_id}",
            "random_value": random.randint(1, 1000)
        }
    }

def main():
    print("🚀 Publisher started")
    print(f"📡 Sending events to {AGGREGATOR_URL}")
    
    time.sleep(5)  # Wait for aggregator to be ready
    
    event_counter = 0
    
    while True:
        try:
            # Generate unique event
            event = generate_event(f"evt_{event_counter}")
            
            # Send to aggregator
            response = requests.post(
                f"{AGGREGATOR_URL}/publish",
                json=event,
                timeout=5
            )
            
            if response.status_code == 202:
                print(f"✅ Sent: {event['event_id']}")
            
            # Simulasi duplikasi (20% chance)
            if random.random() < 0.2:
                print(f"🔁 Sending duplicate: {event['event_id']}")
                requests.post(f"{AGGREGATOR_URL}/publish", json=event)
            
            event_counter += 1
            time.sleep(random.uniform(0.1, 0.5))
            
        except Exception as e:
            print(f"❌ Error: {e}")
            time.sleep(1)

if __name__ == "__main__":
    main()