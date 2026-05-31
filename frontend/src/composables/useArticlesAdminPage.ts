import { onMounted, reactive, ref } from 'vue'
import {
  createAdminArticle,
  deleteAdminArticle,
  fetchAdminArticleCategoriesAll,
  fetchAdminArticlesPage,
  updateAdminArticle,
  uploadAdminArticleBodyImage,
  uploadAdminArticleCover,
} from '@/api/admin/articles'
import { getApiErrorMessage } from '@/api/errors'
import type { Article, ArticleCategoryItem } from '@/types/models'
import { coerceBool } from '@/utils/boolDisplay'
import { uploadUrl } from '@/utils/media'
export type ArticleAdminForm = {
  id: number | null
  title: string
  summary: string
  article_category_id: number | undefined
  tags: string[]
  published_at: string
  cover_path: string
  source_url: string
  content_type: string
  body_markdown: string
  is_pinned: boolean
  pin_order: number
  is_promoted: boolean
}

export function useArticlesAdminPage() {
  const list = ref<Article[]>([])
  const cats = ref<ArticleCategoryItem[]>([])
  const dialog = ref(false)
  const q = ref('')
  const filterCat = ref<number | undefined>(undefined)
  const filterType = ref<string | undefined>(undefined)
  const page = ref(1)
  const pageSize = ref(20)
  const total = ref(0)

  const form = reactive<ArticleAdminForm>({
    id: null,
    title: '',
    summary: '',
    article_category_id: undefined,
    tags: [],
    published_at: new Date().toISOString().slice(0, 19).replace('T', ' '),
    cover_path: '',
    source_url: '',
    content_type: 'external',
    body_markdown: '',
    is_pinned: false,
    pin_order: 0,
    is_promoted: false,
  })
  const tagInput = ref('')

  async function load(opts?: { resetPage?: boolean }) {
    if (opts?.resetPage) page.value = 1
    try {
      const [block, categories] = await Promise.all([
        fetchAdminArticlesPage({
          q: q.value || undefined,
          article_category_id: filterCat.value,
          content_type: filterType.value,
          page: page.value,
          page_size: pageSize.value,
        }),
        fetchAdminArticleCategoriesAll(),
      ])
      list.value = block.items
      total.value = block.total
      cats.value = [...categories].sort(
        (a, b) => (a.sort_order ?? 0) - (b.sort_order ?? 0) || a.id - b.id,
      )
    } catch (e: unknown) {
      ElMessage.error(getApiErrorMessage(e, '加载失败'))
    }
  }

  function openCreate() {
    Object.assign(form, {
      id: null,
      title: '',
      summary: '',
      article_category_id: cats.value[0]?.id,
      tags: [],
      published_at: new Date().toISOString().slice(0, 19).replace('T', ' '),
      cover_path: '',
      source_url: '',
      content_type: 'external',
      body_markdown: '',
      is_pinned: false,
      pin_order: 0,
      is_promoted: false,
    })
    dialog.value = true
  }

  function openEdit(row: Article) {
    Object.assign(form, {
      id: row.id,
      title: row.title,
      summary: row.summary ?? '',
      article_category_id: row.article_category_id,
      tags: row.tags || [],
      published_at: String(row.published_at).replace('T', ' ').slice(0, 19),
      cover_path: row.cover_path ?? '',
      source_url: row.source_url ?? '',
      content_type: row.content_type,
      body_markdown: row.body_markdown ?? '',
      is_pinned: coerceBool(row.is_pinned),
      pin_order: row.pin_order ?? 0,
      is_promoted: coerceBool(row.is_promoted),
    })
    dialog.value = true
  }

  async function save() {
    const pd = String(form.published_at).trim()
    const isoSource = pd.includes('T') ? pd : pd.replace(' ', 'T')
    const published_at = new Date(isoSource)
    const isOriginal = form.content_type === 'original'
    const payload = {
      title: form.title,
      summary: form.summary,
      article_category_id: form.article_category_id!,
      tags: form.tags,
      published_at: published_at.toISOString(),
      cover_path: form.cover_path || null,
      source_url: form.source_url || null,
      content_type: form.content_type,
      is_pinned: form.is_pinned,
      pin_order: form.pin_order,
      is_promoted: form.is_promoted,
      body_markdown: isOriginal ? form.body_markdown?.trim() || null : null,
      body_html: null as string | null,
    }
    try {
      if (form.id) await updateAdminArticle(form.id, payload)
      else await createAdminArticle(payload)
      ElMessage.success('已保存')
      dialog.value = false
      await load()
    } catch (e: unknown) {
      ElMessage.error(getApiErrorMessage(e, '保存失败'))
    }
  }

  async function removeRow(row: Article) {
    await ElMessageBox.confirm('确定删除？', '提示')
    try {
      await deleteAdminArticle(row.id)
      ElMessage.success('已删除')
      await load()
    } catch (e: unknown) {
      ElMessage.error(getApiErrorMessage(e, '删除失败'))
    }
  }

  function onPageSizeChange(s: number) {
    pageSize.value = s
    page.value = 1
    void load()
  }

  async function uploadCover(file: File) {
    try {
      form.cover_path = await uploadAdminArticleCover(file)
      ElMessage.success('封面上传成功')
    } catch (e: unknown) {
      ElMessage.error(getApiErrorMessage(e, '上传失败'))
    }
  }

  async function onUploadImg(files: File[], callback: (urls: string[]) => void) {
    try {
      const urls = await Promise.all(
        files.map(async (file) => {
          const path = await uploadAdminArticleBodyImage(file)
          return uploadUrl(path)
        }),
      )
      callback(urls)
      if (urls.length) {
        ElMessage.success(urls.length > 1 ? `已上传 ${urls.length} 张图片` : '图片已插入')
      }
    } catch {
      ElMessage.error('图片上传失败')
      callback([])
    }
  }

  function addTag() {
    const v = tagInput.value.trim()
    if (!v) return
    if (!form.tags.includes(v)) form.tags.push(v)
    tagInput.value = ''
  }

  onMounted(() => {
    void load()
  })

  return {
    list,
    cats,
    dialog,
    q,
    filterCat,
    filterType,
    page,
    pageSize,
    total,
    form,
    tagInput,
    load,
    openCreate,
    openEdit,
    save,
    removeRow,
    onPageSizeChange,
    uploadCover,
    onUploadImg,
    addTag,
  }
}
