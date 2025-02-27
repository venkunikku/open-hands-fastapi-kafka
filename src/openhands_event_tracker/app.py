from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
import uuid
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from kafka_client import KafkaProducer, KafkaConsumer

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# FastAPI app configuration
app = FastAPI(title="Event Tracking API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Kafka configuration
KAFKA_BROKER = "localhost:9092"
KAFKA_TOPIC = "events"

producer_config = {
    'bootstrap.servers': KAFKA_BROKER,
    'client.id': 'fastapi-producer',
    'acks': 'all',
    'retries': 5,
    'retry.backoff.ms': 1000,
    'compression.type': 'gzip',
    'linger.ms': 100,
    'batch.size': 16384,
}

consumer_config = {
    'bootstrap.servers': KAFKA_BROKER,
    'group.id': 'event-tracking-group',
    'auto.offset.reset': 'earliest',
    'enable.auto.commit': True,
    'auto.commit.interval.ms': 5000,
    'max.poll.interval.ms': 300000,
    'session.timeout.ms': 30000,
}

# Initialize Kafka clients
kafka_producer = KafkaProducer(producer_config)
kafka_consumer = KafkaConsumer(consumer_config, [KAFKA_TOPIC])

class Event(BaseModel):
    event_type: str = Field(..., description="Type of the event")
    event_data: Dict[str, Any] = Field(..., description="Event payload")
    timestamp: Optional[str] = Field(default_factory=lambda: datetime.utcnow().isoformat())
    source: Optional[str] = None
    version: str = Field(default="1.0", description="Event schema version")

def handle_event(event_data: Dict[str, Any]):
    logger.info(f"Processing event: {event_data}")
    # Add your event processing logic here
    # For example, store in database, trigger notifications, etc.

@app.post("/track-event", status_code=202)
async def track_event(event: Event):
    try:
        event_id = str(uuid.uuid4())
        
        message = {
            "id": event_id,
            "type": event.event_type,
            "data": event.event_data,
            "timestamp": event.timestamp,
            "source": event.source or "api",
            "version": event.version
        }
        
        kafka_producer.send_message(
            topic=KAFKA_TOPIC,
            key=event_id,
            value=message
        )
        
        return {
            "status": "accepted",
            "event_id": event_id,
            "timestamp": event.timestamp
        }
    
    except Exception as e:
        logger.error(f"Error processing event: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="Failed to process event"
        )

@app.on_event("startup")
async def startup_event():
    try:
        # Start Kafka producer
        kafka_producer.start()
        
        # Add event handler and start consumer
        kafka_consumer.add_message_handler(handle_event)
        kafka_consumer.start()
        
        logger.info("Application started successfully")
    except Exception as e:
        logger.error(f"Failed to start application: {str(e)}")
        raise

@app.on_event("shutdown")
async def shutdown_event():
    try:
        # Stop Kafka clients
        kafka_producer.stop()
        kafka_consumer.stop()
        
        logger.info("Application shutdown complete")
    except Exception as e:
        logger.error(f"Error during shutdown: {str(e)}")

def main():
    import uvicorn
    uvicorn.run(
        "openhands_event_tracker.app:app",
        host="0.0.0.0",
        port=52988,
        reload=False,
        workers=1,
        log_level="info"
    )

if __name__ == "__main__":
    main()