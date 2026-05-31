import http from '@/api/http'
import type { PageResult, SiteCategoryItem, SiteItem } from '@/types/models'

export type AdminSitesListParams = {
  q?: string
  site_category_id?: number
  page: number
  page_size: number
}

export type AdminSitePayload = {
  name: string
  url: string
  site_category_id: number
  tags?: string[] | null
  description?: string | null
  favicon_path?: string | null
  logo_path?: string | null
  is_valid: boolean
  sort_order: number
  is_promoted: boolean
}

export type AdminSiteUpdatePayload = AdminSitePayload & {
  invalid_note?: string | null
}

export type SiteFetchMeta = {
  title: string
  description: string | null
  favicon_url: string | null
  resolved_url: string
}

export type SiteCheckResult = { site_id: number; ok: boolean; message: string | null }

export async function fetchAdminSitesPage(params: AdminSitesListParams) {
  const { data } = await http.get<PageResult<SiteItem>>('/api/admin/sites', { params })
  return data
}

export async function fetchAdminSiteCategoriesAll() {
  const { data } = await http.get<PageResult<SiteCategoryItem>>('/api/admin/site-categories', {
    params: { page: 1, page_size: 500 },
  })
  return data.items
}

export async function createAdminSite(body: AdminSitePayload) {
  const { data } = await http.post<SiteItem>('/api/admin/sites', body)
  return data
}

export async function updateAdminSite(id: number, body: AdminSiteUpdatePayload) {
  const { data } = await http.put<SiteItem>(`/api/admin/sites/${id}`, body)
  return data
}

export async function deleteAdminSite(id: number) {
  await http.delete(`/api/admin/sites/${id}`)
}

export async function fetchSiteMeta(url: string) {
  const { data } = await http.post<SiteFetchMeta>('/api/admin/sites/fetch-meta', { url })
  return data
}

export async function uploadFaviconFromUrl(url: string) {
  const { data } = await http.post<{ path: string }>('/api/admin/sites/upload-favicon-from-url', { url })
  return data.path
}

export async function uploadAdminSiteLogo(file: File) {
  const fd = new FormData()
  fd.append('file', file)
  const { data } = await http.post<{ path: string }>('/api/admin/sites/upload-logo', fd, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data.path
}

export async function checkAdminSite(id: number) {
  const { data } = await http.post<SiteCheckResult>(`/api/admin/sites/${id}/check`)
  return data
}

export async function checkAdminSitesBatch(ids: number[]) {
  const { data } = await http.post<SiteCheckResult[]>('/api/admin/sites/check-batch', ids)
  return data
}
