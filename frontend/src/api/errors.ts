import axios from 'axios'

/** 解析后端统一格式 { detail: string | ValidationError[] } */
export function getApiErrorMessage(err: unknown, fallback = '请求失败'): string {
  if (!axios.isAxiosError(err)) {
    return err instanceof Error ? err.message : fallback
  }
  if (!err.response) {
    if (err.code === 'ECONNABORTED') return '请求超时，请检查网络或后端服务'
    return '无法连接服务器，请确认后端已启动'
  }
  const detail = err.response.data?.detail
  if (typeof detail === 'string' && detail.trim()) return detail
  if (Array.isArray(detail)) {
    const parts = detail
      .map((item) => {
        if (item && typeof item === 'object' && 'msg' in item) {
          return String((item as { msg?: string }).msg ?? '')
        }
        return ''
      })
      .filter(Boolean)
    if (parts.length) return parts.join('；')
  }
  return fallback
}
