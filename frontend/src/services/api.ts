import axios from 'axios'

// API URL: em prod (build Docker) usamos '' = mesma origem. Em dev, fallback localhost:8000.
// VITE_API_URL="" no build → mesmo origem; sem isso em dev → backend em :8000.
const _raw = import.meta.env.VITE_API_URL
const API_URL =
  _raw === '' ? '' : (_raw || (import.meta.env.DEV ? 'http://localhost:8000' : ''))
let API_KEY = import.meta.env.VITE_API_KEY || ''

// Se não encontrou, tentar carregar manualmente (fallback)
if (!API_KEY && import.meta.env.DEV) {
  console.warn('⚠️ VITE_API_KEY não encontrada em import.meta.env')
  console.warn('   Verifique se o arquivo .env existe e foi carregado')
  console.warn('   Reinicie o servidor do Vite após criar/editar o .env')
}

// Log para debug (sempre mostrar em dev)
if (import.meta.env.DEV) {
  console.log('🔧 Configuração da API:')
  console.log('  API_URL:', API_URL)
  console.log('  API_KEY:', API_KEY ? `${API_KEY.substring(0, 30)}... (${API_KEY.length} chars)` : '❌ NÃO CONFIGURADA')
  if (API_KEY) {
    console.log('  ✅ API_KEY carregada com sucesso')
  } else {
    console.error('  ❌ API_KEY NÃO FOI CARREGADA!')
    console.error('     Verifique o arquivo frontend/.env')
    console.error('     Reinicie o servidor do Vite (Ctrl+C e npm run dev)')
  }
}

const api = axios.create({
  baseURL: API_URL,
  headers: {
    'Content-Type': 'application/json',
  },
})

// Adicionar API key em cada requisição (para garantir que está sendo enviada)
api.interceptors.request.use(
  (config) => {
    if (API_KEY) {
      config.headers['X-API-Key'] = API_KEY.trim() // Remove espaços em branco
      if (import.meta.env.DEV) {
        console.log('🔑 Enviando API Key:', API_KEY.substring(0, 30) + '...')
      }
    } else if (import.meta.env.DEV) {
      console.error('❌ API_KEY não configurada! Verifique o arquivo .env')
    }
    return config
  },
  (error) => {
    return Promise.reject(error)
  }
)

// Interceptor para log de erros (só em dev para não poluir produção)
api.interceptors.response.use(
  (response) => response,
  (error) => {
    if (import.meta.env.DEV) {
      console.error('API Error:', {
        status: error.response?.status,
        data: error.response?.data,
        message: error.message,
        config: { url: error.config?.url, method: error.config?.method },
      })
    }
    return Promise.reject(error)
  }
)

// Settings API
export const getSettings = async (tenantId: string) => {
  const response = await api.get(`/api/v1/settings/${tenantId}`)
  return response.data
}

export const updateSettings = async (tenantId: string, settings: any) => {
  const response = await api.put(`/api/v1/settings/${tenantId}`, settings)
  return response.data
}

// QA API
export const askQuestion = async (question: string, tenantId?: string, history?: any[]) => {
  const response = await api.post('/api/v1/qa/ask', {
    question,
    tenant_id: tenantId,
    conversation_history: history || [],
  })
  return response.data
}

// Training API
export const getDocuments = async (tenantId: string) => {
  const response = await api.get(`/api/v1/training/documents?tenant_id=${tenantId}`)
  return response.data
}

export const saveDocument = async (data: any) => {
  const response = await api.post('/api/v1/training/documents', data)
  return response.data
}

export const deleteDocument = async (tenantId: string, docId: string) => {
  const response = await api.delete(`/api/v1/training/documents/${docId}?tenant_id=${tenantId}`)
  return response.data
}

export default api
