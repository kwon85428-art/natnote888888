import { computed } from 'vue'
import { useRoute } from 'vue-router'
import {
  ROUTE_ERROR_COPY,
  ROUTE_ERROR_MODULE_DISABLED,
  type RouteErrorKind,
} from '@/constants/routeErrors'

export function useRouteErrorContent(
  fallbackKind: RouteErrorKind = 'not-found',
  overrideKind?: RouteErrorKind,
) {
  const route = useRoute()

  const kind = computed<RouteErrorKind>(() => {
    if (overrideKind === 'not-found' || overrideKind === 'forbidden') return overrideKind
    const meta = route.meta.errorKind as RouteErrorKind | undefined
    if (meta === 'not-found' || meta === 'forbidden') return meta
    return fallbackKind
  })

  const copy = computed(() => {
    if (route.query.reason === 'module-disabled') return ROUTE_ERROR_MODULE_DISABLED
    return ROUTE_ERROR_COPY[kind.value]
  })

  const redirectTarget = computed(() => {
    const r = route.query.redirect
    return typeof r === 'string' && r.startsWith('/') ? r : ''
  })

  return { kind, copy, redirectTarget }
}
