<script setup lang="ts">
import { Share } from '@element-plus/icons-vue'
import { formatZhDateTime } from '@/utils/datetime'
import { articleContentTypeLabel } from '@/utils/text'
import type { Article } from '@/types/models'

defineProps<{
  item: Article
  inlineHtml: string
  showReadOriginalBtn: boolean
  htmlHasContent: (html: string) => boolean
}>()

const emit = defineEmits<{
  openOriginal: []
  copyShare: []
  showQr: []
}>()
</script>

<template>
  <article class="article-detail__card">
    <div class="article-detail__body">
      <header class="article-detail__header">
        <div class="article-detail__badges">
          <span v-if="item.is_promoted" class="article-detail__badge article-detail__badge--promo">推广</span>
          <span v-if="item.is_pinned" class="article-detail__badge article-detail__badge--pin">置顶</span>
          <span
            class="article-detail__badge article-detail__badge--type"
            :class="item.content_type === 'original' ? 'article-detail__badge--orig' : ''"
            >{{ articleContentTypeLabel(item) }}</span
          >
        </div>
        <h1 class="article-detail__title">{{ item.title }}</h1>
        <div class="article-detail__meta-row">
          <div class="article-detail__meta">
            <time :datetime="item.published_at">{{
              formatZhDateTime(item.published_at, 'detail')
            }}</time>
            <span class="article-detail__meta-dot" aria-hidden="true">·</span>
            <span>阅读 {{ item.visit_count ?? 0 }}</span>
          </div>
          <el-dropdown trigger="click" placement="bottom-end" :teleported="true">
            <button type="button" class="article-detail__share-trigger" aria-label="分享本文">
              <el-icon aria-hidden="true"><Share /></el-icon>
              <span>分享</span>
            </button>
            <template #dropdown>
              <el-dropdown-menu>
                <el-dropdown-item @click="emit('copyShare')">复制标题与链接</el-dropdown-item>
                <el-dropdown-item @click="emit('showQr')">生成文章二维码</el-dropdown-item>
              </el-dropdown-menu>
            </template>
          </el-dropdown>
        </div>
      </header>

      <div v-if="item.summary" class="article-detail__lead">
        <span class="article-detail__lead-label">摘要</span>
        <p class="article-detail__lead-text">{{ item.summary }}</p>
      </div>

      <div v-if="showReadOriginalBtn" class="article-detail__original-cta">
        <el-button type="primary" size="large" round @click="emit('openOriginal')">
          阅读原文
        </el-button>
      </div>

      <p v-if="item.content_type === 'original' && !htmlHasContent(inlineHtml)" class="article-detail__empty">
        正文暂不可用，请稍后再试或联系站点管理员。
      </p>

      <div
        v-if="item.content_type === 'original' && htmlHasContent(inlineHtml)"
        id="article-body"
        class="article-detail__content"
        v-html="inlineHtml"
      />
    </div>
  </article>
</template>
