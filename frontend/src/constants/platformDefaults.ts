import type { PlatformSettings } from '@/types/models'

/** 与后端 PlatformSettings 默认值一致 */
export const DEFAULT_PLATFORM_SETTINGS: Readonly<PlatformSettings> = {
  platform_name: 'NavNote',
  show_promoted_sites_on_sites: true,
  show_promoted_articles_on_sites: true,
  show_promoted_sites_on_articles: false,
  show_promoted_articles_on_articles: true,
  public_sites_enabled: true,
  public_articles_enabled: true,
  default_home: 'sites',
  menu_sites_label: '网址',
  menu_articles_label: '文章',
}
