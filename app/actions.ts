'use server'

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

const groq = new Groq({
  apiKey: process.env.GROQ_API_KEY,
})

// Direct keyword-based search function
function searchFoods(query: string): Array<{ text: string; region: string; type: string }> {
  const queryLower = query.toLowerCase()
  const queryWords = queryLower.split(/\s+/).filter((w) => w.length > 2)

  // Score each food item based on keyword matches
  const scoredFoods = (foodsData as any[]).map((food) => {
    const textLower = food.text.toLowerCase()
    const regionLower = food.region.toLowerCase()
    const typeLower = food.type.toLowerCase()

    let score = 0

    // Match query words in food text
    for (const word of queryWords) {
      if (textLower.includes(word)) score += 5
      if (regionLower.includes(word)) score += 3
      if (typeLower.includes(word)) score += 2
    }

    return { food, score }
  })

  // Sort by score and return top 5 matches
  return scoredFoods
    .filter((item) => item.score > 0)
    .sort((a, b) => b.score - a.score)
    .slice(0, 5)
    .map((item) => ({
      text: item.food.text,
      region: item.food.region,
      type: item.food.type,
    }))
}

export async function queryFood(userQuery: string): Promise<QueryResult> {
  try {
    if (!userQuery.trim()) {
      return {
        success: false,
        error: 'Please enter a question about food.',
      }
    }

    if (!process.env.GROQ_API_KEY) {
      return {
        success: false,
        error: 'AI service not configured. Please set up Groq API.',
      }
    }

    // Search for relevant foods using keyword matching
    const sources = searchFoods(userQuery)

    if (sources.length === 0) {
      return {
        success: false,
        error: 'No relevant food information found. Try asking about different foods or cuisines.',
      }
    }

    // Build context from matched foods
    const context = sources
      .map((source) => `${source.text} (Region: ${source.region}, Type: ${source.type})`)
      .join('\n\n')

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
