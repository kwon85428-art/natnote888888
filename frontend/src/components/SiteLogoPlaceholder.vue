<script setup lang="ts">
import { Link } from '@element-plus/icons-vue'

withDefaults(
  defineProps<{
    /** 推荐区卡片略偏紫色调 */
    variant?: 'default' | 'featured'
  }>(),
  { variant: 'default' },
)
</script>

<template>
  <div class="site-logo-ph" :class="'site-logo-ph--' + variant" aria-hidden="true">
    <el-icon class="site-logo-ph__ico"><Link /></el-icon>
  </div>
</template>

<style scoped>
.site-logo-ph {
  width: 100%;
  height: 100%;
  min-height: 0;
  container-type: size;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: inherit;
  background: linear-gradient(145deg, #eef2ff 0%, #e0e7ff 48%, #ede9fe 100%);
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.88);
}

.site-logo-ph--featured {
  background: linear-gradient(145deg, #f5f3ff 0%, #ede9fe 45%, #faf5ff 100%);
}

.site-logo-ph__ico {
  color: #4f46e5;
  font-size: clamp(15px, 32cqmin, 26px);
}

@supports not (font-size: 1cqmin) {
  .site-logo-ph__ico {
    font-size: clamp(15px, 4.5vmin, 22px);
  }
}
</style>
