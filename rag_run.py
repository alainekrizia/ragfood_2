import json
try:
    import chromadb  # type: ignore
except ImportError:
    print("❌ The 'chromadb' module is not installed. Please install it with 'pip install chromadb'.")
    exit(1)

# Constants
JSON_FILE = "foods.json"
CHROMA_DB_DIR = "./chroma_db"

# Load data
with open(JSON_FILE, "r", encoding="utf-8") as f:
    food_data = json.load(f)

# Initialize ChromaDB client
client = chromadb.PersistentClient(path=CHROMA_DB_DIR)
collection = client.get_or_create_collection(
    name="foods",
    metadata={"hnsw:space": "cosine"}
)

# Add documents to ChromaDB
existing_ids = set()
try:
    # Try to get existing document count
    existing_count = collection.count()
    if existing_count > 0:
        # Get all existing IDs
        results = collection.get()
        existing_ids = set(results["ids"])
except:
    existing_ids = set()

new_items = [item for item in food_data if item['id'] not in existing_ids]

if new_items:
    print(f"🆕 Adding {len(new_items)} new documents to ChromaDB...")
    
    for item in new_items:
        # Enhance text with region/type
        enriched_text = item["text"]
        if "region" in item:
            enriched_text += f" This food is popular in {item['region']}."
        if "type" in item:
            enriched_text += f" It is a type of {item['type']}."

        collection.add(
            ids=[item["id"]],
            metadatas=[{
                "text": item["text"],
                "enriched_text": enriched_text
            }],
            documents=[enriched_text]
        )
    
    print(f"✅ Successfully added {len(new_items)} documents to ChromaDB!")
else:
    print("✅ All documents already in ChromaDB.")

# RAG query
def rag_query(question):
    # Step 1: Query ChromaDB
    results = collection.query(
        query_texts=[question],
        n_results=3
    )

    # Step 2: Extract documents
    top_docs = []
    
    if not results["ids"] or len(results["ids"][0]) == 0:
        return "❌ No relevant documents found in the database."

    # Step 3: Show retrieved documents
    print("\n🧠 Retrieving relevant information...\n")

    for i, (doc_id, doc_text) in enumerate(zip(results["ids"][0], results["documents"][0])):
        top_docs.append(doc_text)
        print(f"🔹 Source {i + 1} (ID: {doc_id}):")
        print(f"    \"{doc_text}\"\n")

    print("📚 These are the most relevant documents found.\n")

    # Step 4: Build simple summary
    context = "\n".join(top_docs)
    summary = f"""Based on the documents found:

{context}"""
    
    return summary


# Interactive loop
print("\n🧠 RAG is ready. Ask a question (type 'exit' to quit):\n")
while True:
    question = input("You: ")
    if question.lower() in ["exit", "quit"]:
        print("👋 Goodbye!")
        break
    answer = rag_query(question)
    print("🤖:", answer)

