import http from '@/api/http'
import type { Article, ArticleCategoryItem, PageResult } from '@/types/models'

export type AdminArticleListParams = {
  q?: string
  article_category_id?: number
  content_type?: string
  page: number
  page_size: number
}

export type AdminArticlePayload = {
  title: string
  summary?: string | null
  article_category_id: number
  tags?: string[] | null
  published_at: string
  cover_path?: string | null
  source_url?: string | null
  content_type: string
  body_markdown?: string | null
  body_html?: string | null
  is_pinned: boolean
  pin_order?: number | null
  is_promoted: boolean
}

export async function fetchAdminArticlesPage(params: AdminArticleListParams) {
  const { data } = await http.get<PageResult<Article>>('/api/admin/articles', { params })
  return data
}

export async function fetchAdminArticleCategoriesAll() {
  const { data } = await http.get<PageResult<ArticleCategoryItem>>('/api/admin/article-categories', {
    params: { page: 1, page_size: 500 },
  })
  return data.items
}

export async function createAdminArticle(body: AdminArticlePayload) {
  const { data } = await http.post<Article>('/api/admin/articles', body)
  return data
}

export async function updateAdminArticle(id: number, body: AdminArticlePayload) {
  const { data } = await http.put<Article>(`/api/admin/articles/${id}`, body)
  return data
}

export async function deleteAdminArticle(id: number) {
  await http.delete(`/api/admin/articles/${id}`)
}

export async function uploadAdminArticleCover(file: File) {
  const fd = new FormData()
  fd.append('file', file)
  const { data } = await http.post<{ path: string }>('/api/admin/articles/upload-cover', fd, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data.path
}

export async function uploadAdminArticleBodyImage(file: File) {
  const fd = new FormData()
  fd.append('file', file)
  const { data } = await http.post<{ path: string }>('/api/admin/articles/upload-body-image', fd, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data.path
}
