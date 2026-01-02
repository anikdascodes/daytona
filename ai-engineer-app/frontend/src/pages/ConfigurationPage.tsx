import { useState, useEffect } from 'react'
import { useNavigate } from 'react-router-dom'
import { useConfigStore } from '../store/configStore'
import { getRuntimeProviders } from '../services/api'
import { Button, Input, Select, Card } from '../components/ui'
import type { RuntimeProviderInfo, LLMProvider, RuntimeProvider } from '../types'

export default function ConfigurationPage() {
  const navigate = useNavigate()
  const { setLLMConfig, setRuntimeConfig } = useConfigStore()

  // LLM State
  const [llmModel, setLLMModel] = useState('')
  const [llmApiKey, setLLMApiKey] = useState('')
  const [llmBaseUrl, setLLMBaseUrl] = useState('')

  // Runtime State
  const [runtimeProvider, setRuntimeProvider] = useState<RuntimeProvider>('docker')
  const [runtimeApiKey, setRuntimeApiKey] = useState('')
  const [runtimeApiUrl, setRuntimeApiUrl] = useState('')
  const [runtimeTarget, setRuntimeTarget] = useState('eu')
  const [runtimeProviders, setRuntimeProviders] = useState<RuntimeProviderInfo[]>([])

  // UI State
  const [loading, setLoading] = useState(true)
  const [errors, setErrors] = useState<Record<string, string>>({})

  useEffect(() => {
    loadProviders()
  }, [])

  const loadProviders = async () => {
    try {
      const runtime = await getRuntimeProviders()
      setRuntimeProviders(runtime.providers)
    } catch (error) {
      console.error('Failed to load providers:', error)
    } finally {
      setLoading(false)
    }
  }

  const validate = (): boolean => {
    const newErrors: Record<string, string> = {}

    if (!llmModel.trim()) {
      newErrors.llmModel = 'Model name is required'
    }

    if (!llmApiKey.trim()) {
      newErrors.llmApiKey = 'API key is required'
    }

    const selectedRuntime = runtimeProviders.find(p => p.id === runtimeProvider)
    if (selectedRuntime?.requires_api_key && !runtimeApiKey.trim()) {
      newErrors.runtimeApiKey = 'API key is required for this provider'
    }

    if (selectedRuntime?.requires_api_url && !runtimeApiUrl.trim()) {
      newErrors.runtimeApiUrl = 'API URL is required for this provider'
    }

    setErrors(newErrors)
    return Object.keys(newErrors).length === 0
  }

  const handleContinue = () => {
    if (!validate()) return

    // Auto-detect provider from model name
    let detectedProvider: LLMProvider = 'custom'
    const modelLower = llmModel.toLowerCase()
    if (modelLower.includes('gpt') || modelLower.includes('o1') || modelLower.startsWith('ft:')) {
      detectedProvider = 'openai'
    } else if (modelLower.includes('claude')) {
      detectedProvider = 'anthropic'
    } else if (modelLower.includes('gemini')) {
      detectedProvider = 'google'
    }

    setLLMConfig({
      provider: detectedProvider,
      model: llmModel,
      api_key: llmApiKey,
      base_url: llmBaseUrl || undefined,
      temperature: 0.0,
      max_tokens: 4096,
    })

    setRuntimeConfig({
      provider: runtimeProvider,
      api_key: runtimeApiKey || undefined,
      api_url: runtimeApiUrl || undefined,
      target: runtimeTarget || undefined,
      timeout: 300,
    })

    navigate('/health')
  }

  const selectedRuntimeProvider = runtimeProviders.find(p => p.id === runtimeProvider)

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 flex items-center justify-center">
        <div className="animate-pulse text-gray-600">Loading configuration...</div>
      </div>
    )
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-blue-50 py-12 px-4">
      <div className="max-w-4xl mx-auto">
        {/* Header */}
        <div className="text-center mb-10">
          <div className="flex items-center justify-center gap-3 mb-4">
            <div className="w-12 h-12 bg-blue-600 rounded-xl flex items-center justify-center">
              <svg className="w-7 h-7 text-white" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
              </svg>
            </div>
            <h1 className="text-4xl font-bold text-gray-900">AI Engineer</h1>
          </div>
          <p className="text-lg text-gray-600 max-w-xl mx-auto">
            Open-source AI coding assistant. No login required - bring your own LLM and compute.
          </p>
        </div>

        {/* Step Indicator */}
        <div className="flex items-center justify-center gap-4 mb-8">
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-blue-600 text-white rounded-full flex items-center justify-center text-sm font-medium">1</div>
            <span className="text-sm font-medium text-gray-900">Configure</span>
          </div>
          <div className="w-12 h-0.5 bg-gray-300" />
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-gray-300 text-gray-600 rounded-full flex items-center justify-center text-sm font-medium">2</div>
            <span className="text-sm text-gray-500">Health Check</span>
          </div>
          <div className="w-12 h-0.5 bg-gray-300" />
          <div className="flex items-center gap-2">
            <div className="w-8 h-8 bg-gray-300 text-gray-600 rounded-full flex items-center justify-center text-sm font-medium">3</div>
            <span className="text-sm text-gray-500">Start Coding</span>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* LLM Configuration */}
          <Card className="h-fit">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 bg-purple-100 rounded-lg flex items-center justify-center">
                <svg className="w-5 h-5 text-purple-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
                </svg>
              </div>
              <div>
                <h2 className="text-xl font-semibold text-gray-900">LLM Provider</h2>
                <p className="text-sm text-gray-500">Choose your AI brain</p>
              </div>
            </div>

            <div className="space-y-4">
              <Input
                label="Model"
                placeholder="gpt-4o, claude-sonnet-4-20250514, gemini-2.0-flash, etc."
                value={llmModel}
                onChange={(e) => setLLMModel(e.target.value)}
                error={errors.llmModel}
                hint="Enter your model name (e.g., gpt-4o, claude-sonnet-4-20250514, gemini-2.0-flash)"
              />

              <Input
                label="API Key"
                type="password"
                placeholder="Enter your API key"
                value={llmApiKey}
                onChange={(e) => setLLMApiKey(e.target.value)}
                error={errors.llmApiKey}
              />

              <Input
                label="Base URL (Optional)"
                placeholder="https://api.openai.com/v1"
                value={llmBaseUrl}
                onChange={(e) => setLLMBaseUrl(e.target.value)}
                error={errors.llmBaseUrl}
                hint="Leave empty for default provider URLs, or enter custom endpoint"
              />

            </div>
          </Card>

          {/* Runtime Configuration */}
          <Card className="h-fit">
            <div className="flex items-center gap-3 mb-6">
              <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                <svg className="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 12h14M5 12a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v4a2 2 0 01-2 2M5 12a2 2 0 00-2 2v4a2 2 0 002 2h14a2 2 0 002-2v-4a2 2 0 00-2-2m-2-4h.01M17 16h.01" />
                </svg>
              </div>
              <div>
                <h2 className="text-xl font-semibold text-gray-900">Runtime Environment</h2>
                <p className="text-sm text-gray-500">Where code runs</p>
              </div>
            </div>

            <div className="space-y-4">
              <Select
                label="Provider"
                value={runtimeProvider}
                onChange={(e) => {
                  const provider = e.target.value as RuntimeProvider
                  setRuntimeProvider(provider)
                  const prov = runtimeProviders.find(p => p.id === provider)
                  if (prov?.default_api_url) {
                    setRuntimeApiUrl(prov.default_api_url)
                  }
                }}
                options={runtimeProviders.map(p => ({
                  value: p.id,
                  label: `${p.name} - ${p.description}`,
                }))}
              />

              {selectedRuntimeProvider?.signup_url && (
                <p className="text-sm text-gray-500">
                  Need an account?{' '}
                  <a
                    href={selectedRuntimeProvider.signup_url}
                    target="_blank"
                    rel="noopener noreferrer"
                    className="text-blue-600 hover:underline"
                  >
                    Sign up at {selectedRuntimeProvider.name}
                  </a>
                </p>
              )}

              {selectedRuntimeProvider?.requires_api_key && (
                <Input
                  label="API Key"
                  type="password"
                  placeholder="Enter API key"
                  value={runtimeApiKey}
                  onChange={(e) => setRuntimeApiKey(e.target.value)}
                  error={errors.runtimeApiKey}
                />
              )}

              {selectedRuntimeProvider?.requires_api_url && (
                <Input
                  label="API URL"
                  placeholder={selectedRuntimeProvider.default_api_url || 'Enter API URL'}
                  value={runtimeApiUrl}
                  onChange={(e) => setRuntimeApiUrl(e.target.value)}
                  error={errors.runtimeApiUrl}
                />
              )}

              {runtimeProvider === 'daytona' && (
                <Input
                  label="Target Region"
                  placeholder="eu"
                  value={runtimeTarget}
                  onChange={(e) => setRuntimeTarget(e.target.value)}
                  hint="Daytona deployment region"
                />
              )}

              {runtimeProvider === 'docker' && (
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
                  <p className="text-sm text-blue-800">
                    <strong>Docker</strong> runs locally on your machine. Make sure Docker Desktop is running.
                  </p>
                </div>
              )}
            </div>
          </Card>
        </div>

        {/* Continue Button */}
        <div className="mt-8 flex justify-center">
          <Button size="lg" onClick={handleContinue} className="px-12">
            Continue to Health Check
            <svg className="w-5 h-5 ml-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 7l5 5m0 0l-5 5m5-5H6" />
            </svg>
          </Button>
        </div>
      </div>
    </div>
  )
}
