<script setup lang="ts">
import type { Component } from 'vue'
import { ref, watch } from 'vue'
import { Grid } from '@element-plus/icons-vue'
import type { ArticleListCategory } from '@/composables/useArticleListPage'

const props = defineProps<{
  categories: ArticleListCategory[]
  filter: string
  resolveIcon: (c: { icon_key?: string | null }) => Component
}>()

const emit = defineEmits<{
  select: [value: string]
}>()

const tabScrollRef = ref<HTMLElement | null>(null)

defineExpose({ tabScrollRef })

watch(
  () => props.filter,
  () => {
    const wrap = tabScrollRef.value
    if (!wrap) return
    const key = props.filter === 'all' ? 'all' : props.filter
    requestAnimationFrame(() => {
      const btn = wrap.querySelector<HTMLElement>(`[data-article-tab="${key}"]`)
      btn?.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' })
    })
  },
)
</script>

<template>
  <div class="article-cat-tabs">
    <div ref="tabScrollRef" class="article-cat-tabs__scroll">
      <div class="article-tabs article-cat-tabs__list" role="tablist" aria-label="文章分类">
        <button
          type="button"
          role="tab"
          class="article-tabs__btn"
          :class="{ 'article-tabs__btn--active': filter === 'all' }"
          :aria-selected="filter === 'all'"
          data-article-tab="all"
          @click="emit('select', 'all')"
        >
          <el-icon class="article-tabs__ico" aria-hidden="true"><Grid /></el-icon>
          全部
        </button>
        <button
          v-for="c in categories"
          :key="c.id"
          type="button"
          role="tab"
          class="article-tabs__btn"
          :class="{ 'article-tabs__btn--active': filter === String(c.id) }"
          :aria-selected="filter === String(c.id)"
          :data-article-tab="String(c.id)"
          :title="c.description?.trim() ? `${c.name} — ${c.description.trim()}` : c.name"
          @click="emit('select', String(c.id))"
        >
          <el-icon class="article-tabs__ico" aria-hidden="true"><component :is="resolveIcon(c)" /></el-icon>
          {{ c.name }}
        </button>
      </div>
    </div>
  </div>
</template>
