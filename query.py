import chromadb
import requests
from langchain_community.embeddings import OllamaEmbeddings

# ChromaDB configuration
client = chromadb.PersistentClient(path="./chroma_data")
collection = client.get_or_create_collection("bifrost_data")

# Ollama configuration
OLLAMA_MODEL = "phi3"  # Replace with your model
OLLAMA_HOST = "http://localhost:11434"
oembed = OllamaEmbeddings(base_url=OLLAMA_HOST, model=OLLAMA_MODEL, temperature=0)


# Function to get embeddings from Ollama
def get_ollama_embeddings(text):
    try:
        response = requests.post(
            f"{OLLAMA_HOST}/api/embeddings",
            json={"model": OLLAMA_MODEL, "text": text}  # Changed "prompt" to "text"
        )
        response.raise_for_status()  # Raise error if request fails
        return response.json().get("embedding", [])
    except requests.exceptions.RequestException as e:
        print(f"Error fetching embeddings from Ollama: {e}")
        return []


# Query ChromaDB using embeddings
def query_chromadb(question):
    # Generate embeddings using the same model as ingestion
    question_embedding = oembed.embed_query(question)

    if not question_embedding:
        return "Error: Could not generate embeddings."

    # Perform similarity search
    results = collection.query(
        query_embeddings=[question_embedding],
        n_results=5,
    )

    metadatas = results.get("metadatas", [[]])[0]
    if not metadatas:
        return "No relevant data found."

    # Build a cleaner context string from the metadata
    context_lines = []
    for i, meta in enumerate(metadatas):
        label = meta.get("label", "unknown")
        bbox = meta.get("bbox", "{}")
        confidence = round(meta.get("confidence", 0), 3)
        utc = meta.get("utc", "unknown")
        context_lines.append(
            f"Detection {i+1}: label={label}, confidence={confidence}, bbox={bbox}, timestamp={utc}"
        )

    context = "\n".join(context_lines)
    return context
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
                f"Based on the above detection data, answer the following question:\n"
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


if __name__ == "__main__":
    print("Available collections:", client.list_collections())
    question = input("Ask a question about the captured data: ")

    # Fetch context from ChromaDB using embedding search
    context = query_chromadb(question)
    print(f"Context: {context}")

    # Query Ollama with retrieved context
    answer = ask_ollama(question, context)

    print(f"Ollama's Answer: {answer}")
