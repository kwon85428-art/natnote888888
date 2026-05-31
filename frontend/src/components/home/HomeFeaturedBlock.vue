<script setup lang="ts">
import type { RouteLocationRaw } from 'vue-router'
import { StarFilled } from '@element-plus/icons-vue'
import SiteCard from '@/components/home/SiteCard.vue'
import type { SiteItem } from '@/types/models'

withDefaults(
  defineProps<{
    sites: SiteItem[]
    hideMore?: boolean
    moreRoute?: RouteLocationRaw
  }>(),
  {
    hideMore: false,
    moreRoute: () => ({ path: '/sites' }),
  },
)

const emit = defineEmits<{
  openSite: [site: SiteItem]
}>()
</script>

<template>
  <section v-if="sites.length" class="featured-block home-module" aria-labelledby="feat-sites-title">
    <header class="home-module__head">
      <h2 id="feat-sites-title" class="home-module__title">
        <el-icon class="home-section-ico" :size="16" aria-hidden="true"><StarFilled /></el-icon>
        <span>推荐网址</span>
      </h2>
      <div v-if="!hideMore" class="home-module__extra">
        <router-link :to="moreRoute" class="home-module__more">更多 →</router-link>
      </div>
    </header>
    <div class="featured-sync home-module__body">
      <div class="featured-grid">
        <SiteCard
          v-for="s in sites"
          :key="s.id"
          :site="s"
          variant="featured"
          @open="emit('openSite', $event)"
        />
      </div>
    </div>
  </section>
</template>
