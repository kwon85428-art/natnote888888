<script setup lang="ts">
import { ref } from 'vue'
import StatsLogsSection from '@/components/admin/stats/StatsLogsSection.vue'
import StatsMaintenanceSection from '@/components/admin/stats/StatsMaintenanceSection.vue'
import StatsOverview from '@/components/admin/stats/StatsOverview.vue'
import StatsTrafficSection from '@/components/admin/stats/StatsTrafficSection.vue'
import { useStatsAdminPage } from '@/composables/useStatsAdminPage'
import '@/styles/stats-page.css'

const activeTab = ref('overview')

const {
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
} = useStatsAdminPage()
</script>

<template>
  <div v-loading="loading" class="admin-page stats-page">
    <header class="stats-page__head">
      <div class="admin-page-head stats-page__head-text">
        <h1 class="admin-page-title">统计与日志</h1>
        <p class="admin-page-desc">
          PV 按日汇总并批量落库；操作日志入库；明细见 <code>data/logs/</code> 滚动文件。
        </p>
      </div>
      <el-button type="primary" @click="refreshAll">刷新</el-button>
    </header>

    <el-tabs v-model="activeTab" type="border-card" class="stats-tabs">
      <el-tab-pane label="数据概览" name="overview" lazy>
        <StatsOverview
          v-if="summary"
          :summary="summary"
          :counts="counts"
          :site-category-entries="siteCategoryEntries"
          :article-category-entries="articleCategoryEntries"
        />
      </el-tab-pane>

      <el-tab-pane label="访问趋势" name="traffic" lazy>
        <StatsTrafficSection
          v-if="summary"
          v-model:period="period"
          v-model:trend-page="trendPage"
          v-model:trend-page-size="trendPageSize"
          :trend="trend"
          :trend-total="trendTotal"
          :trend-period-hint="trendPeriodHint"
          @load-trend="loadTrend"
          @trend-page-size-change="onTrendPageSizeChange"
        />
      </el-tab-pane>

      <el-tab-pane label="操作日志" name="logs" lazy>
        <StatsLogsSection
          v-model:action="action"
          v-model:logs-page="logsPage"
          v-model:logs-page-size="logsPageSize"
          :logs="logs"
          :log-actions="logActions"
          :logs-total="logsTotal"
          :counts="counts"
          @load-logs="loadLogs"
          @logs-page-size-change="onLogsPageSizeChange"
        />
      </el-tab-pane>

      <el-tab-pane label="数据维护" name="maint" lazy>
        <StatsMaintenanceSection
          v-model:visit-days="visitDays"
          v-model:admin-days="adminDays"
          :counts="counts"
          :cleaning-visit="cleaningVisit"
          :cleaning-admin="cleaningAdmin"
          :cleaning-captcha="cleaningCaptcha"
          :orphan="orphan"
          :orphan-loading="orphanLoading"
          :format-bytes="formatBytes"
          @cleanup-visit-stats="runCleanupVisitStats"
          @cleanup-admin-logs="runCleanupAdminLogs"
          @cleanup-captcha="runCleanupCaptcha"
          @preview-orphans="previewOrphans"
          @execute-orphan-prune="executeOrphanPrune"
        />
      </el-tab-pane>
    </el-tabs>
  </div>
</template>
