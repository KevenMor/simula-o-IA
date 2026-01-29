import { useState, useRef, useEffect } from 'react'
import { Send, ArrowLeft, Phone, Video, MoreVertical } from 'lucide-react'
import { Link } from 'react-router-dom'
import { askQuestion } from '../services/api'

interface Message {
  role: 'user' | 'assistant'
  content: string
  timestamp?: Date
}

const TENANT_ID = 'hotel_creche_pet'

export default function WhatsAppChatPage() {
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [loading, setLoading] = useState(false)
  const messagesEndRef = useRef<HTMLDivElement>(null)
  const inputRef = useRef<HTMLInputElement>(null)

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' })
  }

  useEffect(() => {
    scrollToBottom()
  }, [messages])

  const handleSend = async () => {
    if (!input.trim() || loading) return

    const userMessage: Message = { role: 'user', content: input.trim(), timestamp: new Date() }
    setMessages((prev) => [...prev, userMessage])
    setInput('')
    setLoading(true)

    try {
      const history = messages.map((m) => ({ role: m.role, content: m.content }))
      const response = await askQuestion(input.trim(), TENANT_ID, history)
      const assistantMessage: Message = {
        role: 'assistant',
        content: response.answer,
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, assistantMessage])
    } catch (error: any) {
      console.error('Erro ao enviar mensagem:', error)
      const errorMessage: Message = {
        role: 'assistant',
        content:
          error?.response?.data?.detail ||
          error?.message ||
          'Desculpe, ocorreu um erro. Tente novamente em instantes.',
        timestamp: new Date(),
      }
      setMessages((prev) => [...prev, errorMessage])
    } finally {
      setLoading(false)
    }
  }

  const formatTime = (d: Date) => {
    return d.toLocaleTimeString('pt-BR', { hour: '2-digit', minute: '2-digit' })
  }

  return (
    <div className="h-screen flex flex-col bg-[#0b141a]">
      {/* Header WhatsApp */}
      <header className="flex items-center justify-between px-4 py-3 bg-[#075E54] text-white shrink-0">
        <div className="flex items-center gap-3">
          <Link
            to="/chat"
            className="p-1.5 rounded-full hover:bg-white/10 transition-colors"
            title="Voltar ao painel"
          >
            <ArrowLeft size={22} />
          </Link>
          <div className="w-10 h-10 rounded-full bg-[#25D366] flex items-center justify-center text-lg font-bold">
            🐕
          </div>
          <div>
            <h1 className="font-semibold text-base">(nome da empresa)</h1>
            <p className="text-xs text-white/80">Tia Bia • online</p>
          </div>
        </div>
        <div className="flex items-center gap-1">
          <button className="p-2 rounded-full hover:bg-white/10 transition-colors">
            <Video size={22} />
          </button>
          <button className="p-2 rounded-full hover:bg-white/10 transition-colors">
            <Phone size={22} />
          </button>
          <button className="p-2 rounded-full hover:bg-white/10 transition-colors">
            <MoreVertical size={22} />
          </button>
        </div>
      </header>

      {/* Background padrão WhatsApp */}
      <div
        className="flex-1 overflow-y-auto relative"
        style={{
          backgroundImage: `url("data:image/svg+xml,%3Csvg width='60' height='60' viewBox='0 0 60 60' xmlns='http://www.w3.org/2000/svg'%3E%3Cg fill='none' fill-rule='evenodd'%3E%3Cg fill='%231a1a1a' fill-opacity='0.03'%3E%3Cpath d='M36 34v-4h-2v4h-4v2h4v4h2v-4h4v-2h-4zm0-30V0h-2v4h-4v2h4v4h2V6h4V4h-4zM6 34v-4H4v4H0v2h4v4h2v-4h4v-2H6zM6 4V0H4v4H0v2h4v4h2V6h4V4H6z'/%3E%3C/g%3E%3C/g%3E%3C/svg%3E")`,
          backgroundColor: '#0b141a',
        }}
      >
        <div className="min-h-full px-4 py-6 max-w-2xl mx-auto">
          {messages.length === 0 && (
            <div className="flex flex-col items-center justify-center py-16 text-center">
              <div className="w-20 h-20 rounded-full bg-[#075E54]/20 flex items-center justify-center text-4xl mb-4">
                🐕
              </div>
              <p className="text-[#8696a0] text-sm max-w-[280px]">
                Converse com a Tia Bia do (nome da empresa). Tire dúvidas sobre hospedagem, creche e
                agendamentos.
              </p>
              <p className="text-[#667781] text-xs mt-2">Simulação de atendimento (desktop)</p>
            </div>
          )}

          {messages.map((msg, idx) => (
            <div
              key={idx}
              className={`flex mb-1 ${msg.role === 'user' ? 'justify-end' : 'justify-start'}`}
            >
              <div
                className={`max-w-[85%] sm:max-w-[75%] rounded-lg px-3 py-2 shadow-sm ${
                  msg.role === 'user'
                    ? 'bg-[#005c4b] text-white rounded-tr-none'
                    : 'bg-[#202c33] text-[#e9edef] rounded-tl-none'
                }`}
              >
                <p className="whitespace-pre-wrap text-[15px] leading-relaxed">{msg.content}</p>
                <span
                  className={`text-[11px] mt-0.5 block ${
                    msg.role === 'user' ? 'text-white/70' : 'text-[#8696a0]'
                  }`}
                >
                  {msg.timestamp ? formatTime(msg.timestamp) : ''}
                </span>
              </div>
            </div>
          ))}

          {loading && (
            <div className="flex justify-start mb-1">
              <div className="bg-[#202c33] text-[#e9edef] rounded-lg rounded-tl-none px-4 py-2 shadow-sm">
                <span className="inline-flex gap-1">
                  <span className="w-2 h-2 bg-[#8696a0] rounded-full animate-bounce [animation-delay:-0.3s]" />
                  <span className="w-2 h-2 bg-[#8696a0] rounded-full animate-bounce [animation-delay:-0.15s]" />
                  <span className="w-2 h-2 bg-[#8696a0] rounded-full animate-bounce" />
                </span>
              </div>
            </div>
          )}
          <div ref={messagesEndRef} />
        </div>
      </div>

      {/* Input área */}
      <div className="shrink-0 bg-[#202c33] px-4 py-3 flex items-end gap-2">
        <div className="flex-1 flex items-center gap-2 bg-[#2a3942] rounded-lg px-3 py-2 min-h-[42px]">
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault()
                handleSend()
              }
            }}
            placeholder="Digite uma mensagem"
            className="flex-1 bg-transparent text-[#e9edef] placeholder-[#8696a0] text-[15px] outline-none"
          />
        </div>
        <button
          onClick={handleSend}
          disabled={loading || !input.trim()}
          className="p-2.5 rounded-full bg-[#00a884] text-white hover:bg-[#06cf9c] disabled:opacity-50 disabled:cursor-not-allowed disabled:hover:bg-[#00a884] transition-colors"
          title="Enviar"
        >
          <Send size={22} strokeWidth={2.5} />
        </button>
      </div>
    </div>
  )
}
