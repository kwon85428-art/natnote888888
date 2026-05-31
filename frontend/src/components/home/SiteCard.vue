<script setup lang="ts">
import { computed } from 'vue'
import SiteLogoPlaceholder from '@/components/SiteLogoPlaceholder.vue'
import type { SiteItem } from '@/types/models'
import { uploadUrl } from '@/utils/media'

const props = withDefaults(
  defineProps<{
    site: SiteItem
    variant?: 'default' | 'featured'
  }>(),
  { variant: 'default' },
)

const emit = defineEmits<{
  open: [site: SiteItem]
}>()

const siteTags = computed(() => {
  const tags = Array.isArray(props.site.tags)
    ? props.site.tags.map((t) => String(t).trim()).filter(Boolean)
    : []
  return tags.slice(0, 6)
})

function onLinkClick() {
  emit('open', props.site)
}
</script>

<template>
  <a
    :href="site.url"
    class="site-card"
    :class="{ 'site-card--feat': variant === 'featured' }"
    target="_blank"
    rel="noopener noreferrer"
    :title="site.description || site.name"
    @click="onLinkClick"
  >
    <template v-if="variant === 'featured'">
      <span class="site-card__name site-card__name--row1">{{ site.name }}</span>
      <div class="site-card__feat-mid">
        <div class="site-card__icon-wrap">
          <el-image
            v-if="site.logo_path || site.favicon_path"
            :src="uploadUrl(site.logo_path || site.favicon_path)"
            fit="contain"
            class="site-card__logo"
          >
            <template #error>
              <SiteLogoPlaceholder variant="featured" />
            </template>
          </el-image>
          <SiteLogoPlaceholder v-else variant="featured" />
        </div>
        <div class="site-card__desc-wrap">
          <span v-if="site.description" class="site-card__desc">{{ site.description }}</span>
        </div>
      </div>
      <div v-if="siteTags.length" class="site-card__feat-tags">
        <span v-for="tag in siteTags" :key="tag" class="site-card__feat-tag">{{ tag }}</span>
      </div>
    </template>
    <template v-else>
      <div class="site-card__top">
        <div class="site-card__icon-wrap">
          <el-image
            v-if="site.logo_path || site.favicon_path"
            :src="uploadUrl(site.logo_path || site.favicon_path)"
            fit="contain"
            class="site-card__logo"
          >
            <template #error>
              <SiteLogoPlaceholder variant="default" />
            </template>
          </el-image>
          <SiteLogoPlaceholder v-else variant="default" />
        </div>
        <div class="site-card__main">
          <span class="site-card__name">{{ site.name }}</span>
          <div class="site-card__desc-wrap">
            <span v-if="site.description" class="site-card__desc">{{ site.description }}</span>
          </div>
        </div>
      </div>
    </template>
  </a>
</template>

<style scoped>
a.site-card {
  display: block;
  text-decoration: none;
  color: inherit;
}
</style>
