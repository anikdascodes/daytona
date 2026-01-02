import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { useConfigStore } from '../store/configStore'
import { performHealthCheck, createSession } from '../services/api'
import { Button, Card, StatusBadge } from '../components/ui'
import type { HealthCheckResponse } from '../types'

export default function HealthCheckPage() {
  const navigate = useNavigate()
  const { llmConfig, runtimeConfig, setConfigured, setSessionId } = useConfigStore()

  const [checking, setChecking] = useState(false)
  const [creating, setCreating] = useState(false)
  const [healthResult, setHealthResult] = useState<HealthCheckResponse | null>(null)
  const [error, setError] = useState<string | null>(null)

  const runHealthCheck = async () => {
    if (!llmConfig || !runtimeConfig) {
      setError('Configuration missing. Please go back and configure.')
      return
    }

    setChecking(true)
    setHealthResult(null)
    setError(null)

    try {
      const result = await performHealthCheck(llmConfig, runtimeConfig)
      setHealthResult(result)
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Health check failed')
      setHealthResult({
        overall_healthy: false,
        llm_status: 'unhealthy',
        llm_message: 'Connection failed',
        runtime_status: 'unhealthy',
        runtime_message: err.message,
        timestamp: new Date().toISOString(),
      })
    } finally {
      setChecking(false)
    }
  }

  const startSession = async () => {
    if (!llmConfig || !runtimeConfig) return

    setCreating(true)
    setError(null)

    try {
      const result = await createSession({
        llm_config: llmConfig,
        runtime_config: runtimeConfig,
      })

      setSessionId(result.session_id)
      setConfigured(true)
      navigate('/chat')
    } catch (err: any) {
      setError(err.response?.data?.detail || err.message || 'Failed to create session')
    } finally {
      setCreating(false)
    }
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 py-12 px-4">
      <div className="max-w-2xl mx-auto">
        {/* Header */}
        <div className="text-center mb-10">
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="w-12 h-12 bg-blue-600 rounded-xl flex items-center justify-center">
              <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
              </svg>
            </div>
            <h1 className="text-4xl font-bold text-gray-900">Health Check</h1>
          </div>
          <p className="text-lg text-gray-600">
            Verify your configuration before starting
          </p>
        </div>

        {/* Step Indicator */}
        <div className="flex items-center justify-center gap-4 mb-8">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-green-500 text-white rounded-full flex items-center justify-center">
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
              </svg>
            </div>
            <span className="text-sm text-gray-500">Configure</span>
          </div>
          <div className="w-12 h-0.5 bg-green-500" />
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-medium">2</div>
            <span className="text-sm font-medium text-gray-900">Health Check</span>
          </div>
          <div className="w-12 h-0.5 bg-gray-300" />
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-gray-300 text-gray-600 rounded-full flex items-center justify-center text-sm font-medium">3</div>
            <span className="text-sm text-gray-500">Start Coding</span>
          </div>
        </div>

        <Card className="mb-6">
          {/* Configuration Summary */}
          <div className="mb-6 pb-6 border-b border-gray-200">
            <h3 className="text-sm font-medium text-gray-500 mb-3">Configuration Summary</h3>
            <div className="grid grid-cols-2 gap-4">
              <div className="bg-gray-50 rounded-lg p-3">
                <p className="text-xs text-gray-500 mb-1">LLM</p>
                <p className="font-medium text-gray-900">{llmConfig?.model || 'Not configured'}</p>
              </div>
              <div className="bg-gray-50 rounded-lg p-3">
                <p className="text-xs text-gray-500 mb-1">Runtime</p>
                <p className="font-medium text-gray-900 capitalize">{runtimeConfig?.provider || 'Not configured'}</p>
              </div>
            </div>
          </div>

          {/* Health Check Results or Initial State */}
          {!healthResult ? (
            <div className="text-center py-8">
              <div className="w-16 h-16 bg-blue-100 rounded-full flex items-center justify-center mx-auto mb-4">
                <svg className="w-8 h-8 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z" />
                </svg>
              </div>
              <h3 className="text-lg font-medium text-gray-900 mb-2">Ready to Check</h3>
              <p className="text-gray-600 mb-6">
                Click below to verify your LLM and runtime connections
              </p>
              <Button size="lg" onClick={runHealthCheck} loading={checking}>
                {checking ? 'Checking...' : 'Run Health Check'}
              </Button>
            </div>
          ) : (
            <div className="space-y-4">
              {/* LLM Status */}
              <div className="flex items-start justify-between p-4 bg-gray-50 rounded-lg">
                <div className="flex items-start gap-3">
                  <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                    healthResult.llm_status === 'healthy' ? 'bg-green-100' : 'bg-red-100'
                  }`}>
                    <svg className={`w-5 h-5 ${healthResult.llm_status === 'healthy' ? 'text-green-600' : 'text-red-600'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                    </svg>
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900">LLM Connection</h4>
                    <p className="text-sm text-gray-600">{healthResult.llm_message}</p>
                    {healthResult.llm_latency_ms && (
                      <p className="text-xs text-gray-400 mt-1">Latency: {healthResult.llm_latency_ms.toFixed(0)}ms</p>
                    )}
                  </div>
                </div>
                <StatusBadge status={healthResult.llm_status === 'healthy' ? 'healthy' : 'unhealthy'} />
              </div>

              {/* Runtime Status */}
              <div className="flex items-start justify-between p-4 bg-gray-50 rounded-lg">
                <div className="flex items-start gap-3">
                  <div className={`w-10 h-10 rounded-lg flex items-center justify-center ${
                    healthResult.runtime_status === 'healthy' ? 'bg-green-100' : 'bg-red-100'
                  }`}>
                    <svg className={`w-5 h-5 ${healthResult.runtime_status === 'healthy' ? 'text-green-600' : 'text-red-600'}`} fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01" />
                    </svg>
                  </div>
                  <div>
                    <h4 className="font-medium text-gray-900">Runtime Connection</h4>
                    <p className="text-sm text-gray-600">{healthResult.runtime_message}</p>
                  </div>
                </div>
                <StatusBadge status={healthResult.runtime_status === 'healthy' ? 'healthy' : 'unhealthy'} />
              </div>

              {/* Overall Status */}
              {healthResult.overall_healthy ? (
                <div className="bg-green-50 border border-green-200 rounded-lg p-4">
                  <div className="flex items-center gap-2 text-green-800">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span className="font-medium">All systems operational!</span>
                  </div>
                  <p className="text-green-700 text-sm mt-1">
                    Your configuration is ready. Start your AI coding session.
                  </p>
                </div>
              ) : (
                <div className="bg-red-50 border border-red-200 rounded-lg p-4">
                  <div className="flex items-center gap-2 text-red-800">
                    <svg className="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M12 8v4m0 4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                    <span className="font-medium">Configuration issues detected</span>
                  </div>
                  <p className="text-red-700 text-sm mt-1">
                    Please check your settings and try again.
                  </p>
                </div>
              )}
            </div>
          )}

          {error && (
            <div className="mt-4 bg-red-50 border border-red-200 rounded-lg p-4">
              <p className="text-red-800 text-sm">{error}</p>
            </div>
          )}
        </Card>

        {/* Actions */}
        <div className="flex justify-between">
          <Button variant="secondary" onClick={() => navigate('/')}>
            <svg className="w-5 h-5 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M11 17l-5-5m0 0l5-5m-5 5h12" />
            </svg>
            Back to Configuration
          </Button>

          {healthResult && (
            healthResult.overall_healthy ? (
              <Button size="lg" onClick={startSession} loading={creating}>
                {creating ? 'Creating Session...' : 'Start Session'}
                <svg className="w-5 h-5 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
                </svg>
              </Button>
            ) : (
              <Button onClick={runHealthCheck} loading={checking}>
                Retry Health Check
              </Button>
            )
          )}
        </div>
      </div>
    </div>
  )
}
