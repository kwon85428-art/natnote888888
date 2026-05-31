<script setup lang="ts">
import { computed } from 'vue'
import AppErrorPanel from '@/components/AppErrorPanel.vue'
import PublicNav from '@/components/PublicNav.vue'
import PlatformFooter from '@/components/PlatformFooter.vue'
import { useRouteErrorContent } from '@/composables/useRouteErrorContent'

const { kind, copy, redirectTarget } = useRouteErrorContent('not-found')
const showLogin = computed(() => kind.value === 'forbidden')
</script>

<template>
  <div class="error-page">
    <PublicNav />
    <main class="error-page__main public-main-shell">
      <div class="error-page__panel">
        <AppErrorPanel
          :kind="kind"
          :copy="copy"
          :show-login="showLogin"
          :redirect-target="redirectTarget"
        />
      </div>
    </main>
    <PlatformFooter />
  </div>
</template>

<style scoped>
.error-page {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: var(--page-bg);
}

.error-page__main {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
}

.error-page__panel {
  width: 100%;
  max-width: min(560px, 100%);
  margin: 0 auto;
  padding: 36px 28px 32px;
}

@media (max-width: 640px) {
  .error-page__panel {
    padding: 28px 18px 24px;
  }
}
</style>
