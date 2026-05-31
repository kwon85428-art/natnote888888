export function uploadUrl(path: string | null | undefined): string {
  if (!path) return ''
  if (path.startsWith('http')) return path
  return `/uploads/${path.replace(/^\/+/, '').replace(/^uploads\/?/, '')}`
}

export function absoluteAssetUrl(path: string): string {
  const p = path.startsWith('/') ? path : `/${path}`
  if (typeof window === 'undefined') return p
  return `${window.location.origin}${p}`
}

/** 将 uploads 路径转为当前站点绝对 URL */
export function absoluteUploadUrl(path: string | null | undefined): string {
  const rel = uploadUrl(path)
  if (!rel) return ''
  return absoluteAssetUrl(rel)
}
