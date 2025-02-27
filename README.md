# OpenHands Event Tracker

A FastAPI application that accepts frontend event tracking and sends the received events to Kafka. Built with FastAPI and confluent-kafka.

## Features

- FastAPI-based REST API for event tracking
- Kafka integration using confluent-kafka
- Production-ready threading and error handling
- Docker support with Kafka and Zookeeper included
- Proper shutdown handling and resource cleanup

## Installation

### Using pip

```bash
pip install openhands-event-tracker
```

### From source

```bash
git clone https://github.com/venkunikku/open-hands-fastapi-kafka.git
cd open-hands-fastapi-kafka
pip install -e .
```

## Usage

### Running with Docker Compose

The easiest way to get started is using Docker Compose:

```bash
docker-compose up -d
```

This will start:
- Zookeeper
- Kafka
- Event Tracker API

### Running locally

1. Make sure you have Kafka running at localhost:9092
2. Run the application:

```bash
event-tracker
```

Or run the module directly:

```bash
python -m openhands_event_tracker.app
```

### Sending Events

Send events using HTTP POST requests:

```bash
curl -X POST http://localhost:52988/track-event \
-H "Content-Type: application/json" \
-d '{
  "event_type": "user_action",
  "event_data": {
    "action": "button_click",
    "page": "/home",
    "user_id": "123"
  },
  "source": "web_app",
  "version": "1.0"
}'
```

## Building the Package

To build the wheel file:

```bash
pip install build
python -m build
```

This will create:
- A wheel file in `dist/*.whl`
- A source distribution in `dist/*.tar.gz`

## Configuration

The application can be configured using environment variables:

- `KAFKA_BROKER`: Kafka broker address (default: localhost:9092)
- `PORT`: Application port (default: 52988)

## License

MIT License