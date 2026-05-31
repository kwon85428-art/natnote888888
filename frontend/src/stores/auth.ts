import { defineStore } from 'pinia'
import { ref } from 'vue'
import http from '../api/http'

export const useAuthStore = defineStore('auth', () => {
  const token = ref<string | null>(localStorage.getItem('admin_token'))
  const username = ref<string>('')

  function setToken(t: string | null) {
    token.value = t
    if (t) localStorage.setItem('admin_token', t)
    else localStorage.removeItem('admin_token')
  }

  async function login(payload: {
    username: string
    password: string
    captcha_id: string
    captcha_code: string
  }) {
    const { data } = await http.post('/api/auth/login', payload)
    setToken(data.access_token)
    await fetchMe()
  }

  async function fetchMe() {
    try {
      const { data } = await http.get('/api/auth/me')
      username.value = data.username
    } catch {
      username.value = ''
    }
  }

  function logout() {
    setToken(null)
    username.value = ''
  }

  return { token, username, login, logout, fetchMe, setToken }
})
