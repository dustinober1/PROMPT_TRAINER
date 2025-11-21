import { useEffect, useState } from 'react'
import Navigation from './components/Navigation'
import { healthApi } from './services/api'

function App() {
  const [backendStatus, setBackendStatus] = useState<'checking' | 'connected' | 'error'>('checking')

  useEffect(() => {
    // Check backend health on mount
    healthApi.check()
      .then(() => setBackendStatus('connected'))
      .catch(() => setBackendStatus('error'))
  }, [])

  return (
    <div className="min-h-screen bg-gray-50">
      <Navigation />

      <main className="container mx-auto px-4 py-8">
        <div className="max-w-4xl mx-auto">
          {/* Backend Status Indicator */}
          <div className={`mb-4 px-4 py-2 rounded-lg flex items-center justify-between ${
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

          <div className="bg-white rounded-lg shadow-md p-8 mb-8">
            <h2 className="text-3xl font-bold text-gray-800 mb-4">
              Welcome to Prompt Trainer
            </h2>
            <p className="text-gray-600 mb-4">
              An AI-powered paper grading system that learns and improves from your feedback.
            </p>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mt-6">
              <div className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition">
                <h3 className="font-semibold text-blue-600 mb-2">Submit Papers</h3>
                <p className="text-sm text-gray-600">
                  Upload or paste student papers for AI evaluation
                </p>
              </div>
              <div className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition">
                <h3 className="font-semibold text-blue-600 mb-2">Build Rubrics</h3>
                <p className="text-sm text-gray-600">
                  Create custom grading rubrics with multiple criteria
                </p>
              </div>
              <div className="border border-gray-200 rounded-lg p-4 hover:shadow-md transition">
                <h3 className="font-semibold text-blue-600 mb-2">Improve Prompts</h3>
                <p className="text-sm text-gray-600">
                  System learns from feedback to enhance accuracy
                </p>
              </div>
            </div>
          </div>

          <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
            <h3 className="text-lg font-semibold text-blue-800 mb-2">
              Getting Started
            </h3>
            <ol className="list-decimal list-inside space-y-2 text-gray-700">
              <li>Create a rubric with grading criteria</li>
              <li>Submit a paper for evaluation</li>
              <li>Review AI-generated scores and provide feedback</li>
              <li>Watch the system improve over time</li>
            </ol>
          </div>
        </div>
      </main>
    </div>
  )
}

export default App
