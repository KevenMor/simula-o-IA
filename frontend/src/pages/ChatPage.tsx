import { useState } from 'react'
import { Send, User, Bot } from 'lucide-react'
import { askQuestion } from '../services/api'

interface Message {
  role: 'user' | 'assistant'
  content: string
}

export default function ChatPage() {
  const [tenantId, setTenantId] = useState('autoescola_ideal')
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)

  const handleSend = async () => {
    if (!input.trim() || loading) return

    const userMessage: Message = { role: 'user', content: input }
    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      const response = await askQuestion(input, tenantId, messages)
      const assistantMessage: Message = {
        role: 'assistant',
        content: response.answer,
      }
      setMessages((prev) => [...prev, assistantMessage])
    } catch (error: any) {
      console.error('Erro ao fazer pergunta:', error)
      const errorMessage: Message = {
        role: 'assistant',
        content: error?.response?.data?.detail || error?.message || 'Desculpe, ocorreu um erro. Tente novamente.',
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="max-w-4xl mx-auto">
      <div className="mb-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Chat com IA</h1>
        <div className="flex items-center gap-4">
          <label className="text-sm text-gray-600">Cliente:</label>
          <input
            type="text"
            value={tenantId}
            onChange={(e) => setTenantId(e.target.value)}
            className="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
            placeholder="autoescola_ideal"
          />
        </div>
      </div>

      {/* Messages */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 h-[600px] flex flex-col">
        <div className="flex-1 overflow-y-auto p-6 space-y-4">
          {messages.length === 0 && (
            <div className="text-center text-gray-500 py-12">
              <Bot size={48} className="mx-auto mb-4 text-gray-400" />
              <p>Comece uma conversa enviando uma mensagem</p>
            </div>
          )}
          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex gap-3 ${
                msg.role === 'user' ? 'justify-end' : 'justify-start'
              }`}
            >
              {msg.role === 'assistant' && (
                <div className="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center flex-shrink-0">
                  <Bot size={18} className="text-primary-600" />
                </div>
              )}
              <div
                className={`max-w-[80%] rounded-lg px-4 py-2 ${
                  msg.role === 'user'
                    ? 'bg-primary-600 text-white'
                    : 'bg-gray-100 text-gray-900'
                }`}
              >
                <p className="whitespace-pre-wrap">{msg.content}</p>
              </div>
              {msg.role === 'user' && (
                <div className="w-8 h-8 rounded-full bg-gray-200 flex items-center justify-center flex-shrink-0">
                  <User size={18} className="text-gray-600" />
                </div>
              )}
            </div>
          ))}
          {loading && (
            <div className="flex gap-3 justify-start">
              <div className="w-8 h-8 rounded-full bg-primary-100 flex items-center justify-center">
                <Bot size={18} className="text-primary-600" />
              </div>
              <div className="bg-gray-100 rounded-lg px-4 py-2">
                <p className="text-gray-500">Pensando...</p>
              </div>
            </div>
          )}
        </div>

        {/* Input */}
        <div className="border-t border-gray-200 p-4">
          <div className="flex gap-2">
            <input
              type="text"
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyPress={(e) => e.key === 'Enter' && handleSend()}
              placeholder="Digite sua mensagem..."
              className="flex-1 px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
            />
            <button
              onClick={handleSend}
              disabled={loading || !input.trim()}
              className="px-6 py-2 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed flex items-center gap-2"
            >
              <Send size={20} />
              Enviar
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}
