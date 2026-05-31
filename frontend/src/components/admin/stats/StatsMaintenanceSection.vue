<script setup lang="ts">
import type { MaintenanceCounts, UploadPruneResult } from '@/api/admin/maintenance'

const emit = defineEmits<{
  cleanupVisitStats: []
  cleanupAdminLogs: []
  cleanupCaptcha: []
  previewOrphans: []
  executeOrphanPrune: []
}>()

defineProps<{
  counts: MaintenanceCounts | null
  cleaningVisit: boolean
  cleaningAdmin: boolean
  cleaningCaptcha: boolean
  orphan: UploadPruneResult | null
  orphanLoading: boolean
  formatBytes: (n: number) => string
}>()

const visitDays = defineModel<number>('visitDays', { required: true })
const adminDays = defineModel<number>('adminDays', { required: true })
</script>

<template>
  <div class="stats-panel">
    <p class="stats-panel__note">
      数据库记录需手工清理；文件日志在服务器目录按大小滚动，请自行归档或删除。
    </p>

    <div v-if="counts" class="stats-maint-overview">
      <span>PV 汇总 <strong>{{ counts.visit_stat_days }}</strong> 天</span>
      <span>操作日志 <strong>{{ counts.admin_logs }}</strong> 条</span>
      <span>验证码 <strong>{{ counts.captcha_challenges }}</strong> 条</span>
      <span>日志目录 <code>{{ counts.logs_dir }}</code></span>
    </div>

    <div class="stats-maint-grid">
      <div class="stats-maint-card">
        <div class="stats-maint-card__head">清理 PV 日汇总</div>
        <div class="stats-maint-card__body">
          <p class="stats-maint-card__desc">删除 visit_daily_stats 中早于指定天数的记录。</p>
          <div class="stats-maint-card__actions">
            <span class="stats-maint-card__label">早于</span>
            <el-input-number v-model="visitDays" :min="1" :max="3650" :step="30" controls-position="right" size="small" />
            <span class="stats-maint-card__label">天</span>
            <el-button type="danger" size="small" :loading="cleaningVisit" @click="emit('cleanupVisitStats')">
              执行清理
            </el-button>
          </div>
        </div>
      </div>

      <div class="stats-maint-card">
        <div class="stats-maint-card__head">清理操作日志</div>
        <div class="stats-maint-card__body">
          <p class="stats-maint-card__desc">删除 admin_logs 中早于指定天数的审计记录。</p>
          <div class="stats-maint-card__actions">
            <span class="stats-maint-card__label">早于</span>
            <el-input-number v-model="adminDays" :min="1" :max="3650" :step="30" controls-position="right" size="small" />
            <span class="stats-maint-card__label">天</span>
            <el-button type="danger" size="small" :loading="cleaningAdmin" @click="emit('cleanupAdminLogs')">
              执行清理
            </el-button>
          </div>
        </div>
      </div>

      <div class="stats-maint-card">
        <div class="stats-maint-card__head">清理过期验证码</div>
        <div class="stats-maint-card__body">
          <p class="stats-maint-card__desc">仅删除 captcha_challenges 中已过期的记录。</p>
          <el-button type="danger" size="small" :loading="cleaningCaptcha" @click="emit('cleanupCaptcha')">
            清理过期验证码
          </el-button>
        </div>
      </div>

      <div class="stats-maint-card stats-maint-card--wide">
        <div class="stats-maint-card__head">未引用的上传文件</div>
        <div class="stats-maint-card__body">
          <p class="stats-maint-card__desc">扫描 uploads 目录中未被数据库引用的文件，先预览再删除。</p>
          <div class="stats-maint-card__actions">
            <el-button size="small" :loading="orphanLoading" @click="emit('previewOrphans')">扫描预览</el-button>
            <el-button
              type="danger"
              size="small"
              :loading="orphanLoading"
              :disabled="!orphan || orphan.orphan_count === 0"
              @click="emit('executeOrphanPrune')"
            >
              删除未引用文件
            </el-button>
          </div>
          <div v-if="orphan" class="stats-orphan-result">
            未引用 <strong>{{ orphan.orphan_count }}</strong> 个，约
            <strong>{{ formatBytes(orphan.total_bytes) }}</strong>
            <template v-if="orphan.deleted_count">
              ；已删 <strong>{{ orphan.deleted_count }}</strong> 个，释放
              <strong>{{ formatBytes(orphan.freed_bytes) }}</strong>
            </template>
          </div>
          <ul v-if="orphan?.sample_paths?.length" class="stats-orphan-sample">
            <li v-for="p in orphan.sample_paths" :key="p">{{ p }}</li>
          </ul>
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.stats-maint-card__label {
  font-size: var(--fs-caption);
  color: var(--admin-muted, #64748b);
}
</style>
