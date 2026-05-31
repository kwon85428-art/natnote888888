<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import ArticleDetailBody from '@/components/article/ArticleDetailBody.vue'
import ArticleQrDialog from '@/components/article/ArticleQrDialog.vue'
import AppErrorPanel from '@/components/AppErrorPanel.vue'
import PublicNav from '@/components/PublicNav.vue'
import PlatformFooter from '@/components/PlatformFooter.vue'
import { useArticleDetailPage } from '@/composables/useArticleDetailPage'
import { ROUTE_ERROR_COPY } from '@/constants/routeErrors'
import '@/styles/article/detail.css'

const router = useRouter()
const {
  item,
  inlineHtml,
  loading,
  loadError,
  showReadOriginalBtn,
  openOriginalLink,
  copyShare,
  openArticleQr,
  articlePageUrl,
  qrDialogVisible,
  htmlHasContent,
} = useArticleDetailPage()

const errorCopy = computed(() => (loadError.value ? ROUTE_ERROR_COPY[loadError.value] : null))
</script>

<template>
  <PublicNav />

  <div class="public-main-shell article-detail-shell" v-loading="loading">
    <div v-if="loadError && errorCopy" class="article-detail__max article-detail__error">
      <AppErrorPanel :kind="loadError" :copy="errorCopy" compact />
    </div>

    <div v-else-if="item" class="article-detail__max">
      <button type="button" class="article-detail__back" @click="router.push('/articles')">
        <span class="article-detail__back-icon" aria-hidden="true">←</span>
        返回列表
      </button>

      <ArticleDetailBody
        :item="item"
        :inline-html="inlineHtml"
        :show-read-original-btn="showReadOriginalBtn"
        :html-has-content="htmlHasContent"
        @open-original="openOriginalLink"
        @copy-share="copyShare"
        @show-qr="openArticleQr"
      />

      <ArticleQrDialog
        v-model:visible="qrDialogVisible"
        :url="articlePageUrl"
        :title="item.title"
      />
    </div>
  </div>

  <PlatformFooter />
</template>

<style scoped>
.article-detail__error {
  padding: 24px 0 32px;
}
</style>
