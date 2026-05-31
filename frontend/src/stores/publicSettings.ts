import { defineStore } from 'pinia'
import { computed, ref } from 'vue'
import http from '@/api/http'
import { DEFAULT_PLATFORM_SETTINGS } from '@/constants/platformDefaults'
import type { PlatformSettings } from '@/types/models'
import { pickMenuLabels } from '@/utils/menuLabels'
import { PLATFORM_SETTINGS_UPDATED } from '@/utils/platformSettingsEvents'
import { syncSeoBrandFromSettings } from '@/utils/seo'

function mergeSettings(data: PlatformSettings | Record<string, unknown>): PlatformSettings {
  return { ...DEFAULT_PLATFORM_SETTINGS, ...data } as PlatformSettings
}

let inflight: Promise<PlatformSettings> | null = null
let settingsListenerBound = false

/** 前台平台配置唯一数据源（响应式，供导航 / SEO / 布局共用） */
export const usePublicSettingsStore = defineStore('publicSettings', () => {
  const settings = ref<PlatformSettings>(mergeSettings(DEFAULT_PLATFORM_SETTINGS))
  const loadedFromApi = ref(false)

  const menuLabels = computed(() => pickMenuLabels(settings.value as Record<string, unknown>))

  function apply(data: PlatformSettings | Record<string, unknown>) {
    settings.value = mergeSettings(data)
    syncSeoBrandFromSettings(settings.value)
  }

  function applyDefaults() {
    settings.value = mergeSettings(DEFAULT_PLATFORM_SETTINGS)
    loadedFromApi.value = false
    syncSeoBrandFromSettings(settings.value)
  }

  function invalidate() {
    inflight = null
    loadedFromApi.value = false
  }

  async function loadFromApi(options?: { force?: boolean }): Promise<PlatformSettings> {
    const force = options?.force ?? false
    if (force) invalidate()
    if (inflight) return inflight
    if (!force && loadedFromApi.value) return settings.value

    inflight = http
      .get<PlatformSettings>('/api/public/settings')
      .then((res) => {
        apply(res.data)
        loadedFromApi.value = true
        return res.data
      })
      .finally(() => {
        inflight = null
      })

    return inflight
  }

  function bindSettingsUpdatedListener() {
    if (settingsListenerBound || typeof window === 'undefined') return
    settingsListenerBound = true
    window.addEventListener(PLATFORM_SETTINGS_UPDATED, (ev) => {
      const detail = (ev as CustomEvent<PlatformSettings>).detail
      if (detail) apply(detail)
    })
  }

  return {
    settings,
    loadedFromApi,
    menuLabels,
    apply,
    applyDefaults,
    invalidate,
    loadFromApi,
    bindSettingsUpdatedListener,
  }
})
