import http from '@/api/http'
import type { SiteCategoryItem, PageResult } from '@/types/models'

export type SiteCategoryPayload = {
  name: string
  icon_key?: string | null
  description?: string | null
  sort_order: number
  enabled: boolean
}

type PageParams = { page: number; page_size: number }

export const siteCategoriesApi = {
  list(params: PageParams) {
    return http.get<PageResult<SiteCategoryItem>>('/api/admin/site-categories', { params })
  },
  create(body: SiteCategoryPayload) {
    return http.post('/api/admin/site-categories', body)
  },
  update(id: number, body: SiteCategoryPayload) {
    return http.put(`/api/admin/site-categories/${id}`, body)
  },
  remove(id: number) {
    return http.delete(`/api/admin/site-categories/${id}`)
  },
}
