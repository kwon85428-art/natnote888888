import type { Component } from 'vue'

import { nextTick, onMounted, onUnmounted, reactive, ref } from 'vue'

import { Compass } from '@element-plus/icons-vue'

import { fetchPublicHome, trackSiteVisit } from '@/api/public'

import { getApiErrorMessage } from '@/api/errors'

import type { ArticleSummary, PlatformSettings, PublicHomePack, SiteItem } from '@/types/models'

import { categoryIconComponent } from '@/utils/categoryIcons'
import { pickMenuLabels } from '@/utils/menuLabels'
import { PLATFORM_SETTINGS_UPDATED } from '@/utils/platformSettingsEvents'

import { usePublicSettingsStore } from '@/stores/publicSettings'

import { applyPublicSeo, syncSeoBrandFromSettings } from '@/utils/seo'



export type SiteCategoryRow = {

  id: number

  name: string

  description?: string

  icon_key?: string | null

}



/** 页脚预取字段，与 PlatformFooter prefetch 一致 */

export type PlatformFooterPrefetch = {

  footer_text?: string | null

  contact_info?: string | null

  icp_text?: string | null

  icp_link_url?: string | null

}



export function useSitesHomePage() {

  const title = ref('NavNote')

  const platformBundle = ref<PlatformFooterPrefetch | null>(null)



  const siteCategories = ref<SiteCategoryRow[]>([])

  const sitesByCategory = reactive<Record<number, SiteItem[]>>({})

  const promotedSites = ref<SiteItem[]>([])

  const promotedArticles = ref<ArticleSummary[]>([])



  const showPromotedSites = ref(true)

  const showPromotedArticles = ref(true)



  const loading = ref(true)

  const loadError = ref('')

  const activeSiteCatId = ref<number | null>(null)

  const siteNavCollapsed = ref(false)

  const catDrawerVisible = ref(false)



  function resolveCatIcon(key?: string | null): Component {

    return categoryIconComponent(key || undefined) || Compass

  }



  function currentSiteCategoryName() {

    const id = activeSiteCatId.value

    if (id == null) return ''

    return siteCategories.value.find((c) => c.id === id)?.name ?? ''

  }



  function siteCatNavTitle(c: { name: string; description?: string | null }) {

    const desc = c.description?.trim()

    return desc ? `${c.name}\n${desc}` : c.name

  }



  function scrollToSiteCategory(catId: number, dockScrollEl?: HTMLElement | null) {

    activeSiteCatId.value = catId

    requestAnimationFrame(() => {

      document.getElementById(`site-cat-${catId}`)?.scrollIntoView({ behavior: 'smooth', block: 'start' })

    })

    nextTick(() => {

      const wrap = dockScrollEl

      if (!wrap) return

      const btn = wrap.querySelector<HTMLElement>(`[data-site-cat="${catId}"]`)

      btn?.scrollIntoView({ behavior: 'smooth', inline: 'center', block: 'nearest' })

    })

  }



  function selectCatFromDrawer(c: { id: number }, dockScrollEl?: HTMLElement | null) {

    scrollToSiteCategory(c.id, dockScrollEl)

    catDrawerVisible.value = false

  }



  function toggleSiteNavCollapsed() {

    siteNavCollapsed.value = !siteNavCollapsed.value

    try {

      localStorage.setItem('home_site_cat_collapsed', siteNavCollapsed.value ? '1' : '0')

    } catch {

      /* ignore */

    }

  }



  async function openSite(site: { id: number; url: string }) {

    try {

      await trackSiteVisit(site.id)

    } catch {

      /* 统计失败不影响打开 */

    }

  }



  function applySettingsFlags(settings: PlatformSettings) {

    showPromotedSites.value =

      settings.public_sites_enabled !== false && settings.show_promoted_sites_on_sites !== false

    showPromotedArticles.value =

      settings.public_articles_enabled !== false && settings.show_promoted_articles_on_sites !== false

  }



  function applyHomePack(pack: PublicHomePack) {

    usePublicSettingsStore().apply(pack.settings)

    applySettingsFlags(pack.settings || {})

    title.value = pack.settings?.platform_name || title.value

    syncSeoBrandFromSettings(pack.settings || {})

    const menu = pickMenuLabels((pack.settings || {}) as Record<string, unknown>)
    applyPublicSeo({
      title: menu.menu_sites_label,
      description: '按分类浏览收录站点，查看推广推荐网址与文章。',
    })

    platformBundle.value = {

      footer_text: pack.settings?.footer_text,

      contact_info: pack.settings?.contact_info,

      icp_text: pack.settings?.icp_text,

      icp_link_url: pack.settings?.icp_link_url,

    }



    siteCategories.value = pack.site_categories || []

    const sbc = pack.sites_by_category || {}

    for (const c of siteCategories.value) {

      sitesByCategory[c.id] = sbc[String(c.id)] ?? []

    }



    promotedSites.value = showPromotedSites.value ? pack.promoted_sites || [] : []

    promotedArticles.value = showPromotedArticles.value ? pack.promoted_articles || [] : []

    activeSiteCatId.value = siteCategories.value[0]?.id ?? null

  }



  async function reloadHome() {

    try {

      const pack = await fetchPublicHome()

      applyHomePack(pack)

    } catch {

      /* 设置变更后静默失败，保留当前列表 */

    }

  }



  function onPlatformSettingsUpdated(ev: Event) {
    const detail = (ev as CustomEvent<PlatformSettings>).detail
    if (detail) {
      title.value = detail.platform_name || title.value
      platformBundle.value = {
        ...platformBundle.value,
        footer_text: detail.footer_text,
        contact_info: detail.contact_info,
        icp_text: detail.icp_text,
        icp_link_url: detail.icp_link_url,
      }
      applySettingsFlags(detail)
    }
    void reloadHome()
  }



  onMounted(async () => {

    window.addEventListener(PLATFORM_SETTINGS_UPDATED, onPlatformSettingsUpdated)

    loading.value = true

    loadError.value = ''

    try {

      const pack = await fetchPublicHome()

      applyHomePack(pack)

      try {

        siteNavCollapsed.value = localStorage.getItem('home_site_cat_collapsed') === '1'

      } catch {

        siteNavCollapsed.value = false

      }

    } catch (e) {

      loadError.value = getApiErrorMessage(e, '首页数据加载失败')

    } finally {

      loading.value = false

    }

  })



  onUnmounted(() => {

    window.removeEventListener(PLATFORM_SETTINGS_UPDATED, onPlatformSettingsUpdated)

  })



  return {

    title,

    platformBundle,

    siteCategories,

    sitesByCategory,

    promotedSites,

    promotedArticles,

    showPromotedSites,

    showPromotedArticles,

    loading,

    loadError,

    activeSiteCatId,

    siteNavCollapsed,

    catDrawerVisible,

    resolveCatIcon,

    currentSiteCategoryName,

    siteCatNavTitle,

    scrollToSiteCategory,

    selectCatFromDrawer,

    toggleSiteNavCollapsed,

    openSite,

  }

}


