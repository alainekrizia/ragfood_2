Here’s a clear, beginner-friendly `README.md` for your RAG project, designed to explain what it does, how it works, and how someone can run it from scratch.

---

## 📄 `README.md`

````markdown
# Food RAG - AI-Powered Food Knowledge Assistant

A full-stack Retrieval-Augmented Generation (RAG) application for food knowledge using Next.js, Upstash Vector, and Groq AI.

**Live chat interface** → Ask questions about foods, cuisines, and recipes from around the world, with citations to food sources.

## Features

- **Interactive Chat UI**: Modern, responsive chat interface built with React
- **Retrieval-Augmented Generation**: Queries vector database before generating responses
- **Real-time AI Responses**: Powered by Groq's fast LLM inference
- **Source Attribution**: Each response includes citations to relevant food items
- **Error Handling**: Graceful fallbacks and user-friendly error messages
- **Food-themed Design**: Warm colors (oranges, greens, gold) inspired by food and cooking

## Tech Stack

### Frontend
- **Next.js 16** - React framework with App Router
- **React 19** - UI library
- **Tailwind CSS** - Styling
- **Lucide React** - Icons

### Backend
- **Upstash Vector** - Serverless vector database for embeddings
- **Groq API** - Fast LLM inference for generating responses
- **Server Actions** - Next.js server-side functions for secure API calls

### Data
- **foods.json** - Knowledge base with 90+ food items from 15+ regions

## Quick Start

### Prerequisites
- Node.js 18+
- API keys for:
  - Upstash Vector (REST URL + Token)
  - Groq API

### Setup

1. **Clone and install**
   ```bash
   git clone https://github.com/alainekrizia/ragfood_2.git
   cd ragfood_2
   npm install
   ```

2. **Configure environment variables**
   ```bash
   cp .env.local.example .env.local
   ```
   Fill in your credentials:
   ```
   UPSTASH_VECTOR_REST_URL=https://...
   UPSTASH_VECTOR_REST_TOKEN=...
   GROQ_API_KEY=...
   ```

3. **Run development server**
   ```bash
   npm run dev
   ```
   Open http://localhost:3000

## Project Structure

```
├── app/
│   ├── layout.tsx           # Root layout with metadata
│   ├── page.tsx             # Main page
│   ├── globals.css          # Global styles & design tokens
│   └── actions.ts           # Server actions for RAG queries
├── components/
│   └── ChatInterface.tsx     # Chat UI component
├── foods.json               # Food knowledge base
├── package.json
├── tailwind.config.ts
└── README.md
```

## How It Works

1. **User submits query** via chat interface
2. **Server Action** (`queryFood`) receives the question
3. **Vector search** against Upstash Vector returns top 5 relevant foods
4. **Context building** from retrieved documents
5. **LLM generation** using Groq API with the context
6. **Response + sources** returned to user

## Deployment

### Deploy to Vercel

```bash
# Connect your repo and push to GitHub
# In Vercel dashboard, add environment variables:
# - UPSTASH_VECTOR_REST_URL
# - UPSTASH_VECTOR_REST_TOKEN
# - GROQ_API_KEY
```

## Python Scripts (Local Development)

The repository includes Python RAG implementations for testing:

- **`rag_run.py`** - ChromaDB-based RAG (local embeddings with Ollama)
- **`rag_run_upstash.py`** - Upstash Vector with retry logic and Groq integration
- **`debug_groq.py`** - Test Groq API connectivity
- **`test_app.py`** - Test the Upstash RAG workflow

Run Python scripts:
```bash
# Install Python dependencies
pip install chromadb requests upstash-vector groq

# Run tests
python test_app.py
```

## Color Palette

- **Primary Orange**: `#d4602e` - Main interactive elements
- **Forest Green**: `#2d5016` - Secondary actions and accents
- **Gold**: `#c9a961` - Highlights and sources
- **Cream**: `#faf8f3` - Background
- **Dark Gray**: `#1a1a1a` - Text

## Error Handling

The app handles:
- Empty query validation
- Missing API credentials detection
- Rate limiting from Groq (free tier)
- Vector store connectivity issues
- Graceful fallbacks with helpful messages

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "Vector store not configured" | Check `.env.local` has correct Upstash credentials |
| "AI service not configured" | Verify `GROQ_API_KEY` is set and valid |
| "Rate limit reached" | Wait a moment - Groq free tier has limits |
| "No relevant food information" | Try different keywords or broader terms |

## Learning Resources

- [Next.js Documentation](https://nextjs.org/docs)
- [Upstash Vector](https://upstash.com/docs/vector/overall/getstarted)
- [Groq API](https://console.groq.com/docs)
- [RAG Pattern](https://en.wikipedia.org/wiki/Retrieval-augmented_generation)

## Credits

**Original RAG Demo**: Built with ChromaDB + Ollama local LLM
**Web Application**: Next.js + Upstash Vector + Groq AI migration  
**Food Knowledge Base**: 90+ global cuisines and recipes
**Contributors**: Alaine Demate, Callum, and the RAG community
