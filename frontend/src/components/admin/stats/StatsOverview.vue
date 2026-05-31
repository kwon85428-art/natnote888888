<script setup lang="ts">
import type { MaintenanceCounts } from '@/api/admin/maintenance'
import type { StatsSummary } from '@/api/admin/stats'

defineProps<{
  summary: StatsSummary
  counts: MaintenanceCounts | null
  siteCategoryEntries: [string, number][]
  articleCategoryEntries: [string, number][]
}>()
</script>

<template>
  <div class="stats-panel">
    <p class="stats-panel__note">库内内容与访问汇总；PV 约 30 秒批量落库，今日数据可能略有延迟。</p>

    <div class="stats-kpi-grid">
      <div class="stats-kpi stats-kpi--accent">
        <span class="stats-kpi__value">{{ summary.visits_total }}</span>
        <span class="stats-kpi__label">累计 PV</span>
      </div>
      <div class="stats-kpi stats-kpi--accent">
        <span class="stats-kpi__value">{{ summary.visits_today }}</span>
        <span class="stats-kpi__label">今日 PV</span>
      </div>
      <div v-if="counts" class="stats-kpi">
        <span class="stats-kpi__value">{{ counts.visit_stat_days }}</span>
        <span class="stats-kpi__label">PV 保留天数</span>
      </div>
      <div class="stats-kpi">
        <span class="stats-kpi__value">{{ summary.site_clicks_total }}</span>
        <span class="stats-kpi__label">外链点击</span>
      </div>
      <div class="stats-kpi">
        <span class="stats-kpi__value">{{ summary.article_reads_total }}</span>
        <span class="stats-kpi__label">文章阅读</span>
      </div>
      <div class="stats-kpi">
        <span class="stats-kpi__value">{{ summary.sites_total }}</span>
        <span class="stats-kpi__label">网站总数</span>
        <span class="stats-kpi__sub">有效 {{ summary.sites_valid }} / 无效 {{ summary.sites_invalid }}</span>
      </div>
      <div class="stats-kpi">
        <span class="stats-kpi__value">{{ summary.articles_total }}</span>
        <span class="stats-kpi__label">文章总数</span>
      </div>
      <div v-if="counts" class="stats-kpi">
        <span class="stats-kpi__value">{{ counts.admin_logs }}</span>
        <span class="stats-kpi__label">操作日志条数</span>
      </div>
    </div>

    <div class="stats-breakdown">
      <el-collapse>
        <el-collapse-item title="按分类 / 类型查看数量" name="breakdown">
          <div class="stats-breakdown-grid">
            <div class="stats-breakdown-col">
              <h3 class="stats-breakdown-col__title">网址分类</h3>
              <ul v-if="siteCategoryEntries.length" class="stats-breakdown-list">
                <li v-for="[name, cnt] in siteCategoryEntries" :key="name">
                  <span>{{ name }}</span>
                  <strong>{{ cnt }}</strong>
                </li>
              </ul>
              <p v-else class="stats-breakdown-empty">暂无</p>
            </div>
            <div class="stats-breakdown-col">
              <h3 class="stats-breakdown-col__title">文章分类</h3>
              <ul v-if="articleCategoryEntries.length" class="stats-breakdown-list">
                <li v-for="[name, cnt] in articleCategoryEntries" :key="name">
                  <span>{{ name }}</span>
                  <strong>{{ cnt }}</strong>
                </li>
              </ul>
              <p v-else class="stats-breakdown-empty">暂无</p>
            </div>
            <div
              v-if="Object.keys(summary.articles_by_content_type).length"
              class="stats-breakdown-col"
            >
              <h3 class="stats-breakdown-col__title">文章类型</h3>
              <ul class="stats-breakdown-list">
                <li v-for="(cnt, name) in summary.articles_by_content_type" :key="name">
                  <span>{{ name }}</span>
                  <strong>{{ cnt }}</strong>
                </li>
              </ul>
            </div>
          </div>
        </el-collapse-item>
      </el-collapse>
    </div>
  </div>
</template>
