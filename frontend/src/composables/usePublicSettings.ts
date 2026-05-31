import { storeToRefs } from 'pinia'
import { usePublicSettingsStore } from '@/stores/publicSettings'

/** 读取响应式平台配置（与顶部导航同源 Pinia store） */
export function usePublicSettings() {
  const store = usePublicSettingsStore()
  const { settings, menuLabels } = storeToRefs(store)
  return { settings, menuLabels }
}
