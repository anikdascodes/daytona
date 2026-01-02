import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import { useConfigStore } from './store/configStore'
import ConfigurationPage from './pages/ConfigurationPage'
import HealthCheckPage from './pages/HealthCheckPage'
import ChatPage from './pages/ChatPage'

function App() {
  const { isConfigured } = useConfigStore()

  return (
    <BrowserRouter>
      <div className="min-h-screen bg-gray-50">
        <Routes>
          <Route path="/" element={<ConfigurationPage />} />
          <Route path="/health" element={<HealthCheckPage />} />
          <Route
            path="/chat"
            element={isConfigured ? <ChatPage /> : <Navigate to="/" replace />}
          />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </div>
    </BrowserRouter>
  )
}

export default App
