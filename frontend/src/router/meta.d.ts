import type { RouteErrorKind } from '@/constants/routeErrors'

declare module 'vue-router' {
  interface RouteMeta {
    requiresAuth?: boolean
    errorKind?: RouteErrorKind
    skipDefaultSeo?: boolean
    seo?: {
      title?: string
      description?: string
    }
  }
}

export {}
