import json
import threading
import uuid
from collections import defaultdict

import chromadb
import paho.mqtt.client as mqtt
import requests
from flask import Flask, jsonify, request
from flask_cors import CORS
from langchain.text_splitter import RecursiveJsonSplitter, RecursiveCharacterTextSplitter
from langchain_community.embeddings import OllamaEmbeddings
from langchain_community.vectorstores import Chroma

app = Flask(__name__)
N_RESULTS = 100
CORS(app)  # enable frontend access
mqtt_client = None
mqtt_thread = None
mqtt_running = False

# ChromaDB settings
chroma_client = chromadb.PersistentClient(path="./chroma_data")
collection = chroma_client.get_or_create_collection("bifrost_data")
# Ollama configuration
OLLAMA_MODEL = "phi3"  # Replace with your model
OLLAMA_HOST = "http://localhost:11434"
oembed = OllamaEmbeddings(base_url=OLLAMA_HOST, model=OLLAMA_MODEL, temperature=0)

# Chroma collections for different devices
chromaForDrone1 = Chroma(client=chroma_client, collection_name="pi5", embedding_function=oembed)
chromaDrone1Sentence = Chroma(client=chroma_client, collection_name="pi5_camera_1", embedding_function=oembed)

# Recursive splitters
recursiveJsonSplitter = RecursiveJsonSplitter(max_chunk_size=300)
recursiveCharacterTextSplitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=50)

# MQTT settings
MQTT_HOST = "192.168.1.124"
MQTT_PORT = 1883
MQTT_USERNAME = "publish"
MQTT_PASSWORD = "publish"
TOPIC = "pi5/camera/1"
CLIENT_ID = "bifrost_mqtt_subscriber"
# Function to get embeddings from Ollama
def get_ollama_embeddings(text):
    try:
        response = requests.post(
            f"{OLLAMA_HOST}/api/embeddings",
            json={"model": OLLAMA_MODEL, "text": text}
        )
        response.raise_for_status()
        return response.json().get("embedding", [])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching embeddings from Ollama: {e}")
        return []


# Query ChromaDB using embeddings
def query_chromadb(question):
    try:
        question_embedding = oembed.embed_query(question)

        if not question_embedding or not isinstance(question_embedding, list):
            return "Error: Failed to generate a valid embedding for the question."

        results = collection.query(
            query_embeddings=[question_embedding],
            n_results=N_RESULTS,
        )

        metadatas = results.get("metadatas", [[]])[0]

        if not metadatas:
            return "No relevant data found."

        # Format results
        context_lines = []
        for i, meta in enumerate(metadatas):
            label = meta.get("label", "unknown")
            bbox = meta.get("bbox", "{}")
            confidence = round(float(meta.get("confidence", 0)), 3)
            utc = meta.get("utc", "unknown")

            context_lines.append(
                f"Detection {i+1}: label={label}, confidence={confidence}, bbox={bbox}, timestamp={utc}"
            )

        return "\n".join(context_lines)

    except Exception as e:
        return f"Error during ChromaDB query: {str(e)}"
# Query Ollama with context
def ask_ollama(question, context):
    messages = [
        {
            "role": "system",
            "content": (
                "You are an AI assistant that answers questions about object detection results. "
                "The input data is a list of detections in JSON format. "
                "Each detection includes:\n"
                "- a 'label' describing the detected object,\n"
                "- a 'bbox' (bounding box) with 'x', 'y', 'width', and 'height' coordinates,\n"
                "- a 'confidence' score indicating the certainty of the classification,\n"
                "- and a 'utc' timestamp.\n\n"
                "Use this context to provide accurate and insightful answers."
            )
        },
        {
            "role": "user",
            "content": (
                f"Context data:\n{context}\n\n"
                f"Based on the above detection data, answer the following question with maximum of 80 words:\n"
                f"{question}\n\n"
                "Answer:"
            )
        }
    ]

    try:
        response = requests.post(
            f"{OLLAMA_HOST}/api/chat",
            json={"model": OLLAMA_MODEL, "messages": messages, "stream": False}
        )
        response.raise_for_status()
        return response.json().get("message", {}).get("content", "No response from Ollama.")
    except requests.exceptions.RequestException as e:
        return f"Error: {e}"

# Flask endpoints
@app.route("/collection", methods=["GET"])
def get_collection():
    results = collection.get()
    grouped = defaultdict(list)

    for doc_id, doc, meta in zip(results["ids"], results["documents"], results["metadatas"]):
        label = meta.get("label", "unknown")
        grouped[label].append({
            "id": doc_id,
            "bbox": meta.get("bbox"),
            "confidence": meta.get("confidence"),
            "utc": meta.get("utc"),
            "did": meta.get("Detection")
        })

    return jsonify(dict(grouped))

@app.route("/collections/<label>/stats", methods=["GET"])
def get_label_stats(label):
    try:
        results = collection.get()
        # Check if results are returned
        if not results or "documents" not in results or "metadatas" not in results:
            return jsonify({'error': 'No documents found'}), 404

        # Filter documents by the specified label
        filtered_docs = [
            doc for doc, meta in zip(results["documents"], results["metadatas"])
            if meta.get("label") == label
        ]

        total = len(filtered_docs)
        last_data = filtered_docs[-1] if filtered_docs else None
        additional_info = {
            "first_detection": filtered_docs[0] if filtered_docs else None,
            "last_detection": last_data
        }

        stats = {
            "total": total,
            "lastData": last_data,
            "additionalInfo": additional_info
        }

        return jsonify(stats)

    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route("/mqtt/start", methods=["POST"])
def start_mqtt_endpoint():
    global mqtt_client, mqtt_thread, mqtt_running
    if mqtt_running:
        return jsonify({"status": "already running"})

    def run_mqtt():
        global mqtt_client
        mqtt_client = connect_mqtt()
        mqtt_client.on_message = on_message
        mqtt_client.loop_forever()

    mqtt_thread = threading.Thread(target=run_mqtt, daemon=True)
    mqtt_thread.start()
    mqtt_running = True
    return jsonify({"status": "started"})


@app.route("/mqtt/stop", methods=["POST"])
def stop_mqtt_endpoint():
    global mqtt_client, mqtt_running
    if mqtt_client and mqtt_running:
        mqtt_client.disconnect()
        mqtt_client = None
        mqtt_running = False
        return jsonify({"status": "stopped"})
    return jsonify({"status": "not running"})


@app.route("/mqtt/status", methods=["GET"])
def mqtt_status():
    return jsonify({"running": mqtt_running})
@app.route('/collections')
def get_collections():
    try:
        result = []
        collection_names = chroma_client.list_collections()  # This returns a list of names (strings)
        for col_name in collection_names:
            col = chroma_client.get_collection(name=col_name)
            items = col.get(include=['metadatas'])  # embeddings not needed for labels
            for i, id in enumerate(items['ids']):
                label = items['metadatas'][i].get('label', 'Unlabeled')
                result.append({'id': id, 'label': label})
        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def query_chromadb_metadata(metadata):
    """
    Query ChromaDB by metadata criteria like label, confidence, etc.
    Filters based on exact string match of metadata fields.
    """
    try:
        # Dummy embedding for metadata-only query
        dummy_embedding = [0] * 3072  # match your actual embedding size
        results = collection.query(
            query_embeddings=[dummy_embedding],
            n_results=100  # increase if needed
        )

        filtered_results = []
        for doc_id, doc, meta_list in zip(results["ids"], results["documents"], results["metadatas"]):
            # Handle list-of-metadata format safely
            meta = meta_list[0] if isinstance(meta_list, list) and len(meta_list) > 0 else {}

            # Check if all metadata conditions match
            match = all(str(meta.get(k)) == str(v) for k, v in metadata.items())
            if match:
                filtered_results.append({
                    "id": doc_id,
                    "document": doc,
                    "metadata": meta
                })

        if not filtered_results:
            return "No matching metadata entries found."

        # Format matching results into readable context
        context_lines = []
        for i, result in enumerate(filtered_results):
            meta = result["metadata"]
            label = meta.get("label", "unknown")
            bbox = meta.get("bbox", "{}")
            confidence = round(float(meta.get("confidence", 0)), 3)
            utc = meta.get("utc", "unknown")
            context_lines.append(
                f"Detection {i+1}: label={label}, confidence={confidence}, bbox={bbox}, timestamp={utc}"
            )

        return "\n".join(context_lines)

    except Exception as e:
        return f"Error querying metadata: {str(e)}"

@app.route("/query", methods=["POST"])
def query():
    data = request.json
    question = data.get("question", "")
    context = query_chromadb(question)
    answer = ask_ollama(question, context)
    return jsonify({"context": context, "answer": answer})



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
def start_mqtt():
    client = connect_mqtt()
    client.on_message = on_message
    client.loop_forever()

def run():
    app.run(debug=True, port=5001)

if __name__ == '__main__':
    run()
