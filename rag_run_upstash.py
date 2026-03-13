import os
import json
import requests

# Constants
JSON_FILE = "foods.json"
HF_MODEL = "BAAI/bge-small-en-v1.5"  # Hugging Face embedding model
GROQ_LLM_MODEL = "llama-3.1-8b-instant"

# Upstash Vector Configuration
UPSTASH_VECTOR_REST_URL = "https://welcome-warthog-69806-us1-vector.upstash.io"
UPSTASH_VECTOR_REST_TOKEN = "ABkFMHdlbGNvbWUtd2FydGhvZy02OTgwNi11czFhZG1pbk0yUXpOamMyTW1NdFlUUmlNUzAwWTJOaUxXRXdNamd0T0dNeU5qUmxZMlV5TmpJMg=="

# Groq API Configuration
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")  # Set via environment variable

# Hugging Face API Configuration
HF_API_URL = "https://router.huggingface.co/pipeline/feature-extraction"
HF_API_KEY = os.getenv("HF_API_KEY", "")  # Set via environment variable

# Validate API keys
if not GROQ_API_KEY:
    print("❌ GROQ_API_KEY not set. Please set it: export GROQ_API_KEY='your-key'")
    exit(1)
if not HF_API_KEY:
    print("❌ HF_API_KEY not set. Please set it: export HF_API_KEY='your-key'")
    exit(1)

# Load data
with open(JSON_FILE, "r", encoding="utf-8") as f:
    food_data = json.load(f)

# Hugging Face embedding function
def get_embedding(text):
    """Get embeddings from Hugging Face Inference API"""
    headers = {"Authorization": f"Bearer {HF_API_KEY}"}
    response = requests.post(
        f"{HF_API_URL}/{HF_MODEL}",
        headers=headers,
        json={"inputs": text}
    )
    if response.status_code == 200:
        # Hugging Face returns a list of embeddings
        embeddings = response.json()
        if isinstance(embeddings, list) and len(embeddings) > 0:
            return embeddings[0]
        return embeddings
    else:
        print(f"❌ Hugging Face API error: {response.status_code}")
        print(response.text)
        raise Exception(f"Failed to get embedding: {response.text}")

# Upstash Vector API helpers
def upstash_headers():
    return {
        "Authorization": f"Bearer {UPSTASH_VECTOR_REST_TOKEN}",
        "Content-Type": "application/json"
    }

def get_existing_ids():
    """Get all existing vector IDs from Upstash"""
    try:
        # Query with empty results to get metadata (or fetch all with range)
        response = requests.post(
            f"{UPSTASH_VECTOR_REST_URL}/scan",
            headers=upstash_headers(),
            json={"limit": 10000}
        )
        if response.status_code == 200:
            data = response.json()
            return set(item.get("id", "") for item in data.get("vectors", []))
        return set()
    except Exception as e:
        print(f"⚠️ Error fetching existing IDs: {e}")
        return set()

def upsert_vectors(vectors):
    """Upsert vectors to Upstash"""
    response = requests.post(
        f"{UPSTASH_VECTOR_REST_URL}/upsert",
        headers=upstash_headers(),
        json={"vectors": vectors}
    )
    return response.status_code == 200

def query_vectors(query_embedding, top_k=3):
    """Query Upstash Vector"""
    response = requests.post(
        f"{UPSTASH_VECTOR_REST_URL}/query",
        headers=upstash_headers(),
        json={
            "vector": query_embedding,
            "top_k": top_k,
            "include_metadata": True
        }
    )
    if response.status_code == 200:
        return response.json()
    return {"results": []}

# Add only new items
# Add only new items
existing_ids = get_existing_ids()
new_items = [item for item in food_data if item['id'] not in existing_ids]

if new_items:
    print(f"🆕 Adding {len(new_items)} new documents to Upstash Vector...")
    vectors_to_upsert = []
    
    for item in new_items:
        # Enhance text with region/type
        enriched_text = item["text"]
        if "region" in item:
            enriched_text += f" This food is popular in {item['region']}."
        if "type" in item:
            enriched_text += f" It is a type of {item['type']}."

        emb = get_embedding(enriched_text)

        vectors_to_upsert.append({
            "id": item["id"],
            "values": emb,
            "metadata": {
                "text": item["text"],
                "enriched_text": enriched_text
            }
        })
    
    if upsert_vectors(vectors_to_upsert):
        print(f"✅ Successfully added {len(new_items)} vectors to Upstash!")
    else:
        print("❌ Error adding vectors to Upstash")
else:
    print("✅ All documents already in Upstash Vector.")

# RAG query
def rag_query(question):
    # Step 1: Embed the user question
    q_emb = get_embedding(question)

    # Step 2: Query the vector DB
    results = query_vectors(q_emb, top_k=3)

    # Step 3: Extract documents
    top_results = results.get("results", [])
    
    if not top_results:
        return "❌ No relevant documents found in the vector database."

    # Step 4: Show friendly explanation of retrieved documents
    print("\n🧠 Retrieving relevant information to reason through your question...\n")

    top_docs = []
    for i, result in enumerate(top_results):
        doc_text = result.get("metadata", {}).get("text", "")
        doc_id = result.get("id", "")
        top_docs.append(doc_text)
        print(f"🔹 Source {i + 1} (ID: {doc_id}):")
        print(f"    \"{doc_text}\"\n")

    print("📚 These seem to be the most relevant pieces of information to answer your question.\n")

    # Step 5: Build prompt from context
    context = "\n".join(top_docs)

    prompt = f"""Use the following context to answer the question.

Context:
{context}

Question: {question}
Answer:"""

    # Step 6: Generate answer with Groq
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    response = requests.post(
        GROQ_API_URL,
        headers=headers,
        json={
            "model": GROQ_LLM_MODEL,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 1000
        }
    )

    # Step 7: Return final result
    if response.status_code == 200:
        return response.json()["choices"][0]["message"]["content"].strip()
    else:
        print(f"❌ Groq API error: {response.status_code}")
        print(response.text)
        return f"Error generating response: {response.text}"


# Interactive loop
print("\n🧠 RAG is ready. Ask a question (type 'exit' to quit):\n")
while True:
    question = input("You: ")
    if question.lower() in ["exit", "quit"]:
        print("👋 Goodbye!")
        break
    answer = rag_query(question)
    print("🤖:", answer)
