<script setup lang="ts">
import AppErrorPanel from '@/components/AppErrorPanel.vue'
import { useRouteErrorContent } from '@/composables/useRouteErrorContent'

const { kind, copy } = useRouteErrorContent('not-found')
</script>

<template>
  <div class="admin-page admin-error-page">
    <div class="admin-error-page__panel admin-panel">
      <AppErrorPanel :kind="kind" :copy="copy" compact />
    </div>
  </div>
</template>

<style scoped>
.admin-error-page {
  display: flex;
  align-items: center;
  justify-content: center;
  min-height: calc(100vh - var(--pub-nav-height, 58px) - 48px);
  padding-top: 8px;
  padding-bottom: 24px;
}

.admin-error-page__panel {
  width: 100%;
  max-width: 520px;
  padding: 28px 24px 24px;
}
</style>
