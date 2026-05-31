<script setup lang="ts">
import type { Component } from 'vue'
import { DArrowLeft, DArrowRight, FolderOpened } from '@element-plus/icons-vue'
import type { SiteCategoryRow } from '@/composables/useSitesHomePage'

defineProps<{
  categories: SiteCategoryRow[]
  activeId: number | null
  collapsed: boolean
  resolveIcon: (key?: string | null) => Component
  navTitle: (c: SiteCategoryRow) => string
}>()

const emit = defineEmits<{
  select: [id: number]
  toggleCollapsed: []
}>()
</script>

<template>
  <aside
    class="split__cat home-cat-aside"
    :class="{ 'split__cat--collapsed': collapsed }"
    aria-label="网址分类"
  >
    <div class="left-card left-card--tall">
      <div class="left-card__top">
        <h2 v-if="!collapsed" class="left-card__label">
          <el-icon class="home-section-ico" :size="15" aria-hidden="true"><FolderOpened /></el-icon>
          <span>网址分类</span>
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
      <nav class="left-nav" aria-label="网址分类锚点">
        <button
          v-for="c in categories"
          :key="c.id"
          type="button"
          class="left-nav__btn"
          :class="{ 'left-nav__btn--active': activeId === c.id }"
          :data-site-cat="c.id"
          :title="navTitle(c)"
          @click="emit('select', c.id)"
        >
          <span class="left-nav__ico" aria-hidden="true">
            <el-icon :size="18"><component :is="resolveIcon(c.icon_key)" /></el-icon>
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
