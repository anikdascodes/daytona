import { create } from 'zustand'
import { persist } from 'zustand/middleware'
import type { LLMConfig, RuntimeConfig } from '../types'

interface ConfigState {
  llmConfig: LLMConfig | null
  runtimeConfig: RuntimeConfig | null
  sessionId: string | null
  isConfigured: boolean
  setLLMConfig: (config: LLMConfig) => void
  setRuntimeConfig: (config: RuntimeConfig) => void
  setSessionId: (id: string) => void
  setConfigured: (configured: boolean) => void
  reset: () => void
}

export const useConfigStore = create<ConfigState>()(
  persist(
    (set) => ({
      llmConfig: null,
      runtimeConfig: null,
      sessionId: null,
      isConfigured: false,
      setLLMConfig: (config) => set({ llmConfig: config }),
      setRuntimeConfig: (config) => set({ runtimeConfig: config }),
      setSessionId: (id) => set({ sessionId: id }),
      setConfigured: (configured) => set({ isConfigured: configured }),
      reset: () =>
        set({
          llmConfig: null,
          runtimeConfig: null,
          sessionId: null,
          isConfigured: false,
        }),
    }),
    {
      name: 'ai-engineer-config',
    }
  )
)
