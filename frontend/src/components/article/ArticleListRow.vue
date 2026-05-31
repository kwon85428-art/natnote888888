<script setup lang="ts">
import { computed } from 'vue'
import { RouterLink } from 'vue-router'
import { articleContentTypeLabel, articleSummaryText } from '@/utils/text'
import { formatZhDateTime } from '@/utils/datetime'
import { uploadUrl } from '@/utils/media'
import type { ArticleSummary } from '@/types/models'
import ArticleCoverPlaceholder from '@/components/ArticleCoverPlaceholder.vue'

const props = withDefaults(
  defineProps<{
    article: ArticleSummary
    titleTag?: 'h2' | 'h3'
    variant?: 'default' | 'home'
  }>(),
  { titleTag: 'h2', variant: 'default' },
)

const summary = computed(() => articleSummaryText(props.article))
const typeLabel = computed(() => articleContentTypeLabel(props.article))
const isExternal = computed(() => props.article.content_type === 'external')
const showReads = computed(() => Number(props.article.visit_count) > 0)
const articleTo = computed(() => `/articles/${props.article.id}`)
</script>

<template>
  <RouterLink
    :to="articleTo"
    class="article-row"
    :class="{ 'article-row--home': variant === 'home' }"
    :aria-label="`查看文章：${article.title}`"
  >
    <!-- 第一行：标题 + 属性标签 -->
    <header class="article-row__head">
      <component :is="titleTag" class="article-row__title">{{ article.title }}</component>
      <div
        v-if="article.is_promoted || article.is_pinned || typeLabel"
        class="article-row__badges"
        aria-label="文章属性"
      >
        <span v-if="article.is_promoted" class="article-row__chip article-row__chip--promo">推广</span>
        <span v-if="article.is_pinned" class="article-row__chip article-row__chip--pin">置顶</span>
        <span
          class="article-row__chip article-row__chip--kind"
          :class="{ 'article-row__chip--orig': !isExternal, 'article-row__chip--ext': isExternal }"
        >
          {{ typeLabel }}
        </span>
      </div>
    </header>

    <!-- 第二行：圆角方形封面 + 摘要 -->
    <div class="article-row__body">
      <div class="article-row__media">
        <el-image
          v-if="article.cover_path"
          :src="uploadUrl(article.cover_path)"
          fit="cover"
          class="article-row__img"
        >
          <template #error>
            <div class="article-row__placeholder" aria-hidden="true">
              <ArticleCoverPlaceholder :density="variant === 'home' ? 'compact' : 'list'" />
            </div>
          </template>
        </el-image>
        <div v-else class="article-row__placeholder" aria-hidden="true">
          <ArticleCoverPlaceholder :density="variant === 'home' ? 'compact' : 'list'" />
        </div>
      </div>
      <p v-if="summary" class="article-row__summary">{{ summary }}</p>
      <p v-else class="article-row__summary article-row__summary--empty">暂无摘要</p>
    </div>

    <!-- 第三行：日期、阅读数等 -->
    <footer class="article-row__meta">
      <time class="article-row__time" :datetime="article.published_at">{{
        formatZhDateTime(article.published_at, 'list')
      }}</time>
      <template v-if="showReads">
        <span class="article-row__meta-dot" aria-hidden="true">·</span>
        <span class="article-row__reads">阅读 {{ article.visit_count }}</span>
      </template>
      <template v-if="variant !== 'home' && article.article_category_name">
        <span class="article-row__meta-dot" aria-hidden="true">·</span>
        <span class="article-row__cat">{{ article.article_category_name }}</span>
      </template>
    </footer>
  </RouterLink>
</template>

<style scoped>
a.article-row {
  text-decoration: none;
  color: inherit;
}

.article-row {
  display: flex;
  flex-direction: column;
  gap: 10px;
  padding: 14px 14px 12px;
  background: linear-gradient(180deg, #ffffff 0%, #fafbfc 100%);
  border: 1px solid var(--border-subtle);
  border-radius: 12px;
  cursor: pointer;
  -webkit-tap-highlight-color: transparent;
  transition:
    border-color 0.2s ease,
    box-shadow 0.2s ease,
    transform 0.16s ease;
  box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
}

.article-row--home {
  gap: 8px;
  padding: 12px 12px 10px;
  background: linear-gradient(180deg, #faf5ff 0%, #ffffff 58%);
  border: 1px solid #ddd6fe;
  box-shadow: 0 1px 2px rgba(91, 33, 182, 0.06);
  height: 100%;
}

.article-row--home:hover {
  border-color: #a78bfa;
  background: linear-gradient(180deg, #f5f3ff 0%, #ffffff 62%);
  box-shadow: 0 2px 12px rgba(91, 33, 182, 0.12);
  transform: translateY(-1px);
}

.article-row:focus-visible {
  outline: 2px solid var(--accent, #1d4ed8);
  outline-offset: 2px;
}

.article-row--home:focus-visible {
  outline-color: #7c3aed;
}

.article-row:hover {
  border-color: #c7d2fe;
  box-shadow: 0 4px 14px rgba(79, 70, 229, 0.1);
  transform: translateY(-1px);
}

.article-row:active {
  transform: translateY(0);
}

/* 第一行 */
.article-row__head {
  display: flex;
  align-items: flex-start;
  justify-content: space-between;
  gap: 8px 12px;
  min-width: 0;
}

.article-row__title {
  margin: 0;
  flex: 1 1 auto;
  min-width: 0;
  font-size: var(--fs-title-sm);
  font-weight: 700;
  color: var(--text);
  line-height: 1.4;
  letter-spacing: -0.025em;
  word-break: break-word;
  display: -webkit-box;
  -webkit-line-clamp: 2;
  line-clamp: 2;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.article-row--home .article-row__title {
  font-size: var(--fs-body);
  font-weight: 800;
  -webkit-line-clamp: 1;
  line-clamp: 1;
}

.article-row__badges {
  display: flex;
  flex-wrap: wrap;
  align-items: center;
  justify-content: flex-end;
  gap: 5px;
  flex: 0 0 auto;
  max-width: 46%;
}

.article-row__chip {
  flex-shrink: 0;
  font-size: var(--fs-micro);
  font-weight: 700;
  padding: 3px 9px;
  border-radius: 999px;
  letter-spacing: 0.02em;
  line-height: 1.25;
  white-space: nowrap;
}

.article-row__chip--promo {
  background: linear-gradient(135deg, #fffbeb, #fef3c7);
  color: #b45309;
  border: 1px solid #fcd34d;
}

.article-row__chip--pin {
  background: linear-gradient(135deg, #fef2f2, #fee2e2);
  color: #b91c1c;
  border: 1px solid #fecaca;
}

.article-row__chip--kind {
  background: #f1f5f9;
  color: #64748b;
  border: 1px solid #e2e8f0;
}

.article-row__chip--orig {
  background: #eff6ff;
  color: #1d4ed8;
  border-color: #bfdbfe;
}

.article-row__chip--ext {
  background: #f5f3ff;
  color: #6d28d9;
  border-color: #ddd6fe;
}

/* 第二行 */
.article-row__body {
  display: flex;
  align-items: flex-start;
  gap: 12px;
  min-width: 0;
}

.article-row__media {
  flex: 0 0 auto;
  width: 88px;
  aspect-ratio: 1;
  border-radius: 10px;
  overflow: hidden;
  background: linear-gradient(145deg, #f1f5f9, #e8eef5);
  box-shadow: inset 0 0 0 1px rgba(15, 23, 42, 0.05);
}

.article-row--home .article-row__media {
  width: 72px;
  border-radius: 9px;
  background: linear-gradient(145deg, #faf5ff, #ede9fe);
  border: 1px solid #e9d5ff;
}

.article-row__img {
  width: 100%;
  height: 100%;
  display: block;
}

.article-row__img :deep(.el-image) {
  width: 100%;
  height: 100%;
  display: block;
}

.article-row__img :deep(.el-image__inner) {
  object-fit: cover;
}

.article-row__placeholder {
  width: 100%;
  height: 100%;
  display: flex;
  align-items: center;
  justify-content: center;
  overflow: hidden;
}

.article-row__summary {
  margin: 0;
  flex: 1 1 auto;
  min-width: 0;
  align-self: center;
  font-size: var(--fs-small);
  line-height: 1.55;
  color: #64748b;
  word-break: break-word;
  display: -webkit-box;
  -webkit-line-clamp: 3;
  line-clamp: 3;
  -webkit-box-orient: vertical;
  overflow: hidden;
}

.article-row--home .article-row__summary {
  font-size: var(--fs-caption);
  line-height: 1.5;
  -webkit-line-clamp: 2;
  line-clamp: 2;
}

.article-row__summary--empty {
  color: #94a3b8;
  font-style: italic;
}

/* 第三行 */
.article-row__meta {
  display: flex;
  align-items: center;
  flex-wrap: wrap;
  gap: 2px 4px;
  margin: 0;
  padding: 0;
  min-width: 0;
  border-top: 1px solid rgba(226, 232, 240, 0.85);
  padding-top: 8px;
}

.article-row--home .article-row__meta {
  border-top-color: rgba(233, 213, 255, 0.9);
  padding-top: 6px;
}

.article-row__meta-dot {
  color: #cbd5e1;
  font-weight: 700;
  user-select: none;
}

.article-row__time,
.article-row__reads,
.article-row__cat {
  font-size: var(--fs-caption);
  font-weight: 500;
  color: #94a3b8;
  font-variant-numeric: tabular-nums;
}

.article-row__cat {
  max-width: 12em;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

@media (max-width: 900px) {
  .article-row {
    gap: 8px;
    padding: 10px;
  }

  .article-row__head {
    flex-direction: column;
    align-items: stretch;
    gap: 6px;
  }

  .article-row__badges {
    max-width: none;
    justify-content: flex-start;
  }

  .article-row__title {
    font-size: var(--fs-body);
    -webkit-line-clamp: 2;
    line-clamp: 2;
  }

  .article-row--home .article-row__title {
    -webkit-line-clamp: 2;
    line-clamp: 2;
  }

  .article-row__media {
    width: 72px;
    border-radius: 9px;
  }

  .article-row--home .article-row__media {
    width: 64px;
  }

  .article-row__body {
    gap: 10px;
  }

  .article-row__summary {
    -webkit-line-clamp: 2;
    line-clamp: 2;
  }
}

@media (max-width: 480px) {
  .article-row__media {
    width: 64px;
  }

  .article-row--home .article-row__media {
    width: 56px;
  }
}
</style>
