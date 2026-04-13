'use server'

import { Index } from '@upstash/vector'
import { Groq } from 'groq-sdk'

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
    const queryResults = await index.query({
      data: userQuery,
      topK: 5,
      includeMetadata: true,
    })

    if (!queryResults || queryResults.length === 0) {
      return {
        success: false,
        error: 'No relevant food information found. Try different keywords.',
      }
    }

    // Extract source documents
    const sources = queryResults
      .filter((result) => result.metadata)
      .map((result) => ({
        text: (result.metadata as Record<string, unknown>).text as string,
        region: (result.metadata as Record<string, unknown>).region as string,
        type: (result.metadata as Record<string, unknown>).type as string,
      }))

    // Build context from retrieved documents
    const context = sources
      .map((doc) => `${doc.text} (${doc.region}, ${doc.type})`)
      .join('\n')

    // Generate response using Groq
    const message = await groq.chat.completions.create({
      model: 'mixtral-8x7b-32768',
      max_tokens: 1024,
      messages: [
        {
          role: 'user',
          content: `You are a helpful food knowledge assistant. Based on the following food information, answer the user's question. Keep your response concise and informative.\n\nFood Information:\n${context}\n\nUser Question: ${userQuery}`,
        },
      ],
    })

    const responseText =
      message.choices[0].message.content || 'Unable to generate response'

    return {
      success: true,
      response: responseText,
      sources,
    }
  } catch (error) {
    console.error('Error querying food RAG:', error)

    if (error instanceof Error) {
      if (error.message.includes('rate limit')) {
        return {
          success: false,
          error: 'Rate limit reached. Please wait a moment and try again.',
        }
      }
      return {
        success: false,
        error: `Error: ${error.message}`,
      }
    }

    return {
      success: false,
      error: 'An unexpected error occurred. Please try again.',
    }
  }
}
