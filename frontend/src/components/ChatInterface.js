import React, { useState, useRef, useEffect } from 'react'
import axios from 'axios'
import {
  Send,
  Bot,
  User,
  Trash2,
  Brain,
  Sparkles,
  Zap,
  MessageCircle,
  Clock,
  Database,
  Copy,
  CheckCheck,
  Volume2,
  VolumeX,
} from 'lucide-react'
import { motion, AnimatePresence } from 'framer-motion'

const ChatInterface = () => {
  const [messages, setMessages] = useState([])
  const [inputMessage, setInputMessage] = useState('')
  const [isLoading, setIsLoading] = useState(false)
  const [sessionId, setSessionId] = useState(null)
  const [isTyping, setIsTyping] = useState(false)
  const [conversationCount, setConversationCount] = useState(0)
  const [copiedMessageId, setCopiedMessageId] = useState(null)
  const [soundEnabled, setSoundEnabled] = useState(true)
  const messagesEndRef = useRef(null)

  // Replace the API_BASE line with:
  const API_BASE =
    process.env.REACT_APP_API_URL ||
    'ai-chat-memory-image-ai.up.railway.app'

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const playSound = (type) => {
    if (!soundEnabled) return

    // Simple beep sounds (you can replace with actual audio files)
    const audioContext = new (window.AudioContext ||
      window.webkitAudioContext)()
    const oscillator = audioContext.createOscillator()
    const gainNode = audioContext.createGain()

    oscillator.connect(gainNode)
    gainNode.connect(audioContext.destination)

    if (type === 'send') {
      oscillator.frequency.setValueAtTime(800, audioContext.currentTime)
    } else {
      oscillator.frequency.setValueAtTime(600, audioContext.currentTime)
    }

    gainNode.gain.setValueAtTime(0.1, audioContext.currentTime)
    gainNode.gain.exponentialRampToValueAtTime(
      0.01,
      audioContext.currentTime + 0.5
    )

    oscillator.start(audioContext.currentTime)
    oscillator.stop(audioContext.currentTime + 0.5)
  }

  const copyToClipboard = async (text, messageId) => {
    try {
      await navigator.clipboard.writeText(text)
      setCopiedMessageId(messageId)
      setTimeout(() => setCopiedMessageId(null), 2000)
    } catch (err) {
      console.error('Failed to copy text: ', err)
    }
  }

 const sendMessage = async (e) => {
  e.preventDefault();
  if (!inputMessage.trim() || isLoading) return;

  const userMessage = inputMessage.trim();
  setInputMessage('');

  // Add user message with animation
  const userMessageId = Date.now() + '-user';
  setMessages((prev) => [
    ...prev,
    {
      id: userMessageId,
      type: 'user',
      content: userMessage,
      timestamp: new Date(),
    },
  ]);

  playSound('send');
  setIsLoading(true);
  setIsTyping(true);

  try {
    console.log('Sending to:', `${API_BASE}/chat`);
    
    const response = await axios.post(
      `${API_BASE}/chat`,
      {
        message: userMessage,
        session_id: sessionId,
      },
      {
        timeout: 10000, // 10 second timeout
        headers: {
          'Content-Type': 'application/json',
        },
      }
    );

    console.log('Response received:', response.data);

    const {
      response: aiResponse,
      session_id,
      conversation_count,
    } = response.data;

    if (session_id && !sessionId) {
      setSessionId(session_id);
    }

    if (conversation_count) {
      setConversationCount(conversation_count);
    }

    // Simulate typing delay for better UX
    setTimeout(() => {
      const aiMessageId = Date.now() + '-ai';
      setMessages((prev) => [
        ...prev,
        {
          id: aiMessageId,
          type: 'assistant',
          content: aiResponse,
          timestamp: new Date(),
        },
      ]);
      playSound('receive');
      setIsLoading(false);
      setIsTyping(false);
    }, 1500 + Math.random() * 1000);
  } catch (error) {
    console.error('Error sending message:', error);
    
    let errorMessage = 'Sorry, I encountered an error. Please try again.';
    
    if (error.response?.status === 502) {
      errorMessage = 'Server is temporarily unavailable. The backend might be restarting. Please try again in 30 seconds.';
    } else if (error.code === 'ECONNABORTED') {
      errorMessage = 'Request timeout. Please check your connection and try again.';
    } else if (error.response?.status >= 500) {
      errorMessage = 'Server error. Please try again later.';
    }
    
    const errorMessageId = Date.now() + '-error';
    setMessages((prev) => [
      ...prev,
      {
        id: errorMessageId,
        type: 'assistant',
        content: errorMessage,
        isError: true,
        timestamp: new Date(),
      },
    ]);
    setIsLoading(false);
    setIsTyping(false);
  }
};

    playSound('send')
    setIsLoading(true)
    setIsTyping(true)

    try {
      const response = await axios.post(`${API_BASE}/chat`, {
        message: userMessage,
        session_id: sessionId,
      })

      const {
        response: aiResponse,
        session_id,
        conversation_count,
      } = response.data

      if (session_id && !sessionId) {
        setSessionId(session_id)
      }

      if (conversation_count) {
        setConversationCount(conversation_count)
      }

      // Simulate typing delay for better UX
      setTimeout(() => {
        const aiMessageId = Date.now() + '-ai'
        setMessages((prev) => [
          ...prev,
          {
            id: aiMessageId,
            type: 'assistant',
            content: aiResponse,
            timestamp: new Date(),
          },
        ])
        playSound('receive')
        setIsLoading(false)
        setIsTyping(false)
      }, 1500 + Math.random() * 1000)
    } catch (error) {
      console.error('Error sending message:', error)
      const errorMessageId = Date.now() + '-error'
      setMessages((prev) => [
        ...prev,
        {
          id: errorMessageId,
          type: 'assistant',
          content: 'Sorry, I encountered an error. Please try again.',
          isError: true,
        },
      ])
      setIsLoading(false)
      setIsTyping(false)
    }
  }

  const clearChat = () => {
    setMessages([])
    setSessionId(null)
    setConversationCount(0)
  }

 const formatTime = (date) => {
  if (!date) return 'Just now'
  
  // Handle both Date objects and string timestamps
  const dateObj = date instanceof Date ? date : new Date(date)
  
  // Check if date is valid
  if (isNaN(dateObj.getTime())) {
    return 'Just now'
  }
  
  return dateObj.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })
}

  return (
    <div className='min-h-screen bg-gradient-to-br from-purple-900 via-blue-900 to-indigo-900 p-4'>
      <div className='max-w-6xl mx-auto h-[95vh] flex flex-col'>
        {/* Header */}
        <motion.div
          initial={{ opacity: 0, y: -20 }}
          animate={{ opacity: 1, y: 0 }}
          className='glass rounded-2xl p-6 mb-6'
        >
          <div className='flex items-center justify-between'>
            <div className='flex items-center space-x-4'>
              <motion.div
                className='relative'
                animate={{ rotate: [0, 10, -10, 0] }}
                transition={{ duration: 2, repeat: Infinity, repeatDelay: 5 }}
              >
                <div className='p-3 bg-gradient-to-r from-purple-500 to-pink-500 rounded-2xl shadow-lg pulse-ai'>
                  <Brain className='h-8 w-8 text-white' />
                </div>
                <motion.div
                  className='absolute -top-1 -right-1 w-4 h-4 bg-green-400 rounded-full border-2 border-white'
                  animate={{ scale: [1, 1.2, 1] }}
                  transition={{ duration: 2, repeat: Infinity }}
                />
              </motion.div>

              <div>
                <h1 className='text-3xl font-bold text-white glow-text'>
                  AI Memory Chat
                </h1>
                <p className='text-purple-200 flex items-center space-x-2 mt-1'>
                  <Sparkles className='h-4 w-4' />
                  <span>Powered by Gemini AI • Remembers everything!</span>
                </p>
              </div>
            </div>

            <div className='flex items-center space-x-3'>
              {/* Stats */}
              <div className='flex items-center space-x-4 text-sm'>
                <div className='glass-dark rounded-lg px-3 py-2'>
                  <div className='flex items-center space-x-2 text-green-300'>
                    <Database className='h-4 w-4' />
                    <span>{conversationCount} memories</span>
                  </div>
                </div>
                <div className='glass-dark rounded-lg px-3 py-2'>
                  <div className='flex items-center space-x-2 text-blue-300'>
                    <MessageCircle className='h-4 w-4' />
                    <span>
                      {messages.filter((m) => m.type === 'user').length}{' '}
                      messages
                    </span>
                  </div>
                </div>
              </div>

              {/* Control Buttons */}
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setSoundEnabled(!soundEnabled)}
                className='p-2 glass-dark rounded-xl text-white hover:bg-white/20 transition-all'
                title={soundEnabled ? 'Mute sounds' : 'Enable sounds'}
              >
                {soundEnabled ? (
                  <Volume2 className='h-5 w-5' />
                ) : (
                  <VolumeX className='h-5 w-5' />
                )}
              </motion.button>

              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={clearChat}
                className='p-2 glass-dark rounded-xl text-white hover:bg-red-500/20 transition-all group'
                title='Clear chat'
              >
                <Trash2 className='h-5 w-5 group-hover:text-red-400 transition-colors' />
              </motion.button>
            </div>
          </div>
        </motion.div>

        {/* Main Chat Area */}
        <div className='flex-1 flex rounded-2xl overflow-hidden shadow-2xl'>
          {/* Sidebar */}
          <motion.div
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
            className='w-80 glass hidden lg:block p-6'
          >
            <div className='space-y-6'>
              <div>
                <h3 className='text-white font-semibold mb-3 flex items-center space-x-2'>
                  <Zap className='h-4 w-4 text-yellow-400' />
                  <span>AI Capabilities</span>
                </h3>
                <div className='space-y-2'>
                  {[
                    'Context Memory',
                    'Learning',
                    '24/7 Available',
                    'Multi-turn Conversations',
                  ].map((feature, index) => (
                    <motion.div
                      key={feature}
                      initial={{ opacity: 0, x: -10 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className='flex items-center space-x-2 text-sm text-purple-200'
                    >
                      <div className='w-2 h-2 bg-green-400 rounded-full'></div>
                      <span>{feature}</span>
                    </motion.div>
                  ))}
                </div>
              </div>

              <div className='pt-4 border-t border-white/20'>
                <h3 className='text-white font-semibold mb-3 flex items-center space-x-2'>
                  <Clock className='h-4 w-4 text-blue-400' />
                  <span>Quick Prompts</span>
                </h3>
                <div className='space-y-2'>
                  {[
                    'Tell me about yourself',
                    'What can you remember?',
                    'Explain how memory works',
                    'Help me with a problem',
                  ].map((prompt, index) => (
                    <motion.button
                      key={prompt}
                      whileHover={{ scale: 1.02 }}
                      whileTap={{ scale: 0.98 }}
                      onClick={() => setInputMessage(prompt)}
                      className='w-full text-left p-3 rounded-xl glass-dark text-sm text-purple-200 hover:bg-white/10 transition-all'
                    >
                      {prompt}
                    </motion.button>
                  ))}
                </div>
              </div>
            </div>
          </motion.div>

          {/* Chat Messages */}
          <div className='flex-1 flex flex-col'>
            <div className='flex-1 overflow-y-auto p-6 bg-white/5 backdrop-blur-sm'>
              <AnimatePresence>
                {messages.length === 0 && (
                  <motion.div
                    initial={{ opacity: 0, scale: 0.9 }}
                    animate={{ opacity: 1, scale: 1 }}
                    exit={{ opacity: 0, scale: 0.9 }}
                    className='text-center py-16'
                  >
                    <motion.div
                      animate={{ y: [0, -10, 0] }}
                      transition={{ duration: 3, repeat: Infinity }}
                      className='mb-6'
                    >
                      <div className='w-20 h-20 mx-auto bg-gradient-to-r from-purple-500 to-pink-500 rounded-3xl flex items-center justify-center shadow-2xl'>
                        <Brain className='h-10 w-10 text-white' />
                      </div>
                    </motion.div>
                    <h3 className='text-2xl font-bold text-white mb-4'>
                      Welcome to AI Memory Chat! 🧠
                    </h3>
                    <p className='text-purple-200 max-w-md mx-auto leading-relaxed'>
                      I'm your AI assistant with long-term memory. I'll remember
                      our conversations and use that context to provide better,
                      more personalized responses.
                    </p>
                    <div className='grid grid-cols-1 md:grid-cols-2 gap-4 mt-8 max-w-lg mx-auto'>
                      {[
                        {
                          icon: '💭',
                          title: 'Context Memory',
                          desc: 'Remembers previous conversations',
                        },
                        {
                          icon: '🚀',
                          title: 'Fast Responses',
                          desc: 'Powered by Gemini AI',
                        },
                        {
                          icon: '🔍',
                          title: 'Smart Search',
                          desc: 'Finds relevant past discussions',
                        },
                        {
                          icon: '🔄',
                          title: 'Continuous Learning',
                          desc: 'Improves with each interaction',
                        },
                      ].map((feature, index) => (
                        <motion.div
                          key={feature.title}
                          initial={{ opacity: 0, y: 20 }}
                          animate={{ opacity: 1, y: 0 }}
                          transition={{ delay: index * 0.1 + 0.5 }}
                          className='p-4 glass-dark rounded-xl text-center'
                        >
                          <div className='text-2xl mb-2'>{feature.icon}</div>
                          <div className='text-white font-semibold text-sm'>
                            {feature.title}
                          </div>
                          <div className='text-purple-300 text-xs mt-1'>
                            {feature.desc}
                          </div>
                        </motion.div>
                      ))}
                    </div>
                  </motion.div>
                )}

{messages.map((message, index) => (
  <motion.div
    key={message.id}
    initial={{ opacity: 0, y: 20, scale: 0.95 }}
    animate={{ opacity: 1, y: 0, scale: 1 }}
    transition={{ duration: 0.3, delay: index * 0.1 }}
    className={`flex ${
      message.type === 'user' ? 'justify-end' : 'justify-start'
    } mb-6`}
  >
    <div
      className={`flex max-w-[85%] ${
        message.type === 'user'
          ? 'bg-gradient-to-r from-blue-500 to-blue-600 text-white'
          : 'bg-white/10 backdrop-blur-sm text-white border border-white/20'
      } rounded-2xl p-4 shadow-lg hover:shadow-xl transition-all duration-300`}
    >
      <div className='flex items-start space-x-3'>
        {message.type === 'assistant' && (
          <motion.div
            whileHover={{ scale: 1.1 }}
            className='flex-shrink-0 w-10 h-10 bg-gradient-to-r from-purple-500 to-pink-500 rounded-full flex items-center justify-center shadow-lg'
          >
            <Bot className='h-5 w-5 text-white' />
          </motion.div>
        )}

        <div className='flex-1 min-w-0'>
          <div className='flex items-center space-x-3 mb-2'>
            <span className='font-semibold text-sm'>
              {message.type === 'user' ? 'You' : 'AI Assistant'}
            </span>
            <span
              className={`text-xs ${
                message.type === 'user'
                  ? 'text-blue-100'
                  : 'text-purple-300'
              }`}
            >
              {formatTime(message.timestamp)}
            </span>
          </div>
          <p className='text-sm leading-relaxed whitespace-pre-wrap'>
            {message.content}
          </p>
        </div>

        {message.type === 'user' && (
          <motion.div
            whileHover={{ scale: 1.1 }}
            className='flex-shrink-0 w-10 h-10 bg-gradient-to-r from-blue-400 to-blue-500 rounded-full flex items-center justify-center shadow-lg'
          >
            <User className='h-5 w-5 text-white' />
          </motion.div>
        )}
      </div>

      {/* Copy Button */}
      <motion.button
        whileHover={{ scale: 1.1 }}
        whileTap={{ scale: 0.9 }}
        onClick={() =>
          copyToClipboard(message.content, message.id)
        }
        className='ml-3 opacity-0 group-hover:opacity-100 transition-opacity p-1 rounded-lg hover:bg-white/20'
        title='Copy message'
      >
        {copiedMessageId === message.id ? (
          <CheckCheck className='h-4 w-4 text-green-400' />
        ) : (
          <Copy className='h-4 w-4 text-current' />
        )}
      </motion.button>
    </div>
  </motion.div>
))}

              <div ref={messagesEndRef} />
            </div>

            {/* Input Area */}
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className='border-t border-white/20 bg-white/5 backdrop-blur-sm p-6'
            >
              <form onSubmit={sendMessage} className='flex space-x-4'>
                <div className='flex-1 relative'>
                  <input
                    type='text'
                    value={inputMessage}
                    onChange={(e) => setInputMessage(e.target.value)}
                    placeholder="Ask me anything... I'll remember our conversation! 🌟"
                    className='w-full px-6 py-4 bg-white/10 border border-white/20 rounded-2xl text-white placeholder-purple-300 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:border-transparent transition-all duration-200 backdrop-blur-sm'
                    disabled={isLoading}
                  />
                  {sessionId && (
                    <div className='absolute -top-6 left-0 text-xs text-purple-300'>
                      Session: {sessionId.slice(0, 8)}... • Memory Active
                    </div>
                  )}
                </div>
                <motion.button
                  type='submit'
                  disabled={isLoading || !inputMessage.trim()}
                  whileHover={{ scale: 1.05 }}
                  whileTap={{ scale: 0.95 }}
                  className='px-8 py-4 bg-gradient-to-r from-purple-500 to-pink-500 text-white rounded-2xl hover:from-purple-600 hover:to-pink-600 focus:outline-none focus:ring-2 focus:ring-purple-500 focus:ring-offset-2 disabled:opacity-50 disabled:cursor-not-allowed transition-all duration-200 flex items-center space-x-2 shadow-lg hover:shadow-xl'
                >
                  <Send className='h-5 w-5' />
                  <span className='font-semibold'>Send</span>
                </motion.button>
              </form>
            </motion.div>
          </div>
        </div>
      </div>
    </div>
  )
}

export default ChatInterface
