<script setup lang="ts">
import type { Component } from 'vue'
import { ref } from 'vue'
import { Menu } from '@element-plus/icons-vue'
import type { SiteCategoryRow } from '@/composables/useSitesHomePage'

defineProps<{
  categories: SiteCategoryRow[]
  activeId: number | null
  currentLabel: string
  drawerVisible: boolean
  resolveIcon: (key?: string | null) => Component
}>()

const emit = defineEmits<{
  'update:drawerVisible': [value: boolean]
  select: [id: number]
  selectFromDrawer: [category: SiteCategoryRow]
}>()

const dockScrollRef = ref<HTMLElement | null>(null)

defineExpose({ dockScrollRef })
</script>

<template>
  <nav class="site-cat-dock" aria-label="网址分类快捷切换">
    <button
      type="button"
      class="site-cat-dock__open"
      aria-label="打开全部分类"
      @click="emit('update:drawerVisible', true)"
    >
      <el-icon :size="18"><Menu /></el-icon>
      <span>分类</span>
    </button>
    <span class="site-cat-dock__current" aria-live="polite">{{ currentLabel }}</span>
    <div ref="dockScrollRef" class="site-cat-dock__scroll">
      <button
        v-for="c in categories"
        :key="'dock-' + c.id"
        type="button"
        class="site-cat-dock__btn"
        :class="{ 'site-cat-dock__btn--active': activeId === c.id }"
        :data-site-cat="c.id"
        @click="emit('select', c.id)"
      >
        <el-icon class="site-cat-dock__btn-ico" aria-hidden="true"
          ><component :is="resolveIcon(c.icon_key)"
        /></el-icon>
        <span class="site-cat-dock__btn-txt">{{ c.name }}</span>
      </button>
    </div>
  </nav>

  <el-drawer
    :model-value="drawerVisible"
    title="网址分类"
    direction="btt"
    size="72%"
    class="cat-drawer"
    destroy-on-close
    @update:model-value="emit('update:drawerVisible', $event)"
  >
    <div class="cat-drawer__list">
      <button
        v-for="c in categories"
        :key="'drawer-cat-' + c.id"
        type="button"
        class="cat-drawer__item"
        :class="{ 'cat-drawer__item--active': activeId === c.id }"
        @click="emit('selectFromDrawer', c)"
      >
        <span class="cat-drawer__item-ico">
          <el-icon :size="22"><component :is="resolveIcon(c.icon_key)" /></el-icon>
        </span>
        <span class="cat-drawer__item-body">
          <span class="cat-drawer__item-name">{{ c.name }}</span>
          <span class="cat-drawer__item-desc">{{ c.description?.trim() || '' }}</span>
        </span>
      </button>
    </div>
  </el-drawer>
</template>
