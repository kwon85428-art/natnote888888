import http from '@/api/http'

export type MaintenanceCounts = {
  visit_stat_days: number
  admin_logs: number
  captcha_challenges: number
  logs_dir: string
}

export type UploadPruneResult = {
  dry_run: boolean
  orphan_count: number
  total_bytes: number
  deleted_count: number
  freed_bytes: number
  sample_paths: string[]
}

export async function fetchMaintenanceCounts() {
  const { data } = await http.get<MaintenanceCounts>('/api/admin/maintenance/counts')
  return data
}

export async function cleanupVisitStats(olderThanDays: number) {
  const { data } = await http.post<{ visit_stats_deleted: number }>(
    '/api/admin/maintenance/cleanup/visit-stats',
    { older_than_days: olderThanDays },
  )
  return data
}

export async function cleanupAdminLogs(olderThanDays: number) {
  const { data } = await http.post<{ admin_logs_deleted: number }>(
    '/api/admin/maintenance/cleanup/admin-logs',
    { older_than_days: olderThanDays },
  )
  return data
}

export async function cleanupCaptcha() {
  const { data } = await http.post<{ captcha_deleted: number }>('/api/admin/maintenance/cleanup/captcha')
  return data
}

export async function scanUploadOrphans() {
  const { data } = await http.get<UploadPruneResult>('/api/admin/maintenance/upload-orphans')
  return data
}

export async function pruneUploadOrphans() {
  const { data } = await http.post<UploadPruneResult>('/api/admin/maintenance/prune-uploads', {
    execute: true,
    confirm_delete: true,
  })
  return data
}
