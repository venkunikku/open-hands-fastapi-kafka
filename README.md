# OpenHands Event Tracker

A production-grade FastAPI application that accepts frontend event tracking and sends the received events to Kafka. Built with FastAPI and confluent-kafka.

## Features

- FastAPI-based REST API for event tracking
- Production-ready Kafka integration using confluent-kafka
- Thread-safe message handling with proper queuing
- Graceful shutdown and error handling
- Docker support with Kafka and Zookeeper included
- Comprehensive logging and monitoring
- Build system for creating distributable packages

## Prerequisites

- Python 3.9 or higher
- librdkafka development libraries (for confluent-kafka)
  ```bash
  # Ubuntu/Debian
  sudo apt-get install librdkafka-dev

  # CentOS/RHEL
  sudo yum install librdkafka-devel

  # macOS
  brew install librdkafka
  ```

## Installation

### Quick Start with Docker (Recommended)

The fastest way to get started is using Docker Compose:

```bash
# Clone the repository
git clone https://github.com/venkunikku/open-hands-fastapi-kafka.git
cd open-hands-fastapi-kafka

# Build and start all services
docker-compose up --build -d
```

### Building and Installing Locally

1. Clone the repository:
   ```bash
   git clone https://github.com/venkunikku/open-hands-fastapi-kafka.git
   cd open-hands-fastapi-kafka
   ```

2. Run the build script (creates virtual environment and builds the package):
   ```bash
   # Make the script executable
   chmod +x scripts/build.sh

   # Run the build script
   ./scripts/build.sh
   ```

   The build script will:
   - Create a virtual environment
   - Install build dependencies
   - Build the wheel package
   - Run tests (if pytest is available)
   - Provide installation instructions

3. Install the package:
   ```bash
   # Activate the virtual environment created by build.sh
   source venv/bin/activate  # On Windows: venv\Scripts\activate

   # For development (editable install)
   pip install -e .

   # OR for regular installation
   pip install dist/openhands_event_tracker-*.whl
   ```

### Manual Build Process

If you prefer to build manually or the build script doesn't work for your environment:

1. Create and activate a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. Install build dependencies:
   ```bash
   pip install --upgrade pip
   pip install build wheel setuptools_scm
   ```

3. Build the package:
   ```bash
   python -m build
   ```

4. Install the package:
   ```bash
   pip install dist/openhands_event_tracker-*.whl
   ```

## Usage

## Running the Application

### Option 1: Using Docker Compose (Recommended)

The easiest way to get started is using Docker Compose, which sets up all required services:

1. Build and start the services:
   ```bash
   # Build and start all services in detached mode
   docker-compose up --build -d

   # Or to see the logs directly
   docker-compose up --build
   ```

2. Monitor the services:
   ```bash
   # View logs from all services
   docker-compose logs -f

   # View logs from specific service
   docker-compose logs -f event-tracker
   docker-compose logs -f kafka
   ```

3. Stop and clean up:
   ```bash
   # Stop services
   docker-compose down

   # Stop and remove volumes (will delete Kafka data)
   docker-compose down -v
   ```

This will start:
- Zookeeper (for Kafka coordination)
- Kafka broker (message broker)
- Event Tracker API (our application)

### Option 2: Running Locally (Development Mode)

1. Make sure you have built and installed the package as described in the Installation section.

2. Start Kafka and Zookeeper using Docker:
   ```bash
   # Start only Kafka and Zookeeper
   docker-compose up -d zookeeper kafka

   # Wait for Kafka to be ready
   docker-compose logs -f kafka
   ```

3. Run the application (make sure your virtual environment is activated):
   ```bash
   # If you installed the package
   event-tracker

   # OR for development
   python -m openhands_event_tracker.app
   ```

4. To stop Kafka and Zookeeper:
   ```bash
   docker-compose down
   ```

### Verifying the Installation

Once the application is running (either method), you can verify it works by sending a test event:

```bash
# Check if the API is responding
curl http://localhost:52988/docs

# Send a test event
curl -X POST http://localhost:52988/track-event \
  -H "Content-Type: application/json" \
  -d '{
    "event_type": "test_event",
    "event_data": {
      "test": true,
      "timestamp": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'"
    }
  }'
```

## API Usage

### Event Tracking Endpoint

Send events using HTTP POST requests to `/track-event`:

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

### Event Schema

The API accepts events with the following structure:

```json
{
  "event_type": "string",       // Required: Type of the event
  "event_data": {              // Required: Event payload
    "any_field": "any_value"
  },
  "source": "string",          // Optional: Source of the event
  "version": "string",         // Optional: Schema version (default: "1.0")
  "timestamp": "string"        // Optional: ISO format (auto-generated if not provided)
}
```

## Configuration

### Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `KAFKA_BROKER` | Kafka broker address | `localhost:9092` |
| `PORT` | Application port | `52988` |
| `LOG_LEVEL` | Logging level (DEBUG, INFO, WARNING, ERROR) | `INFO` |

### Kafka Configuration

The application uses the following Kafka configurations, which can be modified in `app.py`:

#### Producer
- `acks`: "all" (ensures maximum durability)
- `retries`: 5 (with backoff)
- `compression.type`: "gzip"
- `batch.size`: 16384 bytes
- `linger.ms`: 100 (batching delay)

#### Consumer
- `auto.offset.reset`: "earliest"
- `enable.auto.commit`: true
- `auto.commit.interval.ms`: 5000
- `max.poll.interval.ms`: 300000
- `session.timeout.ms`: 30000

## Development

### Project Structure

```
openhands-event-tracker/
├── src/
│   └── openhands_event_tracker/
│       ├── __init__.py          # Package initialization
│       ├── app.py              # FastAPI application
│       └── kafka_client.py     # Kafka producer/consumer
├── scripts/
│   └── build.sh               # Build helper script
├── pyproject.toml            # Build system config
├── setup.cfg                 # Package metadata
├── MANIFEST.in              # Package file inclusion
├── README.md               # This file
├── Dockerfile             # Container definition
└── docker-compose.yml    # Service orchestration
```

### Running Tests

```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest
```

## License

MIT License