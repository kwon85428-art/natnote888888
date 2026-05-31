import { onMounted, reactive, ref } from 'vue'
import {
  checkAdminSite,
  checkAdminSitesBatch,
  createAdminSite,
  deleteAdminSite,
  fetchAdminSiteCategoriesAll,
  fetchAdminSitesPage,
  fetchSiteMeta,
  updateAdminSite,
  uploadAdminSiteLogo,
  uploadFaviconFromUrl,
  type SiteFetchMeta,
} from '@/api/admin/sites'
import { getApiErrorMessage } from '@/api/errors'
import { coerceBool } from '@/utils/boolDisplay'
import type { SiteCategoryItem, SiteItem } from '@/types/models'
export type SiteAdminForm = {
  id: number | null
  name: string
  url: string
  site_category_id: number | undefined
  tags: string[]
  description: string
  favicon_path: string
  logo_path: string
  is_valid: boolean
  invalid_note: string
  sort_order: number
  is_promoted: boolean
}

export function useSitesAdminPage() {
  const sites = ref<SiteItem[]>([])
  const siteCategories = ref<SiteCategoryItem[]>([])
  const q = ref('')
  const siteCategoryId = ref<number | undefined>(undefined)
  const page = ref(1)
  const pageSize = ref(20)
  const total = ref(0)
  const dialog = ref(false)
  const fetchDialog = ref(false)
  const fetchUrl = ref('')
  const fetchPreview = ref<SiteFetchMeta | null>(null)
  const form = reactive<SiteAdminForm>({
    id: null,
    name: '',
    url: '',
    site_category_id: undefined,
    tags: [],
    description: '',
    favicon_path: '',
    logo_path: '',
    is_valid: true,
    invalid_note: '',
    sort_order: 0,
    is_promoted: false,
  })
  const tagInput = ref('')
  const selection = ref<SiteItem[]>([])

  async function load(opts?: { resetPage?: boolean }) {
    if (opts?.resetPage) page.value = 1
    try {
      const [cats, block] = await Promise.all([
        fetchAdminSiteCategoriesAll(),
        fetchAdminSitesPage({
          q: q.value || undefined,
          site_category_id: siteCategoryId.value,
          page: page.value,
          page_size: pageSize.value,
        }),
      ])
      siteCategories.value = cats
      sites.value = block.items
      total.value = block.total
    } catch (e: unknown) {
      ElMessage.error(getApiErrorMessage(e, '加载失败'))
    }
  }

  function onPageSizeChange(s: number) {
    pageSize.value = s
    page.value = 1
    void load()
  }

  function openCreate() {
    Object.assign(form, {
      id: null,
      name: '',
      url: '',
      site_category_id: siteCategories.value.find((c) => !c.is_system)?.id,
      tags: [],
      description: '',
      favicon_path: '',
      logo_path: '',
      is_valid: true,
      invalid_note: '',
      sort_order: 0,
      is_promoted: false,
    })
    dialog.value = true
  }

  function openEdit(row: SiteItem) {
    Object.assign(form, {
      ...row,
      tags: row.tags || [],
      invalid_note: row.invalid_note || '',
      is_valid: coerceBool(row.is_valid),
      is_promoted: coerceBool(row.is_promoted),
    })
    dialog.value = true
  }

  async function save() {
    const payload = {
      name: form.name,
      url: form.url,
      site_category_id: form.site_category_id!,
      tags: form.tags,
      description: form.description,
      favicon_path: form.favicon_path || null,
      logo_path: form.logo_path || null,
      is_valid: form.is_valid,
      sort_order: form.sort_order,
      is_promoted: form.is_promoted,
    }
    try {
      if (form.id) {
        await updateAdminSite(form.id, {
          ...payload,
          invalid_note: form.is_valid ? null : form.invalid_note.trim() || null,
        })
      } else await createAdminSite(payload)
      ElMessage.success('已保存')
      dialog.value = false
      await load()
    } catch (e: unknown) {
      ElMessage.error(getApiErrorMessage(e, '保存失败'))
    }
  }

  async function removeRow(row: SiteItem) {
    await ElMessageBox.confirm('确定删除？', '提示')
    try {
      await deleteAdminSite(row.id)
      ElMessage.success('已删除')
      await load()
    } catch (e: unknown) {
      ElMessage.error(getApiErrorMessage(e, '删除失败'))
    }
  }

  function openFetch() {
    fetchUrl.value = form.url || ''
    fetchPreview.value = null
    fetchDialog.value = true
  }

  async function doFetchPreview() {
    try {
      const data = await fetchSiteMeta(fetchUrl.value)
      fetchPreview.value = data
      form.name = data.title
      form.url = data.resolved_url
      form.description = data.description || ''
      if (data.favicon_url) {
        form.favicon_path = await uploadFaviconFromUrl(data.favicon_url)
      }
    } catch (e: unknown) {
      ElMessage.error(getApiErrorMessage(e, '抓取失败'))
    }
  }

  function applyFetchToForm() {
    fetchDialog.value = false
  }

  async function uploadLogo(file: File) {
    try {
      form.logo_path = await uploadAdminSiteLogo(file)
      ElMessage.success('LOGO 已上传')
    } catch (e: unknown) {
      ElMessage.error(getApiErrorMessage(e, '上传失败'))
    }
  }

  async function checkOne(row: SiteItem) {
    try {
      const data = await checkAdminSite(row.id)
      ElMessage[data.ok ? 'success' : 'warning'](data.ok ? '可访问' : data.message || '不可访问')
      await load()
    } catch (e: unknown) {
      ElMessage.error(getApiErrorMessage(e, '校验失败'))
    }
  }

  async function checkBatch() {
    const ids = selection.value.map((r) => r.id)
    if (!ids.length) return
    try {
      const data = await checkAdminSitesBatch(ids)
      ElMessage.success(`批量校验完成：${data.length} 条`)
      await load()
    } catch (e: unknown) {
      ElMessage.error(getApiErrorMessage(e, '批量校验失败'))
    }
  }

  function addTag() {
    const v = tagInput.value.trim()
    if (!v) return
    if (!form.tags.includes(v)) form.tags.push(v)
    tagInput.value = ''
  }

  function removeTag(t: string) {
    form.tags = form.tags.filter((x) => x !== t)
  }

  function onSelectionChange(v: SiteItem[]) {
    selection.value = v
  }

  onMounted(() => {
    void load()
  })

  return {
    sites,
    siteCategories,
    q,
    siteCategoryId,
    page,
    pageSize,
    total,
    dialog,
    fetchDialog,
    fetchUrl,
    fetchPreview,
    form,
    tagInput,
    selection,
    load,
    onPageSizeChange,
    openCreate,
    openEdit,
    save,
    removeRow,
    openFetch,
    doFetchPreview,
    applyFetchToForm,
    uploadLogo,
    checkOne,
    checkBatch,
    addTag,
    removeTag,
    onSelectionChange,
  }
}
