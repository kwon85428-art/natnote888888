import http from '@/api/http'
import type { PlatformSettings } from '@/types/models'

export type PlatformSettingsPayload = {
  platform_name?: string | null
  footer_text?: string | null
  contact_info?: string | null
  icp_text?: string | null
  icp_link_url?: string | null
  show_promoted_sites_on_sites?: boolean | null
  show_promoted_articles_on_sites?: boolean | null
  show_promoted_sites_on_articles?: boolean | null
  show_promoted_articles_on_articles?: boolean | null
  public_sites_enabled?: boolean | null
  public_articles_enabled?: boolean | null
  default_home?: 'sites' | 'articles' | null
  menu_sites_label?: string | null
  menu_articles_label?: string | null
}

export async function fetchAdminPlatformSettings() {
  const { data } = await http.get<PlatformSettings>('/api/admin/settings/platform')
  return data
}

export async function updateAdminPlatformSettings(body: PlatformSettingsPayload) {
  const { data } = await http.put<PlatformSettings>('/api/admin/settings/platform', body)
  return data
}

export async function uploadAdminPlatformLogo(file: File) {
  const fd = new FormData()
  fd.append('file', file)
  const { data } = await http.post<{ path: string }>('/api/admin/settings/platform/logo', fd, {
    headers: { 'Content-Type': 'multipart/form-data' },
  })
  return data.path
}
