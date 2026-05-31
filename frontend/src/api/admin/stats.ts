import http from '@/api/http'
import type { PageResult } from '@/types/models'

export type StatsSummary = {
  sites_total: number
  sites_valid: number
  sites_invalid: number
  sites_by_category: Record<string, number>
  articles_total: number
  articles_by_category: Record<string, number>
  articles_by_content_type: Record<string, number>
  visits_total: number
  visits_today: number
  site_clicks_total: number
  article_reads_total: number
}

export type TrendPoint = { label: string; count: number }

export type AdminLogRow = {
  id: number
  admin_id: number | null
  admin_username: string | null
  action: string
  action_label: string
  resource_type: string | null
  resource_type_label: string
  resource_id: string | null
  detail: string | null
  ip: string | null
  created_at: string
}

export type LogActionOption = { value: string; label: string }

export async function fetchStatsSummary() {
  const { data } = await http.get<StatsSummary>('/api/admin/stats/summary')
  return data
}

export async function fetchStatsLogActions() {
  const { data } = await http.get<{ items: LogActionOption[] }>('/api/admin/stats/log-actions')
  return data.items
}

export type TrendParams = {
  period: 'day' | 'week' | 'month'
  page: number
  page_size: number
}

export async function fetchStatsTrend(params: TrendParams) {
  const { data } = await http.get<PageResult<TrendPoint>>('/api/admin/stats/trend', { params })
  return data
}

export type AdminLogsParams = {
  action?: string
  page: number
  page_size: number
}

export async function fetchAdminLogs(params: AdminLogsParams) {
  const { data } = await http.get<PageResult<AdminLogRow>>('/api/admin/logs', { params })
  return data
}
