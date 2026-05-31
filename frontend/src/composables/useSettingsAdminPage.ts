import { onMounted, reactive } from 'vue'

import {

  fetchAdminPlatformSettings,

  updateAdminPlatformSettings,

  uploadAdminPlatformLogo,

} from '@/api/admin/settings'

import { getApiErrorMessage } from '@/api/errors'

import { dispatchPlatformSettingsUpdated } from '@/utils/platformSettingsEvents'

import { usePublicSettingsStore } from '@/stores/publicSettings'

import { syncSeoBrandFromSettings } from '@/utils/seo'



export function useSettingsAdminPage() {

  const platform = reactive({

    platform_name: '',

    footer_text: '',

    contact_info: '',

    icp_text: '',

    icp_link_url: '',

    logo_path: '',

    show_promoted_sites_on_sites: true,

    show_promoted_articles_on_sites: true,

    show_promoted_sites_on_articles: false,

    show_promoted_articles_on_articles: true,

    public_sites_enabled: true,

    public_articles_enabled: true,

    default_home: 'sites' as 'sites' | 'articles',

    menu_sites_label: '网址',

    menu_articles_label: '文章',

  })



  async function load() {

    const data = await fetchAdminPlatformSettings()

    const defaultHome = data.default_home === 'articles' ? 'articles' : 'sites'

    Object.assign(platform, data, { default_home: defaultHome })

  }



  async function savePlatform() {

    const menu_sites_label = String(platform.menu_sites_label ?? '').trim()

    const menu_articles_label = String(platform.menu_articles_label ?? '').trim()

    if (!menu_sites_label || !menu_articles_label) {

      ElMessage.warning('网址、文章菜单名称均不能为空')

      return

    }

    try {

      const saved = await updateAdminPlatformSettings({

        platform_name: platform.platform_name,

        footer_text: platform.footer_text,

        contact_info: platform.contact_info,

        icp_text: platform.icp_text,

        icp_link_url: platform.icp_link_url,

        show_promoted_sites_on_sites: platform.show_promoted_sites_on_sites,

        show_promoted_articles_on_sites: platform.show_promoted_articles_on_sites,

        show_promoted_sites_on_articles: platform.show_promoted_sites_on_articles,

        show_promoted_articles_on_articles: platform.show_promoted_articles_on_articles,

        public_sites_enabled: platform.public_sites_enabled,

        public_articles_enabled: platform.public_articles_enabled,

        default_home: platform.default_home,

        menu_sites_label,

        menu_articles_label,

      })

      const store = usePublicSettingsStore()
      store.apply(saved)
      syncSeoBrandFromSettings(saved)
      dispatchPlatformSettingsUpdated(saved)

      ElMessage.success('平台信息已保存')

    } catch (e: unknown) {

      ElMessage.error(getApiErrorMessage(e, '保存失败'))

    }

  }



  async function uploadLogo(file: File) {

    try {

      platform.logo_path = await uploadAdminPlatformLogo(file)

      const saved = await fetchAdminPlatformSettings()

      const store = usePublicSettingsStore()
      store.apply(saved)
      syncSeoBrandFromSettings(saved)
      dispatchPlatformSettingsUpdated(saved)

      ElMessage.success('Logo 已更新')

    } catch (e: unknown) {

      ElMessage.error(getApiErrorMessage(e, '上传失败'))

    }

  }



  onMounted(() => {

    void load()

  })



  return { platform, savePlatform, uploadLogo }

}


