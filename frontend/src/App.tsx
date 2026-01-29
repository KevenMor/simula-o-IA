import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Layout from './components/Layout'
import ChatPage from './pages/ChatPage'
import WhatsAppChatPage from './pages/WhatsAppChatPage'
import TrainingPage from './pages/TrainingPage'
import SettingsPage from './pages/SettingsPage'
import DashboardPage from './pages/DashboardPage'

function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/chat" replace />} />
          <Route path="chat" element={<ChatPage />} />
          <Route path="training" element={<TrainingPage />} />
          <Route path="settings" element={<SettingsPage />} />
          <Route path="dashboard" element={<DashboardPage />} />
        </Route>
        {/* Chat estilo WhatsApp - página standalone para demo (hotel/creche pet) */}
        <Route path="/chat-whatsapp" element={<WhatsAppChatPage />} />
      </Routes>
    </BrowserRouter>
  )
}

export default App
