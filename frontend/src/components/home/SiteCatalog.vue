<script setup lang="ts">
import type { Component } from 'vue'
import SiteCard from '@/components/home/SiteCard.vue'
import type { SiteCategoryRow } from '@/composables/useSitesHomePage'
import type { SiteItem } from '@/types/models'

defineProps<{
  categories: SiteCategoryRow[]
  sitesByCategory: Record<number, SiteItem[]>
  resolveIcon: (key?: string | null) => Component
}>()

const emit = defineEmits<{
  openSite: [site: SiteItem]
}>()
</script>

<template>
  <div class="site-main">
    <section class="sites-wrap" aria-label="按分类展示的网站">
      <article v-for="c in categories" :id="'site-cat-' + c.id" :key="c.id" class="site-cat">
        <header class="site-cat__head">
          <el-icon class="site-cat__ico" aria-hidden="true"><component :is="resolveIcon(c.icon_key)" /></el-icon>
          <h3 class="site-cat__title">{{ c.name }}</h3>
        </header>
        <div v-if="(sitesByCategory[c.id] || []).length" class="site-grid">
          <SiteCard
            v-for="s in sitesByCategory[c.id] || []"
            :key="s.id"
            :site="s"
            @open="emit('openSite', $event)"
          />
        </div>
        <p v-else class="site-cat__empty">该分类下暂无网站</p>
      </article>
    </section>
  </div>
</template>
