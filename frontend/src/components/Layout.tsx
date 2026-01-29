import { Outlet, Link, useLocation } from 'react-router-dom'
import { MessageSquare, BookOpen, Settings, BarChart3 } from 'lucide-react'

export default function Layout() {
  const location = useLocation()

  const navItems = [
    { path: '/chat', icon: MessageSquare, label: 'Chat' },
    { path: '/chat-whatsapp', icon: MessageSquare, label: 'Chat WhatsApp (demo)' },
    { path: '/training', icon: BookOpen, label: 'Treinamento' },
    { path: '/settings', icon: Settings, label: 'Configurações' },
    { path: '/dashboard', icon: BarChart3, label: 'Dashboard' },
  ]

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Sidebar */}
      <aside className="fixed left-0 top-0 h-full w-64 bg-white border-r border-gray-200 shadow-sm">
        <div className="p-6">
          <h1 className="text-2xl font-bold text-primary-600">AI Agent</h1>
          <p className="text-sm text-gray-500 mt-1">Plataforma de Atendimento</p>
        </div>
        
        <nav className="mt-8 px-4">
          {navItems.map((item) => {
            const Icon = item.icon
            const isActive = location.pathname === item.path
            return (
              <Link
                key={item.path}
                to={item.path}
                className={`flex items-center gap-3 px-4 py-3 rounded-lg mb-2 transition-colors ${
                  isActive
                    ? 'bg-primary-50 text-primary-700 font-medium'
                    : 'text-gray-700 hover:bg-gray-50'
                }`}
              >
                <Icon size={20} />
                <span>{item.label}</span>
              </Link>
            )
          })}
        </nav>
      </aside>

      {/* Main Content */}
      <main className="ml-64 p-8">
        <Outlet />
      </main>
    </div>
  )
}
