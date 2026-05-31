import { computed, ref, watch } from 'vue'
import { useRoute } from 'vue-router'
import axios from 'axios'
import { fetchArticleDetail, fetchArticleRead } from '@/api/public'
import { usePublicSettingsStore } from '@/stores/publicSettings'
import { applyPublicSeo, syncSeoBrandFromSettings } from '@/utils/seo'
import { ROUTE_ERROR_COPY, type RouteErrorKind } from '@/constants/routeErrors'
import { absoluteUploadUrl } from '@/utils/media'
import type { Article } from '@/types/models'
export function htmlHasContent(html: string) {
  return !!String(html || '')
    .replace(/<[^>]+>/g, '')
    .trim()
}

export function useArticleDetailPage() {
  const route = useRoute()
  const item = ref<Article | null>(null)
  const inlineHtml = ref('')
  const loading = ref(true)
  const loadError = ref<RouteErrorKind | null>(null)

  const showReadOriginalBtn = computed(() => {
    const it = item.value
    if (!it || it.content_type !== 'external') return false
    return !!String(it.source_url || '').trim()
  })

  /** 本站文章页链接（分享复制、二维码均使用） */
  const articlePageUrl = computed(() => {
    if (!item.value) return ''
    return `${window.location.origin}/articles/${item.value.id}`
  })

  const qrDialogVisible = ref(false)

  async function load() {
    loading.value = true
    loadError.value = null
    const id = Number(route.params.id)
    if (!Number.isFinite(id) || id < 1) {
      loadError.value = 'not-found'
      applyPublicSeo({
        title: ROUTE_ERROR_COPY['not-found'].title,
        description: ROUTE_ERROR_COPY['not-found'].message,
        noindex: true,
      })
      loading.value = false
      return
    }
    try {
      const data = await fetchArticleDetail(id)
      item.value = data
      const read = await fetchArticleRead(id)
      inlineHtml.value = read.mode === 'inline' ? read.body_html || '' : ''
      try {
        const st = await usePublicSettingsStore().loadFromApi()
        syncSeoBrandFromSettings(st as { platform_name?: string; logo_path?: string | null })
      } catch {
        syncSeoBrandFromSettings({ platform_name: 'NavNote' })
      }
      const sum = String(data.summary || '')
        .trim()
        .replace(/\s+/g, ' ')
      applyPublicSeo({
        title: String(data.title || '文章'),
        description: sum.slice(0, 180) || undefined,
        image: data.cover_path ? absoluteUploadUrl(data.cover_path) : undefined,
        ogType: 'article',
        publishedAt: data.published_at,
      })
    } catch (e: unknown) {
      item.value = null
      inlineHtml.value = ''
      if (axios.isAxiosError(e) && e.response?.status === 404) {
        loadError.value = 'not-found'
        applyPublicSeo({
          title: ROUTE_ERROR_COPY['not-found'].title,
          description: ROUTE_ERROR_COPY['not-found'].message,
          noindex: true,
        })
      } else {
        ElMessage.error('加载文章失败，请稍后重试')
      }
    } finally {
      loading.value = false
    }
  }

  watch(
    () => route.params.id,
    () => {
      void load()
    },
    { immediate: true },
  )

  function openOriginalLink() {
    if (!item.value) return
    const u = String(item.value.source_url || '').trim()
    if (u) window.open(u, '_blank', 'noopener,noreferrer')
    else ElMessage.error('未配置原文链接')
  }

  async function copyShare() {
    const text = `${item.value?.title || ''} ${articlePageUrl.value}`.trim()
    try {
      await navigator.clipboard.writeText(text)
      ElMessage.success('已复制标题与链接')
    } catch {
      ElMessage.error('复制失败')
    }
  }

  function openArticleQr() {
    if (!articlePageUrl.value) return
    qrDialogVisible.value = true
  }

  return {
    item,
    inlineHtml,
    loading,
    loadError,
    showReadOriginalBtn,
    articlePageUrl,
    qrDialogVisible,
    openOriginalLink,
    copyShare,
    openArticleQr,
    htmlHasContent,
  }
}
