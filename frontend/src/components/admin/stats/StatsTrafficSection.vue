<script setup lang="ts">
import type { TrendPoint } from '@/api/admin/stats'

defineProps<{
  trend: TrendPoint[]
  trendTotal: number
  trendPeriodHint: () => string
}>()

const period = defineModel<'day' | 'week' | 'month'>('period', { required: true })
const trendPage = defineModel<number>('trendPage', { required: true })
const trendPageSize = defineModel<number>('trendPageSize', { required: true })

const emit = defineEmits<{
  loadTrend: []
  trendPageSizeChange: [size: number]
}>()
</script>

<template>
  <div class="stats-panel">
    <div class="stats-trend-toolbar">
      <p class="stats-trend-toolbar__hint">{{ trendPeriodHint() }}，按时间从新到旧。</p>
      <el-radio-group v-model="period" size="small" @change="emit('loadTrend')">
        <el-radio-button label="day">按日</el-radio-button>
        <el-radio-button label="week">按周</el-radio-button>
        <el-radio-button label="month">按月</el-radio-button>
      </el-radio-group>
    </div>

    <div class="admin-stack">
      <el-table :data="trend" class="admin-table" size="small" stripe empty-text="暂无访问数据">
        <el-table-column prop="label" label="时间" min-width="140" />
        <el-table-column prop="count" label="PV" width="100" align="right" />
      </el-table>
      <div class="pager-row">
        <el-pagination
          v-model:current-page="trendPage"
          v-model:page-size="trendPageSize"
          :total="trendTotal"
          :page-sizes="[10, 15, 20, 50]"
          layout="total, sizes, prev, pager, next"
          background
          small
          @current-change="emit('loadTrend')"
          @size-change="emit('trendPageSizeChange', $event)"
        />
      </div>
    </div>
  </div>
</template>
