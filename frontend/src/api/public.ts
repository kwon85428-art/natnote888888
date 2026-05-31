import http from '@/api/http'
import type {
  Article,
  ArticleCategoryItem,
  ArticleSummary,
  PageResult,
  PublicHomePack,
  SiteItem,
} from '@/types/models'

export async function trackPageVisit() {
  try {
    return await http.post('/api/public/visit')
  } catch {
    /* ignore */
  }
}

export async function fetchPublicHome() {
  const { data } = await http.get<PublicHomePack>('/api/public/home')
  return data
}

export async function fetchArticleCategories() {
  const { data } = await http.get<ArticleCategoryItem[]>('/api/public/article-categories')
  return data
}

export type ArticleListParams = {
  article_category_id?: number
  page?: number
  page_size?: number
}

export async function fetchArticlesPage(params: ArticleListParams) {
  const { data } = await http.get<PageResult<ArticleSummary>>('/api/public/articles', { params })
  return data
}

export async function fetchArticleDetail(id: number) {
  const { data } = await http.get<Article>(`/api/public/articles/${id}`)
  return data
}

export type ArticleReadPayload =
  | { mode: 'inline'; body_html: string }
  | { mode: 'redirect'; url: string }

export async function fetchArticleRead(id: number) {
  const { data } = await http.get<ArticleReadPayload>(`/api/public/articles/${id}/read`)
  return data
}

export async function fetchPromotedSites(limit = 12) {
  const { data } = await http.get<SiteItem[]>('/api/public/sites/promoted', { params: { limit } })
  return data
}

export async function fetchPromotedArticles(limit = 12) {
  const { data } = await http.get<ArticleSummary[]>('/api/public/articles/promoted', { params: { limit } })
  return data
}

export async function trackSiteVisit(siteId: number) {
  return http.post(`/api/public/sites/${siteId}/visit`)
}
