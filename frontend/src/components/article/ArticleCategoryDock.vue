<script setup lang="ts">
import type { Component } from 'vue'
import { ref, watch } from 'vue'
import { Grid, Menu } from '@element-plus/icons-vue'
import type { ArticleListCategory } from '@/composables/useArticleListPage'

const props = defineProps<{
  categories: ArticleListCategory[]
  filter: string
  currentLabel: string
  drawerVisible: boolean
  resolveIcon: (c: { icon_key?: string | null }) => Component
}>()

const emit = defineEmits<{
  'update:drawerVisible': [value: boolean]
  select: [value: string]
}>()

const dockScrollRef = ref<HTMLElement | null>(null)

defineExpose({ dockScrollRef })

watch(
  () => props.filter,
  () => {
    const wrap = dockScrollRef.value
    if (!wrap) return
    const key = props.filter === 'all' ? 'all' : props.filter
    requestAnimationFrame(() => {
      const btn = wrap.querySelector<HTMLElement>(`[data-article-cat="${key}"]`)
      btn?.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' })
    })
  },
)
</script>

<template>
  <nav v-if="categories.length" class="article-cat-dock" aria-label="文章分类快捷切换">
    <button
      type="button"
      class="article-cat-dock__open"
      aria-label="打开全部分类"
      @click="emit('update:drawerVisible', true)"
    >
      <el-icon :size="18"><Menu /></el-icon>
      <span>分类</span>
    </button>
    <span class="article-cat-dock__current" aria-live="polite">{{ currentLabel }}</span>
    <div ref="dockScrollRef" class="article-cat-dock__scroll">
      <button
        type="button"
        class="article-cat-dock__btn"
        :class="{ 'article-cat-dock__btn--active': filter === 'all' }"
        data-article-cat="all"
        @click="emit('select', 'all')"
      >
        <el-icon class="article-cat-dock__btn-ico" aria-hidden="true"><Grid /></el-icon>
        <span class="article-cat-dock__btn-txt">全部</span>
      </button>
      <button
        v-for="c in categories"
        :key="'dock-' + c.id"
        type="button"
        class="article-cat-dock__btn"
        :class="{ 'article-cat-dock__btn--active': filter === String(c.id) }"
        :data-article-cat="String(c.id)"
        @click="emit('select', String(c.id))"
      >
        <el-icon class="article-cat-dock__btn-ico" aria-hidden="true"><component :is="resolveIcon(c)" /></el-icon>
        <span class="article-cat-dock__btn-txt">{{ c.name }}</span>
      </button>
    </div>
  </nav>

  <el-drawer
    :model-value="drawerVisible"
    title="文章分类"
    direction="btt"
    size="72%"
    class="article-cat-drawer"
    destroy-on-close
    @update:model-value="emit('update:drawerVisible', $event)"
  >
    <div class="article-cat-drawer__list">
      <button
        type="button"
        class="article-cat-drawer__item"
        :class="{ 'article-cat-drawer__item--active': filter === 'all' }"
        @click="emit('select', 'all')"
      >
        <span class="article-cat-drawer__item-ico">
          <el-icon :size="22"><Grid /></el-icon>
        </span>
        <span class="article-cat-drawer__item-body">
          <span class="article-cat-drawer__item-name">全部</span>
          <span class="article-cat-drawer__item-desc">浏览所有文章</span>
        </span>
      </button>
      <button
        v-for="c in categories"
        :key="'drawer-' + c.id"
        type="button"
        class="article-cat-drawer__item"
        :class="{ 'article-cat-drawer__item--active': filter === String(c.id) }"
        @click="emit('select', String(c.id))"
      >
        <span class="article-cat-drawer__item-ico">
          <el-icon :size="22"><component :is="resolveIcon(c)" /></el-icon>
        </span>
        <span class="article-cat-drawer__item-body">
          <span class="article-cat-drawer__item-name">{{ c.name }}</span>
          <span v-if="c.description?.trim()" class="article-cat-drawer__item-desc">{{
            c.description.trim()
          }}</span>
        </span>
      </button>
    </div>
  </el-drawer>
</template>
