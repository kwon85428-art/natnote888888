import http from '@/api/http'
import type { ArticleCategoryItem, PageResult } from '@/types/models'

export type ArticleCategoryPayload = {
  name: string
  icon_key?: string | null
  description?: string | null
  sort_order: number
  enabled: boolean
}

type PageParams = { page: number; page_size: number }

export const articleCategoriesApi = {
  list(params: PageParams) {
    return http.get<PageResult<ArticleCategoryItem>>('/api/admin/article-categories', { params })
  },
  create(body: ArticleCategoryPayload) {
    return http.post('/api/admin/article-categories', body)
  },
  update(id: number, body: ArticleCategoryPayload) {
    return http.put(`/api/admin/article-categories/${id}`, body)
  },
  remove(id: number) {
    return http.delete(`/api/admin/article-categories/${id}`)
  },
}
