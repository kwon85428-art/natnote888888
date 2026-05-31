import { usePublicSettingsStore } from '@/stores/publicSettings'
import { DEFAULT_PLATFORM_SETTINGS } from '@/constants/platformDefaults'

export type DefaultHome = 'sites' | 'articles'

export type PublicLayoutSettings = {
  public_sites_enabled: boolean
  public_articles_enabled: boolean
  default_home: DefaultHome
}

function pickLayout(data: Record<string, unknown>): PublicLayoutSettings {
  return {
    public_sites_enabled: data.public_sites_enabled !== false,
    public_articles_enabled: data.public_articles_enabled !== false,
    default_home: data.default_home === 'articles' ? 'articles' : 'sites',
  }
}

export function peekPublicLayoutSettings(): PublicLayoutSettings {
  try {
    const row = usePublicSettingsStore().settings
    return pickLayout(row as Record<string, unknown>)
  } catch {
    return pickLayout(DEFAULT_PLATFORM_SETTINGS as Record<string, unknown>)
  }
}

/** 根路径 `/` 应跳转到的前台路径 */
export function resolvePublicEntryPath(s: PublicLayoutSettings): '/sites' | '/articles' | '/' {
  if (!s.public_sites_enabled && !s.public_articles_enabled) return '/'
  if (!s.public_sites_enabled) return '/articles'
  if (!s.public_articles_enabled) return '/sites'
  if (s.default_home === 'articles') return '/articles'
  return '/sites'
}
