import { onMounted, reactive, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import http from '@/api/http'
import { getApiErrorMessage } from '@/api/errors'
import { useAuthStore } from '@/stores/auth'
const ADMIN_ASIDE_COLLAPSED_KEY = 'admin_aside_collapsed'

export function useAdminLayout() {
  const router = useRouter()
  const auth = useAuthStore()
  const asideCollapsed = ref(false)
  const pwdDialog = ref(false)
  const pwdSaving = ref(false)
  const pwdForm = reactive({
    current_password: '',
    new_password: '',
    new_password2: '',
  })

  onMounted(() => {
    try {
      asideCollapsed.value = localStorage.getItem(ADMIN_ASIDE_COLLAPSED_KEY) === '1'
    } catch {
      /* ignore */
    }
  })

  watch(asideCollapsed, (v) => {
    try {
      localStorage.setItem(ADMIN_ASIDE_COLLAPSED_KEY, v ? '1' : '0')
    } catch {
      /* ignore */
    }
  })

  function toggleAside() {
    asideCollapsed.value = !asideCollapsed.value
  }

  function openPwdDialog() {
    pwdForm.current_password = ''
    pwdForm.new_password = ''
    pwdForm.new_password2 = ''
    pwdDialog.value = true
  }

  function onPwdDialogClosed() {
    pwdSaving.value = false
  }

  async function submitPwd() {
    if (pwdForm.new_password.length < 8) {
      ElMessage.warning('新密码至少 8 位')
      return
    }
    if (pwdForm.new_password !== pwdForm.new_password2) {
      ElMessage.warning('两次输入的新密码不一致')
      return
    }
    pwdSaving.value = true
    try {
      await http.post('/api/auth/change-password', {
        current_password: pwdForm.current_password,
        new_password: pwdForm.new_password,
      })
      ElMessage.success('密码已更新，请重新登录')
      pwdDialog.value = false
      auth.logout()
      router.push('/admin/login')
    } catch (e: unknown) {
      ElMessage.error(getApiErrorMessage(e, '修改失败'))
    } finally {
      pwdSaving.value = false
    }
  }

  function logout() {
    auth.logout()
    router.push('/admin/login')
  }

  return {
    auth,
    asideCollapsed,
    pwdDialog,
    pwdSaving,
    pwdForm,
    toggleAside,
    openPwdDialog,
    onPwdDialogClosed,
    submitPwd,
    logout,
  }
}
