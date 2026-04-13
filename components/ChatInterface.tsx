'use client'

import { useState, useRef, useEffect } from 'react'
import { queryFood } from '@/app/actions'
import { MessageCircle, Send, Loader, AlertCircle, ChefHat } from 'lucide-react'

interface Message {
  id: string
  type: 'user' | 'assistant' | 'error'
  content: string
  sources?: Array<{
    text: string
    region: string
    type: string
  }>
}

export function ChatInterface() {
  const [messages, setMessages] = useState<Message[]>([
    {
      id: '1',
      type: 'assistant',
      content: 'Welcome to Food RAG! Ask me anything about foods, cuisines, and recipes from around the world. What would you like to know?',
    },
  ])
  const [input, setInput] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault()

    if (!input.trim() || isLoading) return

    // Add user message
    const userMessage: Message = {
      id: Date.now().toString(),
      type: 'user',
      content: input,
    }

    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setIsLoading(true)

    try {
      const result = await queryFood(input)

      if (result.success) {
        const assistantMessage: Message = {
          id: (Date.now() + 1).toString(),
          type: 'assistant',
          content: result.response || 'Unable to generate a response.',
          sources: result.sources,
        }
        setMessages((prev) => [...prev, assistantMessage])
      } else {
        const errorMessage: Message = {
          id: (Date.now() + 1).toString(),
          type: 'error',
          content: result.error || 'An error occurred while processing your query.',
        }
        setMessages((prev) => [...prev, errorMessage])
      }
    } catch (error) {
      const errorMessage: Message = {
        id: (Date.now() + 1).toString(),
        type: 'error',
        content: 'An unexpected error occurred. Please try again.',
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setIsLoading(false)
    }
  }

  return (
    <div className="flex flex-col h-screen bg-background">
      {/* Header */}
      <header className="border-b border-neutral-light bg-white shadow-sm">
        <div className="max-w-2xl mx-auto px-4 py-4 flex items-center gap-3">
          <ChefHat className="w-6 h-6 text-primary" />
          <div>
            <h1 className="text-xl font-bold text-foreground">Food RAG</h1>
            <p className="text-xs text-neutral-dark">AI-powered food knowledge assistant</p>
          </div>
        </div>
      </header>

      {/* Chat Messages */}
      <div className="flex-1 overflow-y-auto px-4 py-6 space-y-6">
        <div className="max-w-2xl mx-auto w-full space-y-6">
          {messages.map((message) => (
            <div key={message.id} className="flex gap-3">
              {message.type === 'user' ? (
                <>
                  <div className="flex-1" />
                  <div className="max-w-xs lg:max-w-md bg-primary text-white rounded-lg p-3">
                    <p className="text-sm">{message.content}</p>
                  </div>
                </>
              ) : message.type === 'error' ? (
                <>
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-red-100 flex items-center justify-center">
                    <AlertCircle className="w-5 h-5 text-red-600" />
                  </div>
                  <div className="flex-1 bg-red-50 border border-red-200 rounded-lg p-3">
                    <p className="text-sm text-red-800">{message.content}</p>
                  </div>
                </>
              ) : (
                <>
                  <div className="flex-shrink-0 w-8 h-8 rounded-full bg-secondary flex items-center justify-center">
                    <MessageCircle className="w-5 h-5 text-white" />
                  </div>
                  <div className="flex-1 space-y-3">
                    <div className="bg-neutral-light rounded-lg p-3">
                      <p className="text-sm text-foreground whitespace-pre-wrap">{message.content}</p>
                    </div>
                    {message.sources && message.sources.length > 0 && (
                      <div className="bg-accent bg-opacity-10 rounded-lg p-3 border border-accent border-opacity-20">
                        <p className="text-xs font-semibold text-secondary mb-2">Food Sources:</p>
                        <div className="space-y-1">
                          {message.sources.slice(0, 3).map((source, idx) => (
                            <div
                              key={idx}
                              className="text-xs text-neutral-dark bg-white bg-opacity-60 rounded p-2"
                            >
                              <p className="font-medium">{source.text}</p>
                              <p className="text-xs opacity-75">
                                {source.region} • {source.type}
                              </p>
                            </div>
                          ))}
                        </div>
                      </div>
                    )}
                  </div>
                </>
              )}
            </div>
          ))}
          {isLoading && (
            <div className="flex gap-3">
              <div className="flex-shrink-0 w-8 h-8 rounded-full bg-secondary flex items-center justify-center">
                <Loader className="w-5 h-5 text-white animate-spin" />
              </div>
              <div className="bg-neutral-light rounded-lg p-3">
                <p className="text-sm text-foreground">Thinking...</p>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input Area */}
      <div className="border-t border-neutral-light bg-white">
        <form onSubmit={handleSubmit} className="max-w-2xl mx-auto px-4 py-4">
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              placeholder="Ask about food, cuisines, or recipes..."
              disabled={isLoading}
              className="flex-1 px-4 py-2 rounded-lg border border-neutral-light bg-white text-foreground placeholder-neutral-dark focus:outline-none focus:ring-2 focus:ring-primary disabled:opacity-50"
            />
            <button
              type="submit"
              disabled={isLoading || !input.trim()}
              className="px-4 py-2 bg-primary text-white rounded-lg hover:bg-opacity-90 disabled:opacity-50 disabled:cursor-not-allowed transition-opacity flex items-center gap-2"
            >
              <Send className="w-4 h-4" />
            </button>
          </div>
        </form>
      </div>
    </div>
  )
}
