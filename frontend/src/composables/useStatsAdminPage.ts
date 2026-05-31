import { computed, onMounted, ref, watch } from 'vue'
import {
  fetchAdminLogs,
  fetchStatsLogActions,
  fetchStatsSummary,
  fetchStatsTrend,
  type AdminLogRow,
  type StatsSummary,
  type TrendPoint,
} from '@/api/admin/stats'
import {
  cleanupAdminLogs,
  cleanupCaptcha,
  cleanupVisitStats,
  fetchMaintenanceCounts,
  pruneUploadOrphans,
  scanUploadOrphans,
  type MaintenanceCounts,
  type UploadPruneResult,
} from '@/api/admin/maintenance'
import { getApiErrorMessage } from '@/api/errors'
export function formatBytes(n: number) {
  if (n < 1024) return `${n} B`
  if (n < 1024 * 1024) return `${(n / 1024).toFixed(1)} KB`
  return `${(n / (1024 * 1024)).toFixed(2)} MB`
}

export function useStatsAdminPage() {
  const loading = ref(false)
  const summary = ref<StatsSummary | null>(null)
  const trend = ref<TrendPoint[]>([])
  const trendPage = ref(1)
  const trendPageSize = ref(15)
  const trendTotal = ref(0)
  const period = ref<'day' | 'week' | 'month'>('day')

  const logs = ref<AdminLogRow[]>([])
  const action = ref('')
  const logActions = ref<{ value: string; label: string }[]>([])
  const logsPage = ref(1)
  const logsPageSize = ref(20)
  const logsTotal = ref(0)

  const counts = ref<MaintenanceCounts | null>(null)
  const visitDays = ref(400)
  const adminDays = ref(180)
  const cleaningVisit = ref(false)
  const cleaningAdmin = ref(false)
  const cleaningCaptcha = ref(false)

  const orphan = ref<UploadPruneResult | null>(null)
  const orphanLoading = ref(false)

  const siteCategoryEntries = computed(() =>
    summary.value ? Object.entries(summary.value.sites_by_category).sort((a, b) => b[1] - a[1]) : [],
  )
  const articleCategoryEntries = computed(() =>
    summary.value ? Object.entries(summary.value.articles_by_category).sort((a, b) => b[1] - a[1]) : [],
  )

  function trendPeriodHint() {
    if (period.value === 'day') return '最近约 180 个自然日，按日汇总 PV（批量落库，略有延迟）'
    if (period.value === 'week') return '最近约 52 个自然周，由日数据汇总'
    return '最近约 36 个自然月，由日数据汇总'
  }

  async function loadSummary() {
    summary.value = await fetchStatsSummary()
  }

  async function loadLogActions() {
    logActions.value = await fetchStatsLogActions()
  }

  async function loadTrend() {
    const data = await fetchStatsTrend({
      period: period.value,
      page: trendPage.value,
      page_size: trendPageSize.value,
    })
    trend.value = data.items
    trendTotal.value = data.total
  }

  function onTrendPageSizeChange(s: number) {
    trendPageSize.value = s
    trendPage.value = 1
    void loadTrend()
  }

  async function loadLogs(opts?: { resetPage?: boolean }) {
    if (opts?.resetPage) logsPage.value = 1
    const data = await fetchAdminLogs({
      action: action.value || undefined,
      page: logsPage.value,
      page_size: logsPageSize.value,
    })
    logs.value = data.items
    logsTotal.value = data.total
  }

  function onLogsPageSizeChange(s: number) {
    logsPageSize.value = s
    logsPage.value = 1
    void loadLogs()
  }

  async function loadCounts() {
    counts.value = await fetchMaintenanceCounts()
  }

  async function refreshAll() {
    loading.value = true
    try {
      await Promise.all([loadSummary(), loadTrend(), loadLogs(), loadCounts()])
      ElMessage.success('已刷新')
    } catch (e: unknown) {
      ElMessage.error(getApiErrorMessage(e, '加载失败'))
    } finally {
      loading.value = false
    }
  }

  async function runCleanupVisitStats() {
    await ElMessageBox.confirm(
      `将永久删除 ${visitDays.value} 天之前的 PV 日汇总记录，不可恢复。`,
      '清理访问统计',
      { type: 'warning', confirmButtonText: '确认', cancelButtonText: '取消' },
    )
    cleaningVisit.value = true
    try {
      const data = await cleanupVisitStats(visitDays.value)
      ElMessage.success(
        data.visit_stats_deleted ? `已删除 ${data.visit_stats_deleted} 天的 PV 汇总` : '无符合条件的数据',
      )
      await Promise.all([loadCounts(), loadSummary(), loadTrend()])
    } catch (e: unknown) {
      ElMessage.error(getApiErrorMessage(e, '清理失败'))
    } finally {
      cleaningVisit.value = false
    }
  }

  async function runCleanupAdminLogs() {
    await ElMessageBox.confirm(
      `将永久删除 ${adminDays.value} 天之前的操作日志，不可恢复。`,
      '清理操作日志',
      { type: 'warning', confirmButtonText: '确认', cancelButtonText: '取消' },
    )
    cleaningAdmin.value = true
    try {
      const data = await cleanupAdminLogs(adminDays.value)
      ElMessage.success(data.admin_logs_deleted ? `已删除 ${data.admin_logs_deleted} 条` : '无符合条件的数据')
      await Promise.all([loadCounts(), loadLogs({ resetPage: true })])
    } catch (e: unknown) {
      ElMessage.error(getApiErrorMessage(e, '清理失败'))
    } finally {
      cleaningAdmin.value = false
    }
  }

  async function runCleanupCaptcha() {
    await ElMessageBox.confirm('将删除所有已过期的登录验证码记录。', '清理验证码', {
      type: 'warning',
      confirmButtonText: '确认',
      cancelButtonText: '取消',
    })
    cleaningCaptcha.value = true
    try {
      const data = await cleanupCaptcha()
      ElMessage.success(data.captcha_deleted ? `已删除 ${data.captcha_deleted} 条` : '无过期记录')
      await loadCounts()
    } catch (e: unknown) {
      ElMessage.error(getApiErrorMessage(e, '清理失败'))
    } finally {
      cleaningCaptcha.value = false
    }
  }

  async function previewOrphans() {
    orphanLoading.value = true
    try {
      orphan.value = await scanUploadOrphans()
    } catch (e: unknown) {
      ElMessage.error(getApiErrorMessage(e, '扫描失败'))
    } finally {
      orphanLoading.value = false
    }
  }

  async function executeOrphanPrune() {
    await ElMessageBox.confirm(
      '将永久删除未被数据库引用的上传文件。此操作不可恢复。',
      '删除未引用上传文件',
      { type: 'warning', confirmButtonText: '确认删除', cancelButtonText: '取消' },
    )
    orphanLoading.value = true
    try {
      const data = await pruneUploadOrphans()
      orphan.value = data
      ElMessage.success(`已删除 ${data.deleted_count} 个文件，释放约 ${formatBytes(data.freed_bytes)}`)
    } catch (e: unknown) {
      ElMessage.error(getApiErrorMessage(e, '清理失败'))
    } finally {
      orphanLoading.value = false
    }
  }

  onMounted(async () => {
    loading.value = true
    try {
      await loadLogActions()
      await Promise.all([loadSummary(), loadTrend(), loadLogs(), loadCounts()])
    } catch (e: unknown) {
      ElMessage.error(getApiErrorMessage(e, '加载失败'))
    } finally {
      loading.value = false
    }
  })

  watch(period, () => {
    trendPage.value = 1
    void loadTrend()
  })

  return {
    loading,
    summary,
    trend,
    trendPage,
    trendPageSize,
    trendTotal,
    period,
    logs,
    action,
    logActions,
    logsPage,
    logsPageSize,
    logsTotal,
    counts,
    visitDays,
    adminDays,
    cleaningVisit,
    cleaningAdmin,
    cleaningCaptcha,
    orphan,
    orphanLoading,
    siteCategoryEntries,
    articleCategoryEntries,
    trendPeriodHint,
    loadTrend,
    loadLogs,
    onTrendPageSizeChange,
    onLogsPageSizeChange,
    refreshAll,
    runCleanupVisitStats,
    runCleanupAdminLogs,
    runCleanupCaptcha,
    previewOrphans,
    executeOrphanPrune,
    formatBytes,
  }
}
