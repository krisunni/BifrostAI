import json
import uuid

import chromadb
import paho.mqtt.client as mqtt
from langchain.text_splitter import RecursiveJsonSplitter, RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

# ChromaDB settings
chroma_client = chromadb.PersistentClient(path="./chroma_data")
collection = chroma_client.get_or_create_collection("bifrost_data")

# Ollama settings
OLLAMA_URL = "http://localhost:11434"
MODEL = "phi3"
oembed = OllamaEmbeddings(base_url=OLLAMA_URL, model=MODEL, temperature=0)

# Chroma collections for different devices
chromaForDrone1 = Chroma(client=chroma_client, collection_name="pi5", embedding_function=oembed)
chromaDrone1Sentence = Chroma(client=chroma_client, collection_name="pi5_camera_1", embedding_function=oembed)

# Recursive splitters
recursiveJsonSplitter = RecursiveJsonSplitter(max_chunk_size=300)
recursiveCharacterTextSplitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)

# MQTT settings
MQTT_HOST = "192.168.1.123"
MQTT_PORT = 1883
MQTT_USERNAME = "publish"
MQTT_PASSWORD = "publish"
TOPIC = "pi5/camera/1"
CLIENT_ID = "bifrost_mqtt_subscriber"

def vectorize_data(detection):
    """
    Converts detection data into a string and generates a vector using Ollama.
    """
    data_str = f"Label: {detection['label']}, BBox: {detection['bbox']}, Confidence: {detection['confidence']}, UTC: {detection['utc']}"
    return oembed.embed_query(data_str)  # Uses Ollama instead of SentenceTransformer

def on_message(client, userdata, message):
    try:
        mqtt_message = json.loads(message.payload.decode('utf-8'))
        print(f"Processing frame: {mqtt_message.get('frame', 'N/A')}")

        for detection in mqtt_message.get("detections", []):
            vector = vectorize_data(detection)
            metadata = {
                "label": detection["label"],
                "bbox": json.dumps(detection["bbox"]),
                "confidence": detection["confidence"],
                "utc": detection["utc"]
            }
            unique_id = str(uuid.uuid4())
            collection.add(embeddings=[vector], metadatas=[metadata], documents=[json.dumps(detection)], ids=[unique_id])

    except Exception as e:
        print(f"Error processing message: {e}")

def on_connect(client, userdata, flags, rc):
    if rc == 0:
        print("Connected to MQTT Broker!")
        client.subscribe(TOPIC)
    else:
        print(f"Failed to connect, return code {rc}")

def connect_mqtt():
    client = mqtt.Client(CLIENT_ID)
    client.username_pw_set(MQTT_USERNAME, MQTT_PASSWORD)
    client.on_connect = on_connect
    client.connect(MQTT_HOST, MQTT_PORT)
    return client

def run():
    client = connect_mqtt()
    client.on_message = on_message
    client.loop_forever()

if __name__ == '__main__':
    run()
