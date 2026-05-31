import { reactive, ref } from 'vue'
import { getApiErrorMessage } from '@/api/errors'

export type CategoryCrudApi<TItem, TPayload> = {
  list: (params: { page: number; page_size: number }) => Promise<{ data: { items: TItem[]; total: number } }>
  create: (body: TPayload) => Promise<unknown>
  update: (id: number, body: TPayload) => Promise<unknown>
  remove: (id: number) => Promise<unknown>
}

export type UseAdminCategoryCrudOptions<TItem extends { id: number }, TPayload, TForm extends TPayload & { id: number | null }> = {
  api: CategoryCrudApi<TItem, TPayload>
  emptyForm: () => TForm
  formFromRow: (row: TItem) => TForm
  toPayload: (form: TForm) => TPayload
  deleteConfirm?: string
  successSaved?: string
  successDeleted?: string
}

export function useAdminCategoryCrud<TItem extends { id: number }, TPayload, TForm extends TPayload & { id: number | null }>(
  options: UseAdminCategoryCrudOptions<TItem, TPayload, TForm>,
) {
  const list = ref<TItem[]>([])
  const page = ref(1)
  const pageSize = ref(20)
  const total = ref(0)
  const dialog = ref(false)
  const saving = ref(false)
  const form = reactive(options.emptyForm()) as TForm

  async function load(opts?: { resetPage?: boolean }) {
    if (opts?.resetPage) page.value = 1
    const { data } = await options.api.list({ page: page.value, page_size: pageSize.value })
    list.value = data.items
    total.value = data.total
  }

  function openCreate() {
    Object.assign(form, options.emptyForm())
    dialog.value = true
  }

  function openEdit(row: TItem) {
    Object.assign(form, options.formFromRow(row))
    dialog.value = true
  }

  async function save() {
    saving.value = true
    try {
      const payload = options.toPayload(form)
      if (form.id) await options.api.update(form.id, payload)
      else await options.api.create(payload)
      ElMessage.success(options.successSaved ?? '已保存')
      dialog.value = false
      await load()
    } catch (e: unknown) {
      ElMessage.error(getApiErrorMessage(e, '保存失败'))
    } finally {
      saving.value = false
    }
  }

  async function removeRow(row: TItem) {
    try {
      await ElMessageBox.confirm(options.deleteConfirm ?? '确定删除？', '提示')
      await options.api.remove(row.id)
      ElMessage.success(options.successDeleted ?? '已删除')
      await load()
    } catch (e: unknown) {
      if (e !== 'cancel' && e !== 'close') {
        ElMessage.error(getApiErrorMessage(e, '删除失败'))
      }
    }
  }

  function onPageSizeChange(size: number) {
    pageSize.value = size
    page.value = 1
    void load()
  }

  return {
    list,
    page,
    pageSize,
    total,
    dialog,
    saving,
    form,
    load,
    openCreate,
    openEdit,
    save,
    removeRow,
    onPageSizeChange,
  }
}
