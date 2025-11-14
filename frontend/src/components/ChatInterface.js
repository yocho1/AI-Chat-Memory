import React, { useState, useRef, useEffect } from 'react'
import axios from 'axios'

const ChatInterface = () => {
  const [messages, setMessages] = useState([])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [sessionId, setSessionId] = useState(null)
  const [isTyping, setIsTyping] = useState(false)
  const messagesEndRef = useRef(null)

  const API_BASE = 'https://ai-chat-memory-image-ai.up.railway.app/api'

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const sendMessage = async (e) => {
    e.preventDefault()
    if (!inputMessage.trim() || isLoading) return

    const userMessage = inputMessage.trim()
    setInputMessage('')

    // Add user message with timestamp
    const userMessageObj = {
      type: 'user',
      content: userMessage,
      timestamp: new Date().toLocaleTimeString(),
    }

    setMessages((prev) => [...prev, userMessageObj])
    setIsLoading(true)
    setIsTyping(true)

    try {
      console.log('Sending to:', `${API_BASE}/chat`)

      const response = await axios.post(
        `${API_BASE}/chat`,
        {
          message: userMessage,
          session_id: sessionId,
        },
        {
          timeout: 30000, // 30 second timeout
        }
      )

      console.log('Response received:', response.data)

      const { response: aiResponse, session_id } = response.data

      if (session_id && !sessionId) {
        setSessionId(session_id)
      }

      // Simulate typing delay
      setTimeout(() => {
        const aiMessageObj = {
          type: 'assistant',
          content: aiResponse,
          timestamp: new Date().toLocaleTimeString(),
        }

        setMessages((prev) => [...prev, aiMessageObj])
        setIsLoading(false)
        setIsTyping(false)
      }, 1000)
    } catch (error) {
      console.error('Error sending message:', error)

      let errorMessage = 'Sorry, I encountered an error. Please try again.'

      if (
        error.code === 'NETWORK_ERROR' ||
        error.message.includes('Network Error')
      ) {
        errorMessage =
          'Network error: Cannot connect to the server. Please check your connection.'
      } else if (error.response?.status === 502) {
        errorMessage =
          'Server is temporarily unavailable. Please try again in a moment.'
      } else if (error.response?.status === 403) {
        errorMessage = 'CORS error: Please check server configuration.'
      }

      const errorMessageObj = {
        type: 'assistant',
        content: errorMessage,
        timestamp: new Date().toLocaleTimeString(),
        isError: true,
      }

      setMessages((prev) => [...prev, errorMessageObj])
      setIsLoading(false)
      setIsTyping(false)
    }
  }

  const clearChat = () => {
    setMessages([])
    setSessionId(null)
  }

  return (
    <div className='min-h-screen bg-gray-100 p-4'>
      <div className='max-w-4xl mx-auto bg-white rounded-lg shadow-lg h-[90vh] flex flex-col'>
        {/* Header */}
        <div className='bg-blue-600 text-white p-4 rounded-t-lg'>
          <div className='flex justify-between items-center'>
            <h1 className='text-2xl font-bold'>AI Chat with Memory</h1>
            <button
              onClick={clearChat}
              className='bg-red-500 hover:bg-red-600 px-3 py-1 rounded text-sm'
            >
              Clear Chat
            </button>
          </div>
          <p className='text-blue-200 text-sm'>Backend: {API_BASE}</p>
        </div>

        {/* Messages */}
        <div className='flex-1 overflow-y-auto p-4 space-y-4'>
          {messages.length === 0 && (
            <div className='text-center text-gray-500 py-8'>
              <p className='text-lg'>
                Start a conversation with the AI assistant!
              </p>
              <p className='text-sm mt-2'>
                The AI will remember our conversations
              </p>
            </div>
          )}

          {messages.map((message, index) => (
            <div
              key={index}
              className={`flex ${
                message.type === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              <div
                className={`max-w-[80%] rounded-lg p-3 ${
                  message.type === 'user'
                    ? 'bg-blue-500 text-white'
                    : message.isError
                    ? 'bg-red-100 text-red-800 border border-red-300'
                    : 'bg-gray-200 text-gray-800'
                }`}
              >
                <p className='whitespace-pre-wrap'>{message.content}</p>
                {message.timestamp && (
                  <p
                    className={`text-xs mt-1 ${
                      message.type === 'user'
                        ? 'text-blue-200'
                        : 'text-gray-500'
                    }`}
                  >
                    {message.timestamp}
                  </p>
                )}
              </div>
            </div>
          ))}

          {isTyping && (
            <div className='flex justify-start'>
              <div className='bg-gray-200 rounded-lg p-3'>
                <div className='flex space-x-1'>
                  <div className='h-2 w-2 bg-gray-500 rounded-full animate-bounce'></div>
                  <div
                    className='h-2 w-2 bg-gray-500 rounded-full animate-bounce'
                    style={{ animationDelay: '0.1s' }}
                  ></div>
                  <div
                    className='h-2 w-2 bg-gray-500 rounded-full animate-bounce'
                    style={{ animationDelay: '0.2s' }}
                  ></div>
                </div>
              </div>
            </div>
          )}

          <div ref={messagesEndRef} />
        </div>

        {/* Input */}
        <div className='border-t p-4'>
          <form onSubmit={sendMessage} className='flex space-x-2'>
            <input
              type='text'
              value={inputMessage}
              onChange={(e) => setInputMessage(e.target.value)}
              placeholder='Type your message...'
              className='flex-1 border rounded-lg px-3 py-2 focus:outline-none focus:ring-2 focus:ring-blue-500'
              disabled={isLoading}
            />
            <button
              type='submit'
              disabled={isLoading || !inputMessage.trim()}
              className='bg-blue-500 hover:bg-blue-600 text-white px-4 py-2 rounded-lg disabled:opacity-50 disabled:cursor-not-allowed transition-colors'
            >
              {isLoading ? 'Sending...' : 'Send'}
            </button>
          </form>
        </div>
      </div>
    </div>
  )
}

export default ChatInterface
