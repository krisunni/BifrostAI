# BifrostAI: Real-time Video Analysis with ChromaDB & Ollama

This project ingests video data from a Raspberry Pi 5 with AI HAT+, stores it in ChromaDB, and queries it using Ollama.

## Components

- **Ingest (`ingest.py`)**: Subscribes to an MQTT topic, ingests data (label, bbox, confidence, utc) into ChromaDB.
- **Query (`query.py`)**: Queries ChromaDB and sends data to Ollama for natural language responses.

## Requirements

Install dependencies:

```bash
pip install -r requirements.txt
```

### Dependencies:

paho-mqtt: MQTT client
chromadb: ChromaDB interaction
requests: HTTP requests to Ollama

# Setup on Raspberry Pi 5
To get started with the Raspberry Pi AI HAT+, follow the installation instructions from the official documentation here: [AI HAT+ Setup](https://www.raspberrypi.com/documentation/accessories/ai-hat-plus.html#ai-hat-plus-installation)

1. Clone the Repository
Start by cloning my fork of the repository with MQTT publishing examples:

```bash
git clone https://github.com/krisunni/hailo-rpi5-examples
cd hailo-rpi5-examples

```

This repository contains MQTT publishing scripts to stream video data from your Raspberry Pi.

2. Start the MQTT Server
To start the MQTT server using Docker, run the following on your Raspberry Pi:

```bash
docker run -d --name emqx \
  -p 1883:1883 \
  -p 8083-8084:8083-8084 \
  emqx/emqx-enterprise:5.8.0
```
This will start the MQTT server on ports 1883 and 8083-8084 for WebSocket connections.

# Runbook: Setting Up and Running the Project on Mac
- Step 1: Create and Activate a Virtual Environment
Create a virtual environment:
In your project directory, run:
Activate the virtual environment:
```bash
python -m venv venv
```

Activate the virtual env
```bash
source venv/bin/activate
```

Step 2: Install Project Dependencies
With the virtual environment activated, install the required dependencies by running:

```bash
pip install -r requirements.txt
```

Step 3: Run the Ingest Script
To start ingesting data from the Raspberry Pi, run:

```bash
python ingest.py
````
This script will listen to MQTT and store the received data in ChromaDB.

Step 4: Run the Query Script
To query the stored data using natural language, run:

```bash
python query.py
```
You will be prompted to enter a question. For example:
```bash
Ask a question: What was detected in the most recent image?
```