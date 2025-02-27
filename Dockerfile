# Use Python 3.12 slim image
FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Install system dependencies required for confluent-kafka
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    build-essential \
    librdkafka-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy all necessary files for building the package
COPY pyproject.toml setup.cfg MANIFEST.in README.md LICENSE ./
COPY src ./src
COPY scripts ./scripts

# Install the package
RUN pip install --no-cache-dir -e .

# Expose the port
EXPOSE 52988

# Set environment variables
ENV PYTHONUNBUFFERED=1
ENV KAFKA_BROKER=kafka:9092

# Run the application
CMD ["event-tracker"]