<script setup lang="ts">
import { computed } from 'vue'
import { useRouter } from 'vue-router'
import type { RouteErrorCopy, RouteErrorKind } from '@/constants/routeErrors'

const props = withDefaults(
  defineProps<{
    kind?: RouteErrorKind
    copy?: RouteErrorCopy
    compact?: boolean
    showLogin?: boolean
    redirectTarget?: string
  }>(),
  {
    kind: 'not-found',
    compact: false,
    showLogin: false,
    redirectTarget: '',
  },
)

const router = useRouter()

const iconLabel = computed(() => (props.kind === 'forbidden' ? '无权限' : '未找到'))

function goHome() {
  router.push('/')
}

function goBack() {
  if (window.history.length > 1) router.back()
  else goHome()
}

function goLogin() {
  const q = props.redirectTarget ? { redirect: props.redirectTarget } : undefined
  router.push({ path: '/admin/login', query: q })
}
</script>

<template>
  <section class="app-error" :class="{ 'app-error--compact': compact }" role="alert" aria-live="polite">
    <div class="app-error__icon" :class="`app-error__icon--${kind}`" aria-hidden="true">
      <span class="app-error__code">{{ copy?.code ?? (kind === 'forbidden' ? '403' : '404') }}</span>
      <span class="app-error__icon-label">{{ iconLabel }}</span>
    </div>
    <h1 class="app-error__title">{{ copy?.title }}</h1>
    <p class="app-error__message">{{ copy?.message }}</p>
    <div class="app-error__actions">
      <el-button type="primary" size="large" @click="goHome">返回首页</el-button>
      <el-button size="large" @click="goBack">返回上一页</el-button>
      <el-button v-if="showLogin" type="primary" plain size="large" @click="goLogin">管理员登录</el-button>
      <slot name="actions" />
    </div>
  </section>
</template>

<style scoped>
.app-error {
  text-align: center;
  padding: 8px 4px 4px;
}

.app-error--compact {
  padding: 4px 0;
}

.app-error__icon {
  display: inline-flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  width: 88px;
  height: 88px;
  margin: 0 auto 20px;
  border-radius: 20px;
  border: 1px solid var(--border-subtle);
  background: linear-gradient(145deg, #f8fafc 0%, #fff 100%);
  box-shadow: 0 4px 20px rgba(15, 23, 42, 0.06);
}

.app-error--compact .app-error__icon {
  width: 72px;
  height: 72px;
  margin-bottom: 16px;
}

.app-error__icon--forbidden {
  background: linear-gradient(145deg, #fff7ed 0%, #fff 100%);
  border-color: #fed7aa;
}

.app-error__icon--not-found {
  background: linear-gradient(145deg, #eff6ff 0%, #fff 100%);
  border-color: #bfdbfe;
}

.app-error__code {
  font-size: var(--fs-display);
  font-weight: 800;
  letter-spacing: -0.04em;
  color: var(--accent, #1d4ed8);
  line-height: 1;
}

.app-error__icon--forbidden .app-error__code {
  color: #c2410c;
}

.app-error__icon-label {
  margin-top: 4px;
  font-size: var(--fs-micro);
  font-weight: 600;
  color: var(--text-muted);
}

.app-error__title {
  margin: 0 0 10px;
  font-size: clamp(20px, 3vw, 24px);
  font-weight: 800;
  color: var(--text);
  letter-spacing: -0.02em;
}

.app-error__message {
  margin: 0 auto 24px;
  max-width: 36em;
  font-size: var(--fs-body);
  line-height: 1.65;
  color: var(--text-muted);
}

.app-error--compact .app-error__message {
  margin-bottom: 18px;
}

.app-error__actions {
  display: flex;
  flex-wrap: wrap;
  gap: 10px;
  justify-content: center;
}

.app-error__actions .el-button + .el-button {
  margin-left: 0;
}
</style>
