/** 中文环境下文章/列表常用时间展示，避免各页重复 toLocaleString 配置 */

export type ZhDatePreset = 'list' | 'detail'

const PRESETS: Record<ZhDatePreset, Intl.DateTimeFormatOptions> = {
  list: {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  },
  detail: {
    year: 'numeric',
    month: 'long',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit',
  },
}

export function formatZhDateTime(iso: string | null | undefined, preset: ZhDatePreset = 'list'): string {
  if (iso == null || iso === '') return ''
  try {
    return new Date(iso).toLocaleString('zh-CN', PRESETS[preset])
  } catch {
    return ''
  }
}
