import { useEffect, useState } from 'react'
import Navigation from './components/Navigation'
import PaperForm from './components/PaperForm'
import PapersList from './components/PapersList'
import RubricForm from './components/RubricForm'
import RubricsList from './components/RubricsList'
import EvaluationsList from './components/EvaluationsList'
import PromptManager from './components/PromptManager'
import { ToastContainer } from './components/Toast'
import { healthApi, metricsApi } from './services/api'

type ActiveTab = 'papers' | 'rubrics' | 'evaluations' | 'prompts';

function App() {
  const [backendStatus, setBackendStatus] = useState<'checking' | 'connected' | 'error'>('checking')
  const [activeTab, setActiveTab] = useState<ActiveTab>('papers')
  const [backendAdapter, setBackendAdapter] = useState<string | undefined>()
  const [toasts, setToasts] = useState<{ id: number; type: 'success' | 'error' | 'info'; message: string }[]>([])
  const [accuracy, setAccuracy] = useState<{ total: number; correct: number; accuracy_percent: number | null; timestamp?: string } | null>(null)

  useEffect(() => {
    // Check backend health on mount
    healthApi.check()
      .then((resp) => {
        setBackendStatus('connected')
        setBackendAdapter(resp.adapter)
      })
      .catch(() => setBackendStatus('error'))
  }, [])

  useEffect(() => {
    const fetchAccuracy = () => {
      metricsApi.accuracy()
        .then(setAccuracy)
        .catch(() => setAccuracy(null))
    }
    fetchAccuracy()
    const handleEvalUpdated = () => fetchAccuracy()
    window.addEventListener('evaluationCreated', handleEvalUpdated)
    window.addEventListener('evaluationUpdated', handleEvalUpdated)
    return () => {
      window.removeEventListener('evaluationCreated', handleEvalUpdated)
      window.removeEventListener('evaluationUpdated', handleEvalUpdated)
    }
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
      <Navigation activeTab={activeTab} onChange={setActiveTab} />

      <main className="container mx-auto px-4 py-8">
        <ToastContainer toasts={toasts} onDismiss={dismissToast} />
        <div className="max-w-6xl mx-auto">
          {/* Backend Status Indicator */}
          <div className={`mb-6 px-4 py-2 rounded-lg flex flex-col gap-2 md:flex-row md:items-center md:justify-between ${
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
            <div className="flex flex-wrap items-center gap-4 text-xs text-gray-600">
              <span>http://127.0.0.1:8000</span>
              {backendAdapter && (
                <span className={`px-2 py-1 rounded-full ${
                  backendAdapter === 'ollama' ? 'bg-blue-100 text-blue-800' : 'bg-gray-100 text-gray-700'
                }`}>
                  Adapter: {backendAdapter}
                </span>
              )}
              <span className="px-2 py-1 rounded-full bg-white text-gray-800 border border-gray-200">
                Accuracy: {accuracy?.accuracy_percent !== null && accuracy?.accuracy_percent !== undefined
                  ? `${accuracy.accuracy_percent.toFixed(1)}% (${accuracy.correct}/${accuracy.total})`
                  : 'Needs feedback'}
              </span>
            </div>
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

          {/* Evaluations Tab Content */}
          {activeTab === 'evaluations' && (
            <EvaluationsList onToast={pushToast} />
          )}

          {activeTab === 'prompts' && (
            <PromptManager onToast={pushToast} />
          )}
        </div>
      </main>
    </div>
  )
}

export default App
