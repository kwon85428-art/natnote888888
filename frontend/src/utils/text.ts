/** 折叠摘要等字段中的连续空白 */
export function collapseWhitespace(value: string | null | undefined): string {
  return String(value ?? '')
    .trim()
    .replace(/\s+/g, ' ')
}

/** 文章列表/卡片展示用摘要（勿将整个 article 对象传入 collapseWhitespace） */
export function articleSummaryText(article: { summary?: string | null }): string {
  return collapseWhitespace(article.summary)
}

/** 文章形式展示名（优先 API 下发的 content_type_label） */
export function articleContentTypeLabel(article: {
  content_type?: string
  content_type_label?: string | null
}): string {
  return article.content_type_label || (article.content_type === 'original' ? '原创' : '外链')
}
