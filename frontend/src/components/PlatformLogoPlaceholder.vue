<script setup lang="ts">
import { Compass } from '@element-plus/icons-vue'
</script>

<template>
  <div class="platform-logo-ph" role="img" aria-label="尚未上传 Logo，默认显示导航图标">
    <div class="platform-logo-ph__bg" aria-hidden="true" />
    <el-icon class="platform-logo-ph__ico"><Compass /></el-icon>
    <span class="platform-logo-ph__hint">上传后将显示在此</span>
  </div>
</template>

<style scoped>
.platform-logo-ph {
  position: relative;
  width: 80px;
  height: 80px;
  border-radius: 12px;
  border: 1px solid #e2e8f0;
  background: #fff;
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 5px;
  box-sizing: border-box;
  overflow: hidden;
  box-shadow: inset 0 1px 0 rgba(255, 255, 255, 0.9), 0 1px 3px rgba(15, 23, 42, 0.06);
}

.platform-logo-ph__bg {
  position: absolute;
  inset: 0;
  background:
    radial-gradient(ellipse 90% 80% at 30% 15%, rgba(219, 234, 254, 0.85) 0%, transparent 55%),
    radial-gradient(ellipse 70% 60% at 85% 90%, rgba(237, 233, 254, 0.55) 0%, transparent 50%),
    linear-gradient(165deg, #fafbff 0%, #f1f5f9 100%);
  pointer-events: none;
}

.platform-logo-ph__ico {
  position: relative;
  z-index: 1;
  font-size: var(--fs-display);
  color: #3b82f6;
  opacity: 0.92;
  filter: drop-shadow(0 1px 1px rgba(255, 255, 255, 0.8));
}

.platform-logo-ph__hint {
  position: relative;
  z-index: 1;
  font-size: var(--fs-micro);
  font-weight: 600;
  letter-spacing: 0.02em;
  color: #64748b;
  line-height: 1.2;
  text-align: center;
  padding: 0 6px;
  max-width: 100%;
}
</style>
