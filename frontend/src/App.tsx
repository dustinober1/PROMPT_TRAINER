import { useEffect, useState } from 'react'
import Navigation from './components/Navigation'
import PaperForm from './components/PaperForm'
import PapersList from './components/PapersList'
import RubricForm from './components/RubricForm'
import RubricsList from './components/RubricsList'
import { ToastContainer } from './components/Toast'
import { healthApi } from './services/api'

type ActiveTab = 'papers' | 'rubrics';

function App() {
  const [backendStatus, setBackendStatus] = useState<'checking' | 'connected' | 'error'>('checking')
  const [activeTab, setActiveTab] = useState<ActiveTab>('papers')
  const [toasts, setToasts] = useState<{ id: number; type: 'success' | 'error' | 'info'; message: string }[]>([])

  useEffect(() => {
    // Check backend health on mount
    healthApi.check()
      .then(() => setBackendStatus('connected'))
      .catch(() => setBackendStatus('error'))
  }, [])

  const handlePaperSubmitted = () => {
    window.dispatchEvent(new Event('paperSubmitted'))
  }

  const handleRubricCreated = () => {
    window.dispatchEvent(new Event('rubricCreated'))
  }

  const pushToast = (type: 'success' | 'error' | 'info', message: string) => {
    const id = Date.now() + Math.random()
    setToasts((prev) => [...prev, { id, type, message }])
  }

  const dismissToast = (id: number) => {
    setToasts((prev) => prev.filter((toast) => toast.id !== id))
  }

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />

      <main className="container mx-auto px-4 py-8">
        <ToastContainer toasts={toasts} onDismiss={dismissToast} />
        <div className="max-w-6xl mx-auto">
          {/* Backend Status Indicator */}
          <div className={`mb-6 px-4 py-2 rounded-lg flex items-center justify-between ${
            backendStatus === 'connected' ? 'bg-green-100 border border-green-300' :
            backendStatus === 'error' ? 'bg-red-100 border border-red-300' :
            'bg-yellow-100 border border-yellow-300'
          }`}>
            <span className="text-sm font-medium">
              Backend Status:
              {backendStatus === 'connected' && <span className="text-green-700 ml-2">✓ Connected</span>}
              {backendStatus === 'error' && <span className="text-red-700 ml-2">✗ Disconnected</span>}
              {backendStatus === 'checking' && <span className="text-yellow-700 ml-2">⟳ Checking...</span>}
            </span>
            <span className="text-xs text-gray-600">http://127.0.0.1:8000</span>
          </div>

          {/* Tab Navigation */}
          <div className="mb-6 border-b border-gray-200">
            <nav className="flex space-x-8">
              <button
                onClick={() => setActiveTab('papers')}
                className={`pb-4 px-1 border-b-2 font-medium text-sm transition ${
                  activeTab === 'papers'
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Papers
              </button>
              <button
                onClick={() => setActiveTab('rubrics')}
                className={`pb-4 px-1 border-b-2 font-medium text-sm transition ${
                  activeTab === 'rubrics'
                    ? 'border-blue-600 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                Rubrics
              </button>
            </nav>
          </div>

          {/* Papers Tab Content */}
          {activeTab === 'papers' && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div>
                <PaperForm onSuccess={handlePaperSubmitted} onToast={pushToast} />
              </div>
              <div>
                <PapersList onToast={pushToast} />
              </div>
            </div>
          )}

          {/* Rubrics Tab Content */}
          {activeTab === 'rubrics' && (
            <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
              <div>
                <RubricForm onSuccess={handleRubricCreated} onToast={pushToast} />
              </div>
              <div>
                <RubricsList />
              </div>
            </div>
          )}
        </div>
      </main>
    </div>
  )
}

export default App
