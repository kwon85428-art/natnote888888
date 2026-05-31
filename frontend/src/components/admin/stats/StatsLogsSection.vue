<script setup lang="ts">
import { formatZhDateTime } from '@/utils/datetime'
import type { AdminLogRow } from '@/api/admin/stats'
import type { MaintenanceCounts } from '@/api/admin/maintenance'

defineProps<{
  logs: AdminLogRow[]
  logActions: { value: string; label: string }[]
  logsTotal: number
  counts: MaintenanceCounts | null
}>()

const action = defineModel<string>('action', { required: true })
const logsPage = defineModel<number>('logsPage', { required: true })
const logsPageSize = defineModel<number>('logsPageSize', { required: true })

const emit = defineEmits<{
  loadLogs: [opts?: { resetPage?: boolean }]
  logsPageSizeChange: [size: number]
}>()
</script>

<template>
  <div class="stats-panel">
    <p v-if="counts" class="stats-panel__note">
      重要管理行为入库；访问明细与登录失败见
      <code>{{ counts.logs_dir }}/access.log</code>
    </p>

    <div class="admin-stack">
      <div class="toolbar">
        <el-select
          v-model="action"
          class="toolbar-field--q"
          placeholder="全部操作类型"
          clearable
          filterable
          size="default"
          @change="emit('loadLogs', { resetPage: true })"
        >
          <el-option v-for="opt in logActions" :key="opt.value" :label="opt.label" :value="opt.value" />
        </el-select>
        <el-button type="primary" @click="emit('loadLogs', { resetPage: true })">查询</el-button>
      </div>
      <el-table :data="logs" class="admin-table" size="small" stripe empty-text="暂无操作日志">
        <el-table-column prop="created_at" label="时间" width="158" show-overflow-tooltip>
          <template #default="{ row }">{{ formatZhDateTime(row.created_at) }}</template>
        </el-table-column>
        <el-table-column prop="admin_username" label="管理员" width="88" show-overflow-tooltip>
          <template #default="{ row }">{{ row.admin_username || '—' }}</template>
        </el-table-column>
        <el-table-column prop="action_label" label="操作" min-width="108" show-overflow-tooltip />
        <el-table-column prop="resource_type_label" label="资源" width="80" show-overflow-tooltip />
        <el-table-column prop="resource_id" label="ID" width="72" show-overflow-tooltip>
          <template #default="{ row }">{{ row.resource_id || '—' }}</template>
        </el-table-column>
        <el-table-column prop="detail" label="详情" min-width="140" show-overflow-tooltip />
        <el-table-column prop="ip" label="IP" width="108" show-overflow-tooltip>
          <template #default="{ row }">{{ row.ip || '—' }}</template>
        </el-table-column>
      </el-table>
      <div class="pager-row">
        <el-pagination
          v-model:current-page="logsPage"
          v-model:page-size="logsPageSize"
          :total="logsTotal"
          :page-sizes="[10, 20, 50]"
          layout="total, sizes, prev, pager, next"
          background
          small
          @current-change="emit('loadLogs')"
          @size-change="emit('logsPageSizeChange', $event)"
        />
      </div>
    </div>
  </div>
</template>
