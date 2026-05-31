import { createRouter, createWebHistory } from 'vue-router'
import { useAuthStore } from '../stores/auth'
import { peekPublicLayoutSettings, resolvePublicEntryPath } from '../utils/publicLayout'
import { usePublicSettingsStore } from '@/stores/publicSettings'
import { applyAdminSeo, applyPublicSeo } from '../utils/seo'
import { resolvePublicRouteSeo } from '@/utils/menuLabels'
import type { RouteErrorKind } from '@/constants/routeErrors'
import { seoCopyForRouteError } from '@/constants/routeErrors'

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
      path: '/',
      beforeEnter: () => {
        const p = resolvePublicEntryPath(peekPublicLayoutSettings())
        if (p !== '/') return { path: p, replace: true }
        return true
      },
      meta: {
        seo: {
          title: '首页',
          description: '网址导航与文章入口；若模块关闭将显示提示信息。',
        },
      },
      component: () => import('../views/PublicRootStub.vue'),
    },
    {
      path: '/sites',
      meta: {
        seo: {
          title: '网址',
          description: '按分类浏览收录站点与推荐网址。',
        },
      },
      component: () => import('../views/SitesHome.vue'),
    },
    {
      path: '/articles',
      meta: {
        seo: {
          title: '文章',
          description: '按主题浏览文章列表，支持分类筛选与分页。',
        },
      },
      component: () => import('../views/ArticleList.vue'),
    },
    {
      path: '/articles/:id',
      meta: {
        skipDefaultSeo: true,
      },
      component: () => import('../views/ArticleDetail.vue'),
    },
    {
      path: '/404',
      name: 'error-not-found',
      component: () => import('../views/PublicErrorView.vue'),
      meta: { errorKind: 'not-found' satisfies RouteErrorKind },
    },
    {
      path: '/403',
      name: 'error-forbidden',
      component: () => import('../views/PublicErrorView.vue'),
      meta: { errorKind: 'forbidden' satisfies RouteErrorKind },
    },
    { path: '/admin/login', component: () => import('../views/admin/Login.vue') },
    {
      path: '/admin',
      component: () => import('../views/admin/AdminLayout.vue'),
      meta: { requiresAuth: true },
      children: [
        { path: '', redirect: '/admin/sites' },
        { path: 'site-categories', component: () => import('../views/admin/SiteCategoriesAdmin.vue') },
        { path: 'sites', component: () => import('../views/admin/SitesAdmin.vue') },
        {
          path: 'article-categories',
          component: () => import('../views/admin/ArticleCategoriesAdmin.vue'),
        },
        { path: 'articles', component: () => import('../views/admin/ArticlesAdmin.vue') },
        { path: 'settings', component: () => import('../views/admin/SettingsAdmin.vue') },
        { path: 'stats', component: () => import('../views/admin/StatsAdmin.vue') },
        {
          path: ':pathMatch(.*)*',
          name: 'admin-not-found',
          component: () => import('../views/admin/AdminRouteError.vue'),
          meta: { errorKind: 'not-found' satisfies RouteErrorKind },
        },
      ],
    },
    {
      path: '/:pathMatch(.*)*',
      name: 'public-not-found',
      component: () => import('../views/PublicErrorView.vue'),
      meta: { errorKind: 'not-found' satisfies RouteErrorKind },
    },
  ],
})

router.beforeEach(async (to) => {
  const auth = useAuthStore()

  const isAdminAuthPage = to.path === '/admin/login'
  const isAdminArea = to.path.startsWith('/admin') && !isAdminAuthPage

  if (to.meta.requiresAuth || isAdminArea) {
    if (!auth.token) {
      return {
        name: 'error-forbidden',
        query: { redirect: to.fullPath },
        replace: true,
      }
    }
    if (!auth.username) await auth.fetchMe()
    if (!auth.username) {
      return {
        name: 'error-forbidden',
        query: { redirect: to.fullPath },
        replace: true,
      }
    }
  }

  if (to.path.startsWith('/admin')) return true

  const s = peekPublicLayoutSettings()
  const isArticlePath = to.path === '/articles' || to.path.startsWith('/articles/')
  if (isArticlePath && !s.public_articles_enabled) {
    return {
      name: 'error-forbidden',
      query: { reason: 'module-disabled', from: to.fullPath },
      replace: true,
    }
  }
  if (to.path === '/sites' && !s.public_sites_enabled) {
    return {
      name: 'error-forbidden',
      query: { reason: 'module-disabled', from: to.fullPath },
      replace: true,
    }
  }
  return true
})

router.afterEach((to) => {
  if (to.path.startsWith('/admin')) {
    applyAdminSeo()
    return
  }
  const store = usePublicSettingsStore()
  const cached = store.settings

  const errorKind = to.meta.errorKind
  if (errorKind === 'not-found' || errorKind === 'forbidden') {
    const copy = seoCopyForRouteError(errorKind, to.query.reason)
    applyPublicSeo({ title: copy.title, description: copy.message, noindex: true })
    return
  }

  if (to.meta.skipDefaultSeo) return

  const seo = to.meta.seo
  if (seo?.title || seo?.description) {
    const resolved = resolvePublicRouteSeo(to.path, cached, seo)
    applyPublicSeo({ title: resolved.title, description: resolved.description })
  } else {
    applyPublicSeo()
  }
})

export default router
