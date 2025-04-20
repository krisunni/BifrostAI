# BifrostAI: Real-time Video Analysis with ChromaDB, Ollama & Vue UI

BifrostAI ingests real-time video data from a Raspberry Pi 5 with AI HAT+, stores it in ChromaDB, and enables natural language querying through Ollama?all accessible via a modern Vue-based user interface.


https://github.com/user-attachments/assets/152b8b8e-02b5-4fd8-b3be-56f3879a822f
## Components

- **Backend (`backend.py`)**: A unified service that handles MQTT ingestion and querying from ChromaDB.
- **Frontend (Vue UI)**: A user interface for controlling ingestion and querying using natural language.
- **MQTT Source**: The Raspberry Pi 5 with AI HAT+ publishes detection metadata (label, bounding box, confidence, timestamp) to an MQTT topic.

## Requirements

Install Python dependencies:

```bash
pip install -r requirements.txt
```

### Dependencies:

Python Dependencies
* paho-mqtt~=1.6.1: MQTT client for receiving messages
* chromadb~=0.6.2: Local vector database for storage and similarity search
* requests~=2.28.2: HTTP requests to interact with Ollama
* sentence-transformers: Embedding model for encoding data
* langchain~=0.3.21: Language model orchestration framework
* langchain-community~=0.3.20: Community-contributed LangChain tools
* langchain-core: Core interfaces and utilities for LangChain
* langchainhub: Model and chain registry for LangChain
* Flask~=2.3.3: Web server for backend API

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

```bash
python backend.py
````
This script subscribes to the MQTT topic and stores data in ChromaDB. It also exposes REST endpoints for querying.

Step 4: Running the Vue UI
Navigate to the frontend directory:

```bash
cd frontend
npm install
npm run dev
```
The UI will be available at http://localhost:5173.

```bash
Ask a question: Last time you saw a person
```
I have included sample chromadb data to test without Rpi.


##  Features
- Start or stop the MQTT ingestion from the UI
- Monitor ingestion status (Running / Stopped)
- Ask natural language questions such as:

- What was detected in the most recent image?
- Sample Data Support: Test the application without a Raspberry Pi using preloaded ChromaDB sample data

# Example Workflow
1. Power on your Raspberry Pi with AI HAT+ and start the MQTT publisher script
2. Launch the backend service using python backend.py
3. Start the frontend Vue UI using npm run dev
4. Use the browser UI to monitor ingestion and query detected data
