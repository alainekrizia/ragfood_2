# Quick Start Guide

## Prerequisites

```bash
# Install dependencies
pip install requests python-dotenv

# Ensure food data exists
ls foods.json  # Should exist with food data
```

## Configuration

### 1. Set Groq API Key

**Option A: Environment Variable**
```bash
export GROQ_API_KEY="your-groq-api-key"
```

**Option B: Shell Profile (Linux/Mac)**
```bash
echo 'export GROQ_API_KEY="your-key"' >> ~/.bashrc
source ~/.bashrc
```

**Option C: Windows PowerShell**
```powershell
$env:GROQ_API_KEY="your-groq-api-key"
```

### 2. Verify Upstash Credentials

The `.env.local` file should contain:
```env
UPSTASH_VECTOR_REST_URL=https://your-instance-url
UPSTASH_VECTOR_REST_TOKEN=your-token
```

## Running the Application

```bash
# Navigate to project directory
cd path/to/ragfood

# Run with Python 3.8+
python rag_run_upstash.py
```

## Expected Output

### Initialization (First Run)
```
✅ Loaded 150 food items from foods.json

🔄 Syncing data with Upstash Vector...

🆕 Found 150 new documents to add to Upstash Vector...
  📤 Batch upserting 50 vectors...
  ✅ Successfully upserted 50 vectors
  📤 Batch upserting 50 vectors...
  ✅ Successfully upserted 50 vectors
  📤 Upserting final batch of 50 vectors...
  ✅ Successfully upserted 50 vectors
✅ Successfully synced 150 new documents!

============================================================
🍽️  RAG Food Knowledge Assistant
============================================================
Ask me anything about food items in the database!
Type 'exit' or 'quit' to exit.

You: 
```

### Query Execution
```
You: Tell me about pizza

--- Query 1 ---

🔍 Searching for relevant documents...
🧠 Retrieved relevant information:

  🔹 Source 1 (ID: pizza_001, Score: 0.92):
     "Pizza is a savory dish of Italian origin..."

  🔹 Source 2 (ID: pizza_002, Score: 0.88):
     "Famous types include Margherita, Pepperoni..."

  🔹 Source 3 (ID: italian_cuisine, Score: 0.76):
     "Italian cuisine features many iconic dishes..."

📚 These documents seem most relevant to your question.

🤖 Generating response...

🤖 Assistant: Pizza is a beloved Italian dish with a rich history...
[Full response from Groq]

------------------------------------------------------------
```

## Troubleshooting

### Error: "GROQ_API_KEY not set"

**Solution:**
```bash
# Verify the key is set
echo $GROQ_API_KEY  # Should print your key

# If empty, set it again
export GROQ_API_KEY="your-key"
```

### Error: "No relevant documents found"

**Causes:**
- Empty or filtered food data
- Query is too different from available content
- Vector database is empty

**Solutions:**
```bash
# Check food data
python -c "import json; data = json.load(open('foods.json')); print(f'Items: {len(data)}')"

# Try more general queries
# "Tell me about food"
# "What cuisines exist?"
```

### Error: "Groq API returned status 429"

**Meaning:** Rate limit exceeded

**Solution:**
- Wait a few minutes
- Reduce query frequency
- Upgrade Groq plan if needed

### Error: "Invalid Groq API key"

**Solution:**
- Get new key from https://console.groq.com
- Set it again: `export GROQ_API_KEY="new-key"`

### Error: "Failed to connect to Upstash"

**Solutions:**
```bash
# Test connection
curl -X POST "https://your-upstash-url/scan" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"limit": 1}'

# Verify .env.local
cat .env.local

# Check internet connection
ping google.com
```

## Performance Tips

### 1. First Run Takes Longer
- Initial sync uploads all vectors to Upstash
- Subsequent runs only add new items
- Progress shown with batch counts

### 2. Optimize Queries
```
❌ Slow: "Tell me everything about all foods"
✅ Fast: "What cuisine is pizza from?"
```

### 3. Parallel Processing
- Batch processing automatically used (50 items/batch)
- No additional configuration needed

## Configuration Customization

### Retry Settings

Edit these in `rag_run_upstash.py`:
```python
MAX_RETRIES = 3          # Try 3 times before giving up
RETRY_DELAY = 1          # Start with 1 second delay
EXPONENTIAL_BACKOFF = True  # Double delay each retry
```

**Examples:**
```
Retry 1: Wait 1s
Retry 2: Wait 2s
Retry 3: Wait 4s
```

### LLM Parameters

```python
call_groq_api(
    prompt,
    temperature=0.7,    # 0.0=deterministic, 1.0=creative
    max_tokens=1000     # Response length limit
)
```

## Getting Help

1. **Check logs**: Look at terminal output for error messages
2. **API status**: Verify services are running
   - Groq: https://status.groq.com
   - Upstash: https://status.upstash.io
3. **API keys**: Regenerate from respective dashboards

## Advanced Features

### Monitoring Query Performance

The application shows:
- Query number (`Query 1, 2, 3...`)
- Similarity scores for each document
- Retrieved document IDs
- Source location and count

### Fallback Responses

If Groq API is unavailable:
- System automatically shows retrieved documents
- Explains AI service is temporarily unavailable
- User can still see raw data and try again later

### Batch Processing

Data sync automatically:
- Groups items into 50-item batches
- Shows progress for each batch
- Continues even if one batch fails (partial success)

## Next Steps

1. **Customize queries**: Try different questions
2. **Update food data**: Modify `foods.json` to add new items
3. **Monitor performance**: Check response times and accuracy
4. **Enhance prompts**: Modify system prompts in `rag_query()` for better responses
5. **Scale up**: Monitor API usage and upgrade plans if needed

---

**Need more help?** Check `FEATURES_IMPLEMENTED.md` for detailed technical information.
