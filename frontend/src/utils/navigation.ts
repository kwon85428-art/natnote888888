/** 校验站内 redirect 参数，防止开放重定向。 */
export function sanitizeInternalRedirect(raw: unknown, fallback = '/admin'): string {
  if (typeof raw !== 'string') return fallback
  const path = raw.trim()
  if (!path.startsWith('/') || path.startsWith('//')) return fallback
  return path
}
