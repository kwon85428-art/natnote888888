import { computed, onMounted, ref } from 'vue'
import { fetchPromotedArticles, fetchPromotedSites } from '@/api/public'
import { getApiErrorMessage } from '@/api/errors'
import { usePublicSettings } from '@/composables/usePublicSettings'
import type { ArticleSummary, SiteItem } from '@/types/models'

/** 文章页顶部的推广推荐区块（由平台设置控制） */
export function useArticlePagePromoted() {
  const { settings } = usePublicSettings()
  const promotedSites = ref<SiteItem[]>([])
  const promotedArticles = ref<ArticleSummary[]>([])
  const loadError = ref('')

  const showPromotedSites = computed(
    () =>
      settings.value.public_sites_enabled !== false &&
      settings.value.show_promoted_sites_on_articles !== false,
  )
  const showPromotedArticles = computed(
    () =>
      settings.value.public_articles_enabled !== false &&
      settings.value.show_promoted_articles_on_articles !== false,
  )

  const showAny = computed(
    () =>
      (showPromotedSites.value && promotedSites.value.length > 0) ||
      (showPromotedArticles.value && promotedArticles.value.length > 0),
  )

  async function load() {
    loadError.value = ''
    const tasks: Promise<void>[] = []
    if (showPromotedSites.value) {
      tasks.push(
        fetchPromotedSites(12).then((rows) => {
          promotedSites.value = rows
        }),
      )
    } else {
      promotedSites.value = []
    }
    if (showPromotedArticles.value) {
      tasks.push(
        fetchPromotedArticles(12).then((rows) => {
          promotedArticles.value = rows
        }),
      )
    } else {
      promotedArticles.value = []
    }
    try {
      await Promise.all(tasks)
    } catch (e) {
      loadError.value = getApiErrorMessage(e, '推荐内容加载失败')
    }
  }

  onMounted(() => {
    void load()
  })

  return {
    promotedSites,
    promotedArticles,
    showPromotedSites,
    showPromotedArticles,
    showAny,
    loadError,
  }
}
