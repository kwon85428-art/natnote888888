/** 将 API / 表格中的布尔值规范为 true/false（兼容 0/1、字符串等） */
export function coerceBool(value: unknown): boolean {
  if (value === true || value === 1) return true
  if (value === false || value === 0 || value === null || value === undefined) return false
  if (typeof value === 'string') {
    const s = value.trim().toLowerCase()
    if (s === 'true' || s === '1' || s === 'yes' || s === '是') return true
    if (s === 'false' || s === '0' || s === 'no' || s === '否' || s === '') return false
  }
  return Boolean(value)
}

export type BoolCellVariant = 'yesno' | 'valid' | 'pin' | 'promote'

type BoolCellTag = {
  text: string
  type: 'success' | 'warning' | 'danger' | 'info'
}

/** 后台表格布尔列：返回展示文案与 el-tag 类型 */
export function boolCellTag(variant: BoolCellVariant, value: unknown): BoolCellTag | null {
  const on = coerceBool(value)
  switch (variant) {
    case 'yesno':
      return on ? { text: '是', type: 'success' } : { text: '否', type: 'info' }
    case 'valid':
      return on ? { text: '有效', type: 'success' } : { text: '无效', type: 'danger' }
    case 'pin':
      return on ? { text: '置顶', type: 'danger' } : null
    case 'promote':
      return on ? { text: '推广', type: 'warning' } : null
    default:
      return null
  }
}
