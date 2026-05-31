import { computed, ref, watch } from 'vue'
import { storeToRefs } from 'pinia'
import { useRoute, useRouter } from 'vue-router'
import { usePublicSettingsStore } from '@/stores/publicSettings'
import { uploadUrl } from '@/utils/media'

const DEFAULT_LOGO = '/brand-logo.svg'

export function usePublicNav() {
  const router = useRouter()
  const route = useRoute()
  const store = usePublicSettingsStore()
  const { settings, menuLabels } = storeToRefs(store)

  const displayBrand = computed(
    () => String(settings.value.platform_name || '').trim() || 'NavNote',
  )
  const menuSitesLabel = computed(() => menuLabels.value.menu_sites_label)
  const menuArticlesLabel = computed(() => menuLabels.value.menu_articles_label)
  const showSitesNav = computed(() => settings.value.public_sites_enabled !== false)
  const showArticlesNav = computed(() => settings.value.public_articles_enabled !== false)

  const logoSrc = ref(DEFAULT_LOGO)
  watch(
    () => settings.value.logo_path,
    (path) => {
      logoSrc.value = path ? uploadUrl(path) : DEFAULT_LOGO
    },
    { immediate: true },
  )

  function onLogoError() {
    if (logoSrc.value !== DEFAULT_LOGO) logoSrc.value = DEFAULT_LOGO
  }

  const isSites = computed(() => route.path === '/sites')
  const isArticles = computed(() => route.path.startsWith('/articles'))

  function go(path: string) {
    router.push(path)
  }

  return {
    logoSrc,
    showSitesNav,
    showArticlesNav,
    menuSitesLabel,
    menuArticlesLabel,
    displayBrand,
    isSites,
    isArticles,
    onLogoError,
    go,
  }
}
