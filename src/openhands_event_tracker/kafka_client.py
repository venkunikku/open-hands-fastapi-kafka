from confluent_kafka import Producer, Consumer, KafkaError
import threading
import json
import logging
import signal
import queue
from typing import Dict, Any, Optional
from datetime import datetime

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class KafkaProducer:
    def __init__(self, config: Dict[str, Any]):
        self.producer = Producer(config)
        self.message_queue = queue.Queue()
        self.running = False
        self.producer_thread = None
        self._setup_signal_handling()

    def _setup_signal_handling(self):
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, signum, frame):
        logger.info("Signal received, initiating shutdown...")
        self.stop()

    def start(self):
        if self.running:
            return
        
        self.running = True
        self.producer_thread = threading.Thread(target=self._produce_messages)
        self.producer_thread.daemon = True
        self.producer_thread.start()
        logger.info("Kafka producer started")

    def stop(self):
        logger.info("Stopping Kafka producer...")
        self.running = False
        if self.producer_thread:
            self.message_queue.put(None)  # Sentinel value to stop the thread
            self.producer_thread.join()
        self.producer.flush()
        logger.info("Kafka producer stopped")

    def _delivery_report(self, err, msg):
        if err is not None:
            logger.error(f'Message delivery failed: {err}')
        else:
            logger.debug(f'Message delivered to {msg.topic()} [{msg.partition()}]')

    def _produce_messages(self):
        while self.running:
            try:
                message = self.message_queue.get(timeout=1.0)
                if message is None:  # Sentinel value
                    break
                
                topic, key, value = message
                self.producer.produce(
                    topic=topic,
                    key=key,
                    value=value,
                    callback=self._delivery_report
                )
                self.producer.poll(0)  # Trigger delivery reports
                
            except queue.Empty:
                self.producer.poll(0)
            except Exception as e:
                logger.error(f"Error in producer thread: {str(e)}")

    def send_message(self, topic: str, key: str, value: Dict[str, Any]):
        try:
            message = (topic, key, json.dumps(value))
            self.message_queue.put(message)
        except Exception as e:
            logger.error(f"Error queueing message: {str(e)}")
            raise

class KafkaConsumer:
    def __init__(self, config: Dict[str, Any], topics: list[str]):
        self.config = config
        self.topics = topics
        self.consumer = None
        self.running = False
        self.consumer_thread = None
        self.message_handlers = []
        self._setup_signal_handling()

    def _setup_signal_handling(self):
        signal.signal(signal.SIGTERM, self._signal_handler)
        signal.signal(signal.SIGINT, self._signal_handler)

    def _signal_handler(self, signum, frame):
        logger.info("Signal received, initiating shutdown...")
        self.stop()

    def add_message_handler(self, handler):
        self.message_handlers.append(handler)

    def start(self):
        if self.running:
            return

        self.running = True
        self.consumer = Consumer(self.config)
        self.consumer.subscribe(self.topics, on_assign=self._on_assign)
        
        self.consumer_thread = threading.Thread(target=self._consume_messages)
        self.consumer_thread.daemon = True
        self.consumer_thread.start()
        logger.info(f"Kafka consumer started for topics: {self.topics}")

    def stop(self):
        logger.info("Stopping Kafka consumer...")
        self.running = False
        if self.consumer_thread:
            self.consumer_thread.join()
        if self.consumer:
            self.consumer.close()
        logger.info("Kafka consumer stopped")

    def _on_assign(self, consumer, partitions):
        logger.info(f"Assigned partitions: {partitions}")

    def _process_message(self, msg):
        try:
            value = json.loads(msg.value().decode('utf-8'))
            for handler in self.message_handlers:
                try:
                    handler(value)
                except Exception as e:
                    logger.error(f"Handler error: {str(e)}")
        except json.JSONDecodeError as e:
            logger.error(f"Failed to decode message: {str(e)}")
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")

    def _consume_messages(self):
        while self.running:
            try:
                msg = self.consumer.poll(1.0)
                if msg is None:
                    continue
                if msg.error():
                    if msg.error().code() == KafkaError._PARTITION_EOF:
                        continue
                    logger.error(f"Consumer error: {msg.error()}")
                    continue

                self._process_message(msg)
                
            except Exception as e:
                logger.error(f"Error in consumer thread: {str(e)}")
                
        if self.consumer:
            try:
                self.consumer.close()
            except Exception as e:
                logger.error(f"Error closing consumer: {str(e)}")