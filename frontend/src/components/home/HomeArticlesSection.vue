<script setup lang="ts">
import type { RouteLocationRaw } from 'vue-router'
import { Reading } from '@element-plus/icons-vue'
import ArticleListRow from '@/components/article/ArticleListRow.vue'
import type { ArticleSummary } from '@/types/models'

withDefaults(
  defineProps<{
    articles: ArticleSummary[]
    hideMore?: boolean
    moreRoute?: RouteLocationRaw
  }>(),
  {
    hideMore: false,
    moreRoute: () => ({ path: '/articles' }),
  },
)
</script>

<template>
  <section v-if="articles.length" class="article-section home-module" aria-labelledby="home-articles-title">
    <header class="home-module__head">
      <h2 id="home-articles-title" class="home-module__title">
        <el-icon class="home-section-ico" :size="16" aria-hidden="true"><Reading /></el-icon>
        <span>推荐文章</span>
      </h2>
      <div v-if="!hideMore" class="home-module__extra">
        <router-link :to="moreRoute" class="home-module__more">更多 →</router-link>
      </div>
    </header>

    <div class="article-sync home-module__body">
      <div
        class="home-article-list"
        :class="{ 'home-article-list--single': articles.length === 1 }"
      >
        <ArticleListRow
          v-for="n in articles"
          :key="n.id"
          :article="n"
          title-tag="h3"
          variant="home"
        />
      </div>
    </div>
  </section>
</template>
