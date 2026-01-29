import { BarChart3, MessageSquare, TrendingUp, AlertCircle } from 'lucide-react'

export default function DashboardPage() {
  return (
    <div>
      <div className="mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">Dashboard</h1>
        <p className="text-gray-600">Visão geral do sistema</p>
      </div>

      {/* Stats Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Total de Mensagens</p>
              <p className="text-3xl font-bold text-gray-900">1,234</p>
            </div>
            <MessageSquare className="text-primary-600" size={32} />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Taxa de Cache</p>
              <p className="text-3xl font-bold text-gray-900">68%</p>
            </div>
            <TrendingUp className="text-green-600" size={32} />
          </div>
        </div>

        <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
          <div className="flex items-center justify-between">
            <div>
              <p className="text-sm text-gray-600 mb-1">Revisões Humanas</p>
              <p className="text-3xl font-bold text-gray-900">12</p>
            </div>
            <AlertCircle className="text-yellow-600" size={32} />
          </div>
        </div>
      </div>

      {/* Placeholder for charts */}
      <div className="bg-white rounded-lg shadow-sm border border-gray-200 p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-4">Estatísticas</h2>
        <div className="text-center py-12 text-gray-500">
          <BarChart3 size={48} className="mx-auto mb-4 text-gray-400" />
          <p>Gráficos e métricas detalhadas em breve</p>
        </div>
      </div>
    </div>
  )
}
