import { useState, useEffect } from 'react'
import { Save, AlertCircle } from 'lucide-react'
import { getSettings, updateSettings } from '../services/api'

interface Settings {
  tenant_id: string
  confidence_threshold: number
  enable_hallucination_check: boolean
  temperature: number
  max_tokens: number
  response_style: string
  auto_ask_name: boolean
  cache_enabled: boolean
  cache_ttl_seconds: number
}

export default function SettingsPage() {
  const [tenantId, setTenantId] = useState('autoescola_ideal')
  const [settings, setSettings] = useState<Settings | null>(null)
  const [loading, setLoading] = useState(false)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)

  useEffect(() => {
    loadSettings()
  }, [tenantId])

  const loadSettings = async () => {
    setLoading(true)
    try {
      const data = await getSettings(tenantId)
      setSettings(data)
    } catch (error) {
      setMessage({ type: 'error', text: 'Erro ao carregar configurações' })
    } finally {
      setLoading(false)
    }
  }

  const handleSave = async () => {
    if (!settings) return

    setSaving(true)
    setMessage(null)
    try {
      await updateSettings(tenantId, settings)
      setMessage({ type: 'success', text: 'Configurações salvas com sucesso!' })
    } catch (error) {
      setMessage({ type: 'error', text: 'Erro ao salvar configurações' })
    } finally {
      setSaving(false)
    }
  }

  if (loading || !settings) {
    return <div className="text-center py-12">Carregando...</div>
  }

  return (
    <div className="max-w-4xl">
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Configurações</h1>
        <p className="text-gray-600">Configure o comportamento do agente de IA</p>
      </div>

      {/* Tenant ID */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          ID do Cliente (Tenant)
        </label>
        <input
          type="text"
          value={tenantId}
          onChange={(e) => setTenantId(e.target.value)}
          className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500 focus:border-transparent"
          placeholder="autoescola_ideal"
        />
      </div>

      {message && (
        <div
          className={`mb-6 p-4 rounded-lg flex items-center gap-2 ${
            message.type === 'success'
              ? 'bg-green-50 text-green-800 border border-green-200'
              : 'bg-red-50 text-red-800 border border-red-200'
          }`}
        >
          <AlertCircle size={20} />
          <span>{message.text}</span>
        </div>
      )}

      {/* Anti-Hallucination Settings */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">
          Proteção Anti-Alucinações
        </h2>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Ativar Verificação de Alucinações
            </label>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={settings.enable_hallucination_check}
                onChange={(e) =>
                  setSettings({ ...settings, enable_hallucination_check: e.target.checked })
                }
                className="w-4 h-4 text-primary-600 rounded focus:ring-primary-500"
              />
              <span className="text-sm text-gray-600">
                Valida respostas para evitar informações inventadas
              </span>
            </label>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Threshold de Confiança: {settings.confidence_threshold.toFixed(2)}
            </label>
            <input
              type="range"
              min="0"
              max="1"
              step="0.05"
              value={settings.confidence_threshold}
              onChange={(e) =>
                setSettings({ ...settings, confidence_threshold: parseFloat(e.target.value) })
              }
              className="w-full"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>Menos rigoroso (0.0)</span>
              <span>Mais rigoroso (1.0)</span>
            </div>
            <p className="text-xs text-gray-500 mt-2">
              Respostas com confiança abaixo deste valor serão direcionadas para humano
            </p>
          </div>
        </div>
      </div>

      {/* LLM Settings */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Configurações do Modelo</h2>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Temperatura: {settings.temperature.toFixed(2)}
            </label>
            <input
              type="range"
              min="0"
              max="2"
              step="0.1"
              value={settings.temperature}
              onChange={(e) =>
                setSettings({ ...settings, temperature: parseFloat(e.target.value) })
              }
              className="w-full"
            />
            <div className="flex justify-between text-xs text-gray-500 mt-1">
              <span>Mais preciso (0.0)</span>
              <span>Mais criativo (2.0)</span>
            </div>
            <p className="text-xs text-gray-500 mt-2">
              Valores menores reduzem alucinações, mas tornam respostas mais previsíveis
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Máximo de Tokens por Resposta
            </label>
            <input
              type="number"
              min="50"
              max="4000"
              value={settings.max_tokens}
              onChange={(e) =>
                setSettings({ ...settings, max_tokens: parseInt(e.target.value) })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
            />
          </div>
        </div>
      </div>

      {/* Response Settings */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Estilo de Resposta</h2>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Estilo
            </label>
            <select
              value={settings.response_style}
              onChange={(e) =>
                setSettings({ ...settings, response_style: e.target.value })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
            >
              <option value="friendly">Amigável</option>
              <option value="formal">Formal</option>
              <option value="casual">Casual</option>
            </select>
          </div>

          <div>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={settings.auto_ask_name}
                onChange={(e) =>
                  setSettings({ ...settings, auto_ask_name: e.target.checked })
                }
                className="w-4 h-4 text-primary-600 rounded focus:ring-primary-500"
              />
              <span className="text-sm font-medium text-gray-700">
                Perguntar nome do cliente automaticamente
              </span>
            </label>
          </div>
        </div>
      </div>

      {/* Cache Settings */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6 mb-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Cache</h2>
        
        <div className="space-y-4">
          <div>
            <label className="flex items-center gap-2 cursor-pointer">
              <input
                type="checkbox"
                checked={settings.cache_enabled}
                onChange={(e) =>
                  setSettings({ ...settings, cache_enabled: e.target.checked })
                }
                className="w-4 h-4 text-primary-600 rounded focus:ring-primary-500"
              />
              <span className="text-sm font-medium text-gray-700">
                Ativar cache de respostas
              </span>
            </label>
            <p className="text-xs text-gray-500 mt-1 ml-6">
              Respostas similares são reutilizadas, reduzindo custos de tokens
            </p>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              TTL do Cache (segundos)
            </label>
            <input
              type="number"
              min="60"
              max="3600"
              value={settings.cache_ttl_seconds}
              onChange={(e) =>
                setSettings({ ...settings, cache_ttl_seconds: parseInt(e.target.value) })
              }
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-primary-500"
            />
          </div>
        </div>
      </div>

      {/* Save Button */}
      <div className="flex justify-end">
        <button
          onClick={handleSave}
          disabled={saving}
          className="flex items-center gap-2 px-6 py-3 bg-primary-600 text-white rounded-lg hover:bg-primary-700 disabled:opacity-50 disabled:cursor-not-allowed transition-colors"
        >
          <Save size={20} />
          {saving ? 'Salvando...' : 'Salvar Configurações'}
        </button>
      </div>
    </div>
  )
}
