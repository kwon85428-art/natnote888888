<script setup lang="ts">
import { onMounted, ref } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import http from '@/api/http'
import { getApiErrorMessage } from '@/api/errors'
import { useAuthStore } from '@/stores/auth'
import { sanitizeInternalRedirect } from '@/utils/navigation'
const router = useRouter()
const route = useRoute()
const auth = useAuthStore()

const form = ref({ username: '', password: '', captcha_id: '', captcha_code: '' })
const captchaQuestion = ref('')
const loading = ref(false)

async function refreshCaptcha() {
  const { data } = await http.get('/api/auth/captcha')
  form.value.captcha_id = data.captcha_id
  captchaQuestion.value = data.question
  form.value.captcha_code = ''
}

onMounted(async () => {
  if (auth.token) {
    await auth.fetchMe()
    if (auth.username) {
      router.replace(sanitizeInternalRedirect(route.query.redirect))
      return
    }
  }
  await refreshCaptcha()
})

async function submit() {
  loading.value = true
  try {
    await auth.login(form.value)
    ElMessage.success('登录成功')
    router.replace(sanitizeInternalRedirect(route.query.redirect))
  } catch (e: unknown) {
    ElMessage.error(getApiErrorMessage(e, '登录失败'))
    await refreshCaptcha()
  } finally {
    loading.value = false
  }
}
</script>

<template>
  <div class="auth-shell">
    <el-card class="auth-card" shadow="never">
      <h1 class="auth-card__title">管理员登录</h1>
      <p class="auth-card__lead">请输入账号、密码与验证码。</p>

      <el-form class="auth-form" label-position="top" @submit.prevent="submit">
        <el-form-item label="账号">
          <el-input v-model="form.username" size="large" clearable autocomplete="username" placeholder="用户名" />
        </el-form-item>
        <el-form-item label="密码">
          <el-input
            v-model="form.password"
            size="large"
            type="password"
            show-password
            autocomplete="current-password"
            placeholder="密码"
          />
        </el-form-item>
        <el-form-item label="验证码">
          <div class="auth-captcha">
            <div class="auth-captcha__q">{{ captchaQuestion }}</div>
            <div class="auth-captcha__row">
              <el-input v-model="form.captcha_code" size="large" maxlength="8" clearable placeholder="计算结果" />
              <el-button size="large" @click="refreshCaptcha">换一张</el-button>
            </div>
          </div>
        </el-form-item>
        <el-form-item>
          <div class="auth-actions">
            <el-button type="primary" size="large" native-type="submit" :loading="loading">登录</el-button>
          </div>
        </el-form-item>
      </el-form>

      <el-alert
        class="auth-alert"
        title="默认账号 admin / admin123456，登录后请尽快修改密码"
        type="info"
        show-icon
        :closable="false"
      />
    </el-card>
  </div>
</template>
