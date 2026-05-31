/** 与后端 Pydantic 响应对齐的核心前台/后台类型（手工维护，见 backend/app/schemas） */

export type ContentType = 'original' | 'external'

export type PlatformSettings = {
  platform_name: string
  logo_path?: string | null
  footer_text?: string | null
  contact_info?: string | null
  icp_text?: string | null
  icp_link_url?: string | null
  show_promoted_sites_on_sites?: boolean
  show_promoted_articles_on_sites?: boolean
  show_promoted_sites_on_articles?: boolean
  show_promoted_articles_on_articles?: boolean
  public_sites_enabled?: boolean
  public_articles_enabled?: boolean
  default_home?: 'sites' | 'articles'
  menu_sites_label?: string
  menu_articles_label?: string
}

/** 对应 ArticleSummaryOut（公开列表 / 首页预览，无正文） */
export type ArticleSummary = {
  id: number
  title: string
  summary?: string | null
  article_category_id: number
  article_category_name?: string | null
  tags?: string[] | null
  published_at: string
  cover_path?: string | null
  source_url?: string | null
  content_type: ContentType | string
  content_type_label?: string | null
  is_pinned: boolean
  pin_order?: number | null
  is_promoted: boolean
  visit_count: number
}

/** 对应 ArticleOut（详情 / 管理端） */
export type Article = ArticleSummary & {
  body_html?: string | null
  body_markdown?: string | null
  created_at: string
  updated_at?: string | null
}

/** 对应 SiteOut */
export type SiteItem = {
  id: number
  name: string
  url: string
  site_category_id: number
  site_category_name?: string | null
  tags?: string[] | null
  description?: string | null
  favicon_path?: string | null
  logo_path?: string | null
  is_valid: boolean
  invalid_note?: string | null
  sort_order: number
  is_promoted: boolean
  visit_count: number
  created_at: string
  updated_at?: string | null
}

export type SiteCategoryItem = {
  id: number
  name: string
  icon_key?: string | null
  description?: string | null
  sort_order: number
  enabled: boolean
  is_system?: boolean
}

export type ArticleCategoryItem = {
  id: number
  name: string
  icon_key?: string | null
  description?: string | null
  sort_order?: number
  enabled?: boolean
}

export type PageResult<T> = {
  items: T[]
  total: number
  page: number
  page_size: number
}

export type PublicHomePack = {
  settings: PlatformSettings
  site_categories: { id: number; name: string; description?: string; icon_key?: string | null }[]
  sites_by_category: Record<string, SiteItem[]>
  promoted_sites: SiteItem[]
  promoted_articles: ArticleSummary[]
}
