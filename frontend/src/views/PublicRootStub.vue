<script setup lang="ts">
import { onMounted } from 'vue'
import { DEFAULT_PLATFORM_SETTINGS } from '@/constants/platformDefaults'
import { usePublicSettingsStore } from '@/stores/publicSettings'
import { applyPublicSeo, syncSeoBrandFromSettings } from '../utils/seo'
import PublicNav from '../components/PublicNav.vue'
import PlatformFooter from '../components/PlatformFooter.vue'

onMounted(() => {
  const data = usePublicSettingsStore().settings ?? DEFAULT_PLATFORM_SETTINGS
  syncSeoBrandFromSettings(data)
  applyPublicSeo({
    title: '首页',
    description: '前台暂未开放全部模块时的提示页；开放后将跳转至网址或文章。',
  })
})
</script>

<template>
  <div class="stub">
    <PublicNav />
    <main class="stub__main">
      <div class="stub__panel">
        <p class="stub__msg">前台暂未开放网址与文章模块，请稍后再试或联系管理员。</p>
      </div>
    </main>
    <PlatformFooter />
  </div>
</template>

<style scoped>
.stub {
  min-height: 100vh;
  display: flex;
  flex-direction: column;
  background: #f8fafc;
}
.stub__main {
  flex: 1;
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 32px clamp(16px, 4vw, 28px);
}

.stub__panel {
  width: 100%;
  max-width: min(var(--content-max, 1200px), 100%);
  padding: 28px 24px;
  background: var(--surface);
  border: 1px solid var(--border-subtle);
  border-radius: 14px;
  box-shadow: 0 4px 24px rgba(15, 23, 42, 0.06);
}

.stub__msg {
  margin: 0;
  text-align: center;
  font-size: var(--fs-body);
  color: var(--text-muted);
  line-height: 1.65;
}
</style>
