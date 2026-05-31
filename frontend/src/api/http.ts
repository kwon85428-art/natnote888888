import axios from 'axios'

/** 同源部署留空；前后端分域时在 .env 设置 VITE_API_BASE_URL */
const baseURL = (import.meta.env.VITE_API_BASE_URL ?? '').replace(/\/$/, '')

const http = axios.create({
  baseURL,
  timeout: 15000,
})

http.interceptors.request.use((config) => {
  const token = localStorage.getItem('admin_token')
  if (token) {
    config.headers = config.headers || {}
    config.headers.Authorization = `Bearer ${token}`
  }
  return config
})

http.interceptors.response.use(
  (r) => r,
  async (err) => {
    if (err.response?.status === 401) {
      localStorage.removeItem('admin_token')
      const path = window.location.pathname
      const isAdminAuthPage = path === '/admin/login'
      if (path.startsWith('/admin') && !isAdminAuthPage) {
        const { default: router } = await import('@/router')
        const redirect = path + window.location.search
        void router.replace({ name: 'error-forbidden', query: { redirect } })
      }
    }
    return Promise.reject(err)
  },
)

export default http
