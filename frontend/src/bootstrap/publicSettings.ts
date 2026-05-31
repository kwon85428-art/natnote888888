import type { Pinia } from 'pinia'
import { usePublicSettingsStore } from '@/stores/publicSettings'

const BOOTSTRAP_TIMEOUT_MS = 8000

function withTimeout<T>(promise: Promise<T>, ms: number): Promise<T> {
  return new Promise((resolve, reject) => {
    const timer = setTimeout(() => reject(new Error('bootstrap timeout')), ms)
    promise.then(
      (v) => {
        clearTimeout(timer)
        resolve(v)
      },
      (e) => {
        clearTimeout(timer)
        reject(e)
      },
    )
  })
}

/** 应用启动时拉取公开配置；须在 app.use(pinia) 之后、挂载之前调用 */
export async function bootstrapPublicSettings(pinia: Pinia): Promise<void> {
  const store = usePublicSettingsStore(pinia)
  store.bindSettingsUpdatedListener()
  try {
    await withTimeout(store.loadFromApi(), BOOTSTRAP_TIMEOUT_MS)
  } catch {
    store.applyDefaults()
  }
}
