/** 前台主导航「网址 / 文章」菜单显示名（与平台设置 menu_*_label 同步） */

export const DEFAULT_MENU_SITES_LABEL = '网址'
export const DEFAULT_MENU_ARTICLES_LABEL = '文章'

export type PublicMenuLabels = {
  menu_sites_label: string
  menu_articles_label: string
}

export function pickMenuLabels(data: Record<string, unknown>): PublicMenuLabels {
  const sites = String(data.menu_sites_label ?? '').trim()
  const articles = String(data.menu_articles_label ?? '').trim()
  return {
    menu_sites_label: sites || DEFAULT_MENU_SITES_LABEL,
    menu_articles_label: articles || DEFAULT_MENU_ARTICLES_LABEL,
  }
}

/** 前台列表页浏览器标题：与主导航菜单文案（平台设置）一致 */
export function resolvePublicRouteSeo(
  path: string,
  settings: Record<string, unknown> | null | undefined,
  fallback: { title?: string; description?: string } = {},
): { title?: string; description?: string } {
  if (!settings) return fallback
  const labels = pickMenuLabels(settings)
  if (path === '/sites') {
    return { title: labels.menu_sites_label, description: fallback.description }
  }
  if (path === '/articles') {
    return { title: labels.menu_articles_label, description: fallback.description }
  }
  return fallback
}
