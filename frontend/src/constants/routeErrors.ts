/** 路由 / 页面级错误类型 */
export type RouteErrorKind = 'not-found' | 'forbidden'

export type RouteErrorCopy = {
  title: string
  message: string
  code: string
}

export const ROUTE_ERROR_COPY: Record<RouteErrorKind, RouteErrorCopy> = {
  'not-found': {
    code: '404',
    title: '页面不存在',
    message: '您访问的链接可能已失效、已被移除，或地址输入有误。',
  },
  forbidden: {
    code: '403',
    title: '暂无访问权限',
    message: '您没有权限查看该页面。如需访问管理功能，请先登录管理员账号。',
  },
}

/** 平台模块关闭等场景 */
export const ROUTE_ERROR_MODULE_DISABLED: RouteErrorCopy = {
  code: '403',
  title: '暂无访问权限',
  message: '该功能模块暂未对外开放，请稍后再试或联系管理员。',
}

export function seoCopyForRouteError(
  kind: RouteErrorKind,
  reason?: string | null | unknown,
): RouteErrorCopy {
  if (reason === 'module-disabled') return ROUTE_ERROR_MODULE_DISABLED
  return ROUTE_ERROR_COPY[kind]
}
