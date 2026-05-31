import { absoluteAssetUrl, absoluteUploadUrl } from '@/utils/media'

const DEFAULT_DESC =
  'NavNote：网址导航与文章阅读，收录优质站点，支持分类浏览与文章详情。'

const FALLBACK_OG_IMAGE_PATH = '/brand-logo.svg'

let siteBrand = 'NavNote'
let defaultOgImage = ''

/** 与顶栏品牌同步，用于 title 后缀与 Open Graph */
export function setSeoSiteBrand(name: string) {
  siteBrand = (name && name.trim()) || 'NavNote'
}

/** 全站默认分享图（绝对 URL），通常为平台 Logo */
export function setSeoDefaultImage(url: string | null | undefined) {
  defaultOgImage = (url && url.trim()) || ''
}

export function syncSeoBrandFromSettings(settings: {
  platform_name?: string | null
  logo_path?: string | null
}) {
  setSeoSiteBrand(String(settings.platform_name || 'NavNote'))
  const logo = settings.logo_path ? absoluteUploadUrl(settings.logo_path) : ''
  setSeoDefaultImage(logo || absoluteAssetUrl(FALLBACK_OG_IMAGE_PATH))
  syncSiteFaviconFromSettings(settings)
}

function upsertMeta(attrName: 'name' | 'property', key: string, content: string) {
  const sel = `meta[${attrName}="${key}"]`
  let el = document.head.querySelector(sel) as HTMLMetaElement | null
  if (!el) {
    el = document.createElement('meta')
    el.setAttribute(attrName, key)
    document.head.appendChild(el)
  }
  el.setAttribute('content', content)
}

function removeMeta(attrName: 'name' | 'property', key: string) {
  document.head.querySelector(`meta[${attrName}="${key}"]`)?.remove()
}

function upsertLink(rel: string, href: string, attrs?: Record<string, string>) {
  const id = attrs?.id
  let el = (id ? document.getElementById(id) : null) as HTMLLinkElement | null
  if (!el) {
    const sel = id ? null : `link[rel="${rel}"]`
    el = (sel ? document.head.querySelector(sel) : null) as HTMLLinkElement | null
  }
  if (!el) {
    el = document.createElement('link')
    el.rel = rel
    if (id) el.id = id
    document.head.appendChild(el)
  }
  el.href = href
  if (attrs) {
    for (const [k, v] of Object.entries(attrs)) {
      if (k === 'id') continue
      if (v) el.setAttribute(k, v)
      else el.removeAttribute(k)
    }
  }
}

const FAVICON_PRIMARY_ID = 'navnote-favicon-primary'
const APPLE_TOUCH_ICON_ID = 'navnote-apple-touch-icon'

/** 同步浏览器标签页图标：有平台 Logo 时用 Logo，否则用内置 favicon */
export function syncSiteFaviconFromSettings(settings: { logo_path?: string | null }) {
  const logoPath = settings.logo_path?.trim()
  if (logoPath) {
    const url = absoluteUploadUrl(logoPath)
    const ext = logoPath.split('.').pop()?.toLowerCase()
    const type =
      ext === 'svg'
        ? 'image/svg+xml'
        : ext === 'png'
          ? 'image/png'
          : ext === 'jpg' || ext === 'jpeg'
            ? 'image/jpeg'
            : ext === 'webp'
              ? 'image/webp'
              : undefined
    upsertLink('icon', url, { id: FAVICON_PRIMARY_ID, ...(type ? { type } : {}) })
  } else {
    upsertLink('icon', absoluteAssetUrl('/favicon.svg'), {
      id: FAVICON_PRIMARY_ID,
      type: 'image/svg+xml',
    })
  }
  const appleHref = logoPath ? absoluteUploadUrl(logoPath) : absoluteAssetUrl('/brand-logo.svg')
  upsertLink('apple-touch-icon', appleHref, { id: APPLE_TOUCH_ICON_ID })
}

export type PublicSeoOptions = {
  title?: string
  description?: string
  noindex?: boolean
  /** 为 true 时 `title` 作为完整 document.title，不再拼接站点名 */
  rawTitle?: boolean
  /** 分享图绝对 URL；缺省使用平台默认图 */
  image?: string | null
  ogType?: 'website' | 'article'
  publishedAt?: string | null
}

/**
 * 前台 SPA 的轻量 SEO：title、description、canonical、Open Graph、Twitter Card。
 */
export function applyPublicSeo(opts: PublicSeoOptions = {}) {
  let fullTitle = siteBrand
  if (opts.title?.trim()) {
    fullTitle = opts.rawTitle ? opts.title.trim() : `${opts.title.trim()} | ${siteBrand}`
  }
  document.title = fullTitle

  const desc = (opts.description && opts.description.trim()) || DEFAULT_DESC
  upsertMeta('name', 'description', desc.slice(0, 320))
  upsertMeta('property', 'og:title', fullTitle.slice(0, 200))
  upsertMeta('property', 'og:description', desc.slice(0, 300))
  upsertMeta('property', 'og:site_name', siteBrand.slice(0, 120))

  const ogType = opts.ogType || 'website'
  upsertMeta('property', 'og:type', ogType)
  if (ogType === 'article' && opts.publishedAt) {
    upsertMeta('property', 'article:published_time', opts.publishedAt)
  } else {
    removeMeta('property', 'article:published_time')
  }

  const image = (opts.image && opts.image.trim()) || defaultOgImage || absoluteAssetUrl(FALLBACK_OG_IMAGE_PATH)
  upsertMeta('property', 'og:image', image)
  upsertMeta('name', 'twitter:card', 'summary_large_image')
  upsertMeta('name', 'twitter:title', fullTitle.slice(0, 200))
  upsertMeta('name', 'twitter:description', desc.slice(0, 300))
  upsertMeta('name', 'twitter:image', image)

  const origin = typeof window !== 'undefined' ? window.location.origin : ''
  const path = typeof window !== 'undefined' ? window.location.pathname + window.location.search : ''
  if (origin) {
    upsertMeta('property', 'og:url', `${origin}${path}`)
    upsertLink('canonical', `${origin}${path}`)
  }

  upsertMeta('name', 'robots', opts.noindex ? 'noindex,nofollow' : 'index,follow')
}

export function applyAdminSeo(page?: string) {
  const t = page?.trim() ? `${page.trim()} · 管理` : '管理后台'
  document.title = `${t} | ${siteBrand}`
  upsertMeta('name', 'robots', 'noindex,nofollow')
  upsertMeta('name', 'description', '站内管理页面，不参与公开检索。')
}
