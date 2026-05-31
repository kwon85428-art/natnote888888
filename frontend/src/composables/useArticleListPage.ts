import type { Component } from 'vue'
import { computed, nextTick, onMounted, ref, watch } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { Reading } from '@element-plus/icons-vue'
import { fetchArticleCategories, fetchArticlesPage } from '@/api/public'
import { getApiErrorMessage } from '@/api/errors'
import { usePublicSettings } from '@/composables/usePublicSettings'
import type { ArticleCategoryItem, ArticleSummary } from '@/types/models'
import { categoryIconComponent } from '@/utils/categoryIcons'
import { applyPublicSeo } from '@/utils/seo'
export const ARTICLE_LIST_PAGE_SIZE = 10

export type ArticleListCategory = ArticleCategoryItem

export function useArticleListPage() {
  const route = useRoute()
  const router = useRouter()
  const { menuLabels } = usePublicSettings()
  const menuArticlesLabel = computed(() => menuLabels.value.menu_articles_label)

  const categories = ref<ArticleListCategory[]>([])
  const list = ref<ArticleSummary[]>([])
  const total = ref(0)
  const filter = ref<string>('all')
  const drawerVisible = ref(false)
  const articleNavCollapsed = ref(false)

  const currentPage = computed(() => {
    const p = parseInt(String(route.query.page || '1'), 10)
    return Number.isFinite(p) && p >= 1 ? p : 1
  })

  function currentCategoryLabel() {
    if (filter.value === 'all') return '全部'
    const c = categories.value.find((x) => String(x.id) === filter.value)
    return c?.name ?? '全部'
  }

  function resolveCatIcon(c: { icon_key?: string | null }): Component {
    return categoryIconComponent(c.icon_key || undefined) || Reading
  }

  function catNavTitle(c: ArticleListCategory) {
    const desc = c.description?.trim()
    return desc ? `${c.name}\n${desc}` : c.name
  }

  function sortCategories(cats: ArticleListCategory[]) {
    return [...cats].sort((a, b) => (a.sort_order ?? 0) - (b.sort_order ?? 0) || a.id - b.id)
  }

  function scrollDockIntoView(dockScrollEl?: HTMLElement | null, catKey?: string) {
    nextTick(() => {
      const wrap = dockScrollEl
      if (!wrap) return
      const key = catKey ?? (filter.value === 'all' ? 'all' : filter.value)
      const btn = wrap.querySelector<HTMLElement>(`[data-article-cat="${key}"]`)
      btn?.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' })
    })
  }

  function scrollTabIntoView(tabScrollEl?: HTMLElement | null, catKey?: string) {
    nextTick(() => {
      const wrap = tabScrollEl
      if (!wrap) return
      const key = catKey ?? (filter.value === 'all' ? 'all' : filter.value)
      const btn = wrap.querySelector<HTMLElement>(`[data-article-tab="${key}"]`)
      btn?.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' })
    })
  }

  function scrollSidebarIntoView(catKey?: string) {
    nextTick(() => {
      const key = catKey ?? (filter.value === 'all' ? 'all' : filter.value)
      const btn = document.querySelector<HTMLElement>(
        `.article-page .left-nav [data-article-cat="${key}"]`,
      )
      btn?.scrollIntoView({ behavior: 'smooth', block: 'nearest' })
    })
  }

  function getScrollMain() {
    return document.querySelector<HTMLElement>('.article-page .split__main')
  }

  function scrollWithinMain(target: HTMLElement | null, offset = 0) {
    nextTick(() => {
      const main = getScrollMain()
      if (!target || !main) {
        window.scrollTo({ top: 0, behavior: 'smooth' })
        return
      }
      const mainRect = main.getBoundingClientRect()
      const targetRect = target.getBoundingClientRect()
      const top = targetRect.top - mainRect.top + main.scrollTop - offset
      main.scrollTo({ top: Math.max(0, top), behavior: 'smooth' })
    })
  }

  /** 切换分类时：定位到列表区（含标签栏） */
  function scrollToListSection() {
    scrollWithinMain(document.getElementById('article-list-panel'), 0)
  }

  /** 翻页时：定位到当前分类列表内容 */
  function scrollToTabPanel() {
    scrollWithinMain(document.querySelector<HTMLElement>('.article-tab-panel'), 4)
  }

  function toggleArticleNavCollapsed() {
    articleNavCollapsed.value = !articleNavCollapsed.value
    try {
      localStorage.setItem('article_cat_collapsed', articleNavCollapsed.value ? '1' : '0')
    } catch {
      /* ignore */
    }
  }

  async function load() {
    try {
      const cats = await fetchArticleCategories()
      categories.value = sortCategories(cats)
      filter.value = route.query.cid ? String(route.query.cid) : 'all'
      const cid = filter.value === 'all' ? undefined : Number(filter.value)
      let page = currentPage.value
      const data = await fetchArticlesPage({
        article_category_id: cid,
        page,
        page_size: ARTICLE_LIST_PAGE_SIZE,
      })
      const t = data?.total ?? 0
      const maxPage = Math.max(1, Math.ceil(t / ARTICLE_LIST_PAGE_SIZE))
      if (t > 0 && page > maxPage) {
        await router.replace({
          path: '/articles',
          query: {
            ...(filter.value !== 'all' ? { cid: filter.value } : {}),
            ...(maxPage > 1 ? { page: String(maxPage) } : {}),
          },
        })
        return
      }
      list.value = data?.items ?? []
      total.value = t
    } catch (e: unknown) {
      ElMessage.error(getApiErrorMessage(e, '加载失败'))
    }
  }

  function onFilterChange(
    val: string,
    opts?: {
      dockScrollEl?: HTMLElement | null
      tabScrollEl?: HTMLElement | null
    },
  ) {
    drawerVisible.value = false
    void router.push({ path: '/articles', query: val === 'all' ? {} : { cid: val } }).then(() => {
      scrollToListSection()
      scrollDockIntoView(opts?.dockScrollEl, val)
      scrollTabIntoView(opts?.tabScrollEl, val)
      scrollSidebarIntoView(val)
    })
  }

  function onPageChange(p: number) {
    const q: Record<string, string> = {}
    if (filter.value !== 'all') q.cid = filter.value
    if (p > 1) q.page = String(p)
    void router.push({ path: '/articles', query: q }).then(scrollToTabPanel)
  }

  function goDetail(id: number) {
    router.push(`/articles/${id}`)
  }

  function applyArticlePageSeo() {
    applyPublicSeo({
      title: menuArticlesLabel.value,
      description: '按主题浏览文章列表，支持分类筛选与分页。',
    })
  }

  onMounted(() => {
    try {
      articleNavCollapsed.value = localStorage.getItem('article_cat_collapsed') === '1'
    } catch {
      articleNavCollapsed.value = false
    }
    applyArticlePageSeo()
    void load()
  })

  watch(menuArticlesLabel, applyArticlePageSeo)

  watch(
    () => route.fullPath,
    () => load(),
  )

  return {
    menuArticlesLabel,
    categories,
    list,
    total,
    filter,
    drawerVisible,
    articleNavCollapsed,
    currentPage,
    pageSize: ARTICLE_LIST_PAGE_SIZE,
    currentCategoryLabel,
    resolveCatIcon,
    catNavTitle,
    onFilterChange,
    onPageChange,
    goDetail,
    load,
    toggleArticleNavCollapsed,
  }
}
