<script setup lang="ts">
import type { Component } from 'vue'
import { DArrowLeft, DArrowRight, Grid, Reading } from '@element-plus/icons-vue'
import type { ArticleListCategory } from '@/composables/useArticleListPage'

defineProps<{
  categories: ArticleListCategory[]
  filter: string
  collapsed: boolean
  resolveIcon: (c: { icon_key?: string | null }) => Component
  catNavTitle: (c: ArticleListCategory) => string
}>()

const emit = defineEmits<{
  select: [value: string]
  toggleCollapsed: []
}>()
</script>

<template>
  <aside
    class="split__cat home-cat-aside"
    :class="{ 'split__cat--collapsed': collapsed }"
    aria-label="文章分类"
  >
    <div class="left-card left-card--tall">
      <div class="left-card__top">
        <h2 v-if="!collapsed" class="left-card__label">
          <el-icon class="home-section-ico" :size="15" aria-hidden="true"><Reading /></el-icon>
          <span>文章分类</span>
        </h2>
        <button
          type="button"
          class="left-card__collapse"
          :aria-expanded="!collapsed"
          aria-label="收起或展开分类栏"
          @click="emit('toggleCollapsed')"
        >
          <el-icon :size="16">
            <DArrowLeft v-if="!collapsed" />
            <DArrowRight v-else />
          </el-icon>
        </button>
      </div>
      <nav class="left-nav" aria-label="文章分类筛选">
        <button
          type="button"
          class="left-nav__btn"
          :class="{ 'left-nav__btn--active': filter === 'all' }"
          data-article-cat="all"
          title="浏览所有文章"
          @click="emit('select', 'all')"
        >
          <span class="left-nav__ico" aria-hidden="true">
            <el-icon :size="18"><Grid /></el-icon>
          </span>
          <span class="left-nav__text">
            <span class="left-nav__name">全部</span>
            <span class="left-nav__desc">浏览所有文章</span>
          </span>
        </button>
        <button
          v-for="c in categories"
          :key="c.id"
          type="button"
          class="left-nav__btn"
          :class="{ 'left-nav__btn--active': filter === String(c.id) }"
          :data-article-cat="String(c.id)"
          :title="catNavTitle(c)"
          @click="emit('select', String(c.id))"
        >
          <span class="left-nav__ico" aria-hidden="true">
            <el-icon :size="18"><component :is="resolveIcon(c)" /></el-icon>
          </span>
          <span class="left-nav__text">
            <span class="left-nav__name">{{ c.name }}</span>
            <span class="left-nav__desc">{{ c.description?.trim() || '' }}</span>
          </span>
        </button>
      </nav>
    </div>
  </aside>
</template>
