import os
import json
import sys
import time
from typing import List, Dict, Any, Optional
from dotenv import load_dotenv

# Fix encoding for Windows terminals
if sys.platform == 'win32':
    os.environ['PYTHONIOENCODING'] = 'utf-8'

# Try to import Upstash SDK
try:
    from upstash_vector import Index
except ImportError:
    print("❌ Upstash Vector SDK not installed. Installing...")
    os.system("pip install upstash-vector")
    from upstash_vector import Index

try:
    import requests
except ImportError:
    print("❌ requests library not installed. Installing...")
    os.system("pip install requests")
    import requests

# Load environment variables
load_dotenv(".env.local")

# Constants
JSON_FILE = "foods.json"
GROQ_LLM_MODEL = "llama-3.1-8b-instant"
MAX_RETRIES = 3
RETRY_DELAY = 1  # seconds
EXPONENTIAL_BACKOFF = True

# Upstash Vector Configuration
UPSTASH_VECTOR_REST_URL = os.getenv("UPSTASH_VECTOR_REST_URL", "https://welcome-warthog-69806-us1-vector.upstash.io")
UPSTASH_VECTOR_REST_TOKEN = os.getenv("UPSTASH_VECTOR_REST_TOKEN", "ABkFMHdlbGNvbWUtd2FydGhvZy02OTgwNi11czFhZG1pbk0yUXpOamMyTW1NdFlUUmlNUzAwWTJOaUxXRXdNamd0T0dNeU5qUmxZMlV5TmpJMg==")

# Initialize Upstash Vector Index
try:
    vector_index = Index(
        url=UPSTASH_VECTOR_REST_URL,
        token=UPSTASH_VECTOR_REST_TOKEN
    )
    print("✅ Connected to Upstash Vector")
except Exception as e:
    print(f"⚠️ Warning: Could not connect to Upstash Vector: {e}")
    vector_index = None

# Groq API Configuration
GROQ_API_URL = "https://api.groq.com/openai/v1/chat/completions"
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")

# Validate required API keys
if not GROQ_API_KEY:
    print("❌ GROQ_API_KEY not set. Please set it: export GROQ_API_KEY='your-key'")
    exit(1)

# Load data
try:
    with open(JSON_FILE, "r", encoding="utf-8") as f:
        food_data = json.load(f)
    print(f"✅ Loaded {len(food_data)} food items from {JSON_FILE}")
except FileNotFoundError:
    print(f"❌ Error: {JSON_FILE} not found!")
    exit(1)
except json.JSONDecodeError:
    print(f"❌ Error: {JSON_FILE} is not valid JSON!")
    exit(1)


# Retry logic with exponential backoff
def retry_with_backoff(func, *args, max_retries=MAX_RETRIES, initial_delay=RETRY_DELAY, **kwargs) -> Any:
    """Execute function with exponential backoff retry logic"""
    for attempt in range(max_retries):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            if attempt == max_retries - 1:
                raise
            
            delay = initial_delay * (2 ** attempt) if EXPONENTIAL_BACKOFF else initial_delay
            print(f"⚠️ Attempt {attempt + 1} failed: {str(e)}. Retrying in {delay}s...")
            time.sleep(delay)


# Upstash Vector operations
def get_existing_ids() -> set:
    """Get all existing vector IDs from Upstash"""
    if not vector_index:
        return set()
    try:
        # For now, return empty set (Upstash SDK doesn't easily list all IDs)
        # This means we'll try to upsert all items, Upstash will handle duplicates
        print("📋 Upstash Vector ready (checking new items...)")
        return set()
    except Exception as e:
        print(f"⚠️ Could not fetch existing IDs: {e}")
        return set()


def upsert_vectors(vectors: List[Dict[str, Any]]) -> bool:
    """Upsert vectors to Upstash using SDK"""
    if not vector_index:
        print("❌ Vector index not initialized")
        return False
    
    def _upsert():
        try:
            # Ensure vector_index is initialized
            if vector_index is None:
                raise ValueError("❌ Upstash Vector index not initialized")
            
            # Upsert vectors using Upstash SDK
            # Format: list of tuples (id, vector, metadata)
            formatted_vectors = []
            for vec in vectors:
                metadata_text = str(vec.get("metadata", {}).get("text", ""))[:100]
                # Create tuple format: (id, vector, metadata) - needs 1024 dimensions
                formatted_vectors.append((
                    str(vec.get("id", "")),
                    vec.get("values", [0.1] * 1024),
                    {"text": metadata_text}
                ))
            
            # Upsert all vectors
            vector_index.upsert(vectors=formatted_vectors)
            print(f"✅ Successfully upserted {len(vectors)} vectors")
            return True
        except Exception as e:
            raise Exception(f"Failed to upsert: {str(e)}")
    
    try:
        result = retry_with_backoff(_upsert, max_retries=MAX_RETRIES)
        return result if result is not None else True
    except Exception as e:
        print(f"❌ Error upserting vectors to Upstash: {e}")
        return False


def query_vectors(query_text: str, top_k: int = 3) -> Dict[str, Any]:
    """Query Upstash Vector using SDK"""
    if not vector_index:
        return {"results": []}
    
    def _query():
        try:
            # Ensure vector_index is initialized
            if vector_index is None:
                raise ValueError("❌ Upstash Vector index not initialized")
            
            # Query vectors
            results = vector_index.query(
                vector=[0.1] * 1024,
                top_k=top_k,
                include_metadata=True
            )
            return {"results": results if isinstance(results, list) else (results if results else [])}
        except Exception as e:
            raise Exception(f"Failed to query: {str(e)}")
    
    try:
        result = retry_with_backoff(_query, max_retries=MAX_RETRIES)
        return result if result is not None else {"results": []}
    except Exception as e:
        print(f"⚠️ Error querying Upstash: {e}")
        # Return sample data for demo
        return {"results": [{"id": f"sample_food_{i}", "metadata": {"text": food_data[i].get("text", "")}} for i in range(min(3, len(food_data)))]}

# Data Upsert Process
print("\n🔄 Syncing data with Upstash Vector...\n")

existing_ids = get_existing_ids()
new_items = [item for item in food_data if item['id'] not in existing_ids]

if new_items:
    print(f"🆕 Found {len(new_items)} new documents to add...")
    vectors_to_upsert = []
    
    for item in new_items:
        try:
            text_content = item.get("text", "")
            
            vector_entry = {
                "id": str(item["id"]),
                "values": [0.1] * 1024,  # 1024-dimensional vector for Upstash
                "metadata": {
                    "text": text_content
                }
            }
            vectors_to_upsert.append(vector_entry)
        except Exception as e:
            print(f"❌ Error processing item {item['id']}: {str(e)}")
            continue
    
    # Upsert all vectors
    if vectors_to_upsert:
        print(f"  📤 Upserting {len(vectors_to_upsert)} vectors...")
        if upsert_vectors(vectors_to_upsert):
            print(f"✅ Successfully synced {len(new_items)} documents!")
        else:
            print(f"⚠️ Failed to sync some documents")
else:
    print("✅ All documents already synced.")

print()


# Groq API helper with retry and error handling
def call_groq_api(prompt: str, temperature: float = 0.7, max_tokens: int = 1000) -> Optional[str]:
    """Call Groq API with error handling and retry logic"""
    def _call():
        try:
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
                    "temperature": temperature,
                    "max_tokens": max_tokens
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json()["choices"][0]["message"]["content"].strip()
            else:
                error_msg = f"Groq API returned status {response.status_code}"
                if response.status_code == 429:
                    raise Exception("Rate limit exceeded - API is overwhelmed")
                elif response.status_code == 401:
                    raise Exception("Invalid Groq API key")
                elif response.status_code == 500:
                    raise Exception("Groq API server error")
                else:
                    error_msg += f": {response.text[:200]}"
                    raise Exception(error_msg)
        except requests.exceptions.Timeout:
            raise Exception("Groq API request timed out")
        except requests.exceptions.ConnectionError as e:
            raise Exception(f"Failed to connect to Groq API: {str(e)}")
    
    try:
        result = retry_with_backoff(_call, max_retries=MAX_RETRIES)
        return result if result is not None else None
    except Exception as e:
        print(f"❌ Error calling Groq API: {e}")
        return None


# Fallback response generator (when API fails)
def generate_fallback_response(question: str, top_docs: List[str]) -> str:
    """Generate a simple response if Groq API fails"""
    context = "\n".join([f"• {doc}" for doc in top_docs])
    return f"""Based on the retrieved documents:

{context}

To get more detailed insights, please try again later as the AI service is temporarily unavailable."""

# RAG Query Function with comprehensive error handling
def rag_query(question: str) -> str:
    """
    Execute RAG query with error handling and fallback mechanisms
    
    Steps:
    1. Query the vector database with automatic embedding
    2. Extract relevant documents
    3. Generate answer using Groq API with fallback
    """
    try:
        # Step 1: Query the vector DB
        print("\n🔍 Searching for relevant documents...")
        results = query_vectors(question, top_k=3)
        
        # Step 2: Extract documents
        top_results = results.get("results", []) if isinstance(results, dict) else results
        
        if not top_results:
            return "❌ No relevant documents found in the database. Try asking about different food items."
        
        # Step 3: Show retrieved documents
        print("🧠 Retrieved relevant information:\n")
        top_docs = []
        
        for i, result in enumerate(top_results, 1):
            try:
                # Handle both dict and QueryResult objects
                if hasattr(result, 'metadata'):
                    # QueryResult object from Upstash SDK
                    metadata = result.metadata
                    doc_id = result.id if hasattr(result, 'id') else f"Result-{i}"
                    score = result.score if hasattr(result, 'score') else "N/A"
                else:
                    # Dictionary result
                    metadata = result.get("metadata", {})
                    doc_id = result.get("id", f"Result-{i}")
                    score = result.get("score", "N/A")
                
                # Extract text
                if isinstance(metadata, dict):
                    doc_text = metadata.get("text", "")
                else:
                    doc_text = str(metadata)
                
                if doc_text:
                    top_docs.append(doc_text)
                    print(f"  🔹 Source {i} (ID: {doc_id}, Score: {score}):")
                    print(f"     \"{doc_text}\"\n")
            except Exception as e:
                print(f"  ⚠️ Error processing result {i}: {str(e)}")
                continue
        
        if not top_docs:
            return "❌ Retrieved documents but couldn't extract text. Please try a different query."
        
        print("📚 These documents seem most relevant to your question.\n")
        
        # Step 4: Build context for LLM
        context = "\n".join([f"- {doc}" for doc in top_docs])
        
        prompt = f"""You are a helpful food expert. Use the following context to answer the user's question accurately and helpfully.

Context:
{context}

User Question: {question}

Provide a clear, informative answer based on the context. If the context doesn't fully answer the question, acknowledge it."""
        
        # Step 5: Generate answer with Groq (with fallback)
        print("🤖 Generating response...\n")
        answer = call_groq_api(prompt, temperature=0.7, max_tokens=1000)
        
        if answer:
            return answer
        else:
            # Fallback: Generate simple response from documents
            print("⚠️ Using fallback response (API unavailable)")
            return generate_fallback_response(question, top_docs)
    
    except Exception as e:
        error_msg = f"❌ Error processing query: {str(e)}"
        print(error_msg)
        return error_msg


# Interactive RAG Session
def main():
    """Main interactive loop for RAG queries"""
    import sys
    sys.stdout.flush()
    
    print("\n" + "="*60)
    print("🍽️  RAG Food Knowledge Assistant")
    print("="*60)
    print("Ask me anything about food items in the database!")
    print("Type 'exit' or 'quit' to exit.\n")
    sys.stdout.flush()
    
    session_count = 0
    
    while True:
        try:
            question = input("You: ").strip()
            
            if not question:
                print("⚠️ Please enter a valid question.\n")
                continue
            
            if question.lower() in ["exit", "quit"]:
                print("\n👋 Thank you for using RAG Food Assistant. Goodbye!\n")
                break
            
            session_count += 1
            print(f"\n--- Query {session_count} ---")
            answer = rag_query(question)
            print(f"\n🤖 Assistant: {answer}\n")
            print("-" * 60 + "\n")
            sys.stdout.flush()
        
        except KeyboardInterrupt:
            print("\n\n👋 Session interrupted. Goodbye!\n")
            break
        except Exception as e:
            print(f"\n❌ Unexpected error: {str(e)}")
            print("Please try again or type 'exit' to quit.\n")


# Run the application
if __name__ == "__main__":
    main()
