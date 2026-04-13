'use server'

import { Index } from '@upstash/vector'
import { Groq } from 'groq-sdk'
import foodsData from '@/foods.json'

interface QueryResult {
  success: boolean
  response?: string
  sources?: Array<{
    text: string
    region: string
    type: string
  }>
  error?: string
}

const index = new Index({
  url: process.env.UPSTASH_VECTOR_REST_URL,
  token: process.env.UPSTASH_VECTOR_REST_TOKEN,
})

const groq = new Groq({
  apiKey: process.env.GROQ_API_KEY,
})

// Create a semantic embedding by analyzing word importance
function generateEmbedding(text: string): number[] {
  const vector: number[] = new Array(1024).fill(0)
  
  // Important keywords for food classification
  const foodKeywords = [
    'sushi', 'ramen', 'tempura', 'miso', 'okonomiyaki', 'japanese',
    'adobo', 'lechon', 'sinigang', 'patatim', 'pancit', 'filipin',
    'curry', 'biryani', 'samosa', 'paneer', 'dosa', 'tandoori',
    'pad thai', 'tom yum', 'green curry', 'thai',
    'pho', 'vietnamese',
    'peking', 'kung pao', 'mapo tofu', 'dim sum', 'chow mein', 'chinese',
    'nasi goreng', 'rendang', 'indonesian',
    'spring roll', 'dumpling', 'noodle', 'soup', 'stir-fry',
    'fish', 'meat', 'chicken', 'pork', 'beef', 'seafood',
    'rice', 'noodles', 'bread', 'pastry', 'dessert',
    'spicy', 'sweet', 'sour', 'savory', 'creamy',
  ]
  
  const lowerText = text.toLowerCase()
  let keywordMatchCount = 0
  
  // Score each keyword
  for (let i = 0; i < foodKeywords.length; i++) {
    if (lowerText.includes(foodKeywords[i])) {
      vector[i % 1024] += 1.0
      keywordMatchCount++
    }
  }
  
  // Add position-based scores (important words often appear early)
  const words = lowerText.split(/\s+/)
  for (let i = 0; i < Math.min(words.length, 20); i++) {
    const word = words[i]
    if (word.length > 3) {
      const charSum = word.split('').reduce((sum, c) => sum + c.charCodeAt(0), 0)
      const idx = charSum % 1024
      vector[idx] += (1 - i / 20) * 0.5 // Earlier words get higher weight
    }
  }
  
  // Add region-based signals
  const regions = ['japan', 'filipin', 'thai', 'vietn', 'chinese', 'indian', 'korean', 'italian', 'mexican']
  for (let i = 0; i < regions.length; i++) {
    if (lowerText.includes(regions[i])) {
      for (let j = 0; j < 50; j++) {
        vector[(i * 50 + j) % 1024] += 0.8
      }
    }
  }
  
  // Normalize the vector
  let norm = Math.sqrt(vector.reduce((sum, v) => sum + v * v, 0))
  if (norm > 0) {
    for (let i = 0; i < vector.length; i++) {
      vector[i] /= norm
    }
  } else {
    // If all zeros, create a uniform distribution
    for (let i = 0; i < vector.length; i++) {
      vector[i] = 1 / Math.sqrt(1024)
    }
  }
  
  return vector
}

// Initialize vector database with foods
async function initializeVectorDb() {
  if (!foodsData.length) {
    console.warn('[RAG] No food data to initialize')
    return
  }

  try {
    console.log('[RAG] Initializing Upstash Vector database...')
    
    // Upload vectors in batches
    const batchSize = 50
    for (let i = 0; i < foodsData.length; i += batchSize) {
      const batch = foodsData.slice(i, i + batchSize)
      const vectors = batch.map((food) => ({
        id: food.id,
        vector: generateEmbedding(food.text),
        metadata: {
          text: food.text,
          region: food.region,
          type: food.type,
        },
      }))

      await index.upsert(vectors)
      console.log(`[RAG] Upserted ${Math.min(i + batchSize, foodsData.length)}/${foodsData.length} items`)
    }
    
    console.log('[RAG] Vector database initialized successfully')
  } catch (error) {
    console.error('[RAG] Error initializing vector database:', error)
  }
}

// Call initialization on module load
initializeVectorDb().catch(console.error)

export async function queryFood(userQuery: string): Promise<QueryResult> {
  try {
    if (!userQuery.trim()) {
      return {
        success: false,
        error: 'Please enter a question about food.',
      }
    }

    if (!process.env.UPSTASH_VECTOR_REST_URL || !process.env.UPSTASH_VECTOR_REST_TOKEN) {
      return {
        success: false,
        error: 'Vector store not configured. Please set up Upstash Vector.',
      }
    }

    if (!process.env.GROQ_API_KEY) {
      return {
        success: false,
        error: 'AI service not configured. Please set up Groq API.',
      }
    }

    // Query the vector store for relevant documents
    const queryEmbedding = generateEmbedding(userQuery)
    const queryResults = await index.query({
      vector: queryEmbedding,
      topK: 5,
      includeMetadata: true,
    })

    if (!queryResults || queryResults.length === 0) {
      return {
        success: false,
        error: 'No relevant food information found. Try asking about different foods.',
      }
    }

    // Extract context from results
    const sources = queryResults
      .map((result: any) => ({
        text: result.metadata?.text || '',
        region: result.metadata?.region || '',
        type: result.metadata?.type || '',
      }))
      .filter((source: any) => source.text)

    const context = sources
      .map((source: any) => `${source.text} (Region: ${source.region}, Type: ${source.type})`)
      .join('\n\n')

    if (!context) {
      return {
        success: false,
        error: 'Unable to extract food information from results.',
      }
    }

    // Generate response using Groq
    const message = await groq.chat.completions.create({
      model: 'llama-3.3-70b-versatile',
      max_tokens: 1024,
      messages: [
        {
          role: 'user',
          content: `You are a helpful food knowledge assistant. Based on the following food information, answer the user's question. Keep your response concise and informative.\n\nFood Information:\n${context}\n\nUser Question: ${userQuery}`,
        },
      ],
    })

    const responseText = message.choices[0].message.content || 'Unable to generate response'

    return {
      success: true,
      response: responseText,
      sources,
    }
  } catch (error) {
    console.error('[RAG] Query error:', error)
    const errorMessage = error instanceof Error ? error.message : 'Unknown error occurred'
    return {
      success: false,
      error: `Failed to process query: ${errorMessage}`,
    }
  }
}
