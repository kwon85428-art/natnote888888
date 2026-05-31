<script setup lang="ts">
import { Reading } from '@element-plus/icons-vue'

withDefaults(
  defineProps<{
    /** list：文章列表封面区（铺满圆角矩形）；compact：首页文章预览缩略图 */
    density?: 'list' | 'compact'
  }>(),
  { density: 'list' },
)
</script>

<template>
  <div class="article-cover-ph" :data-density="density" aria-hidden="true">
    <div class="article-cover-ph__wash" />
    <el-icon class="article-cover-ph__ico"><Reading /></el-icon>
  </div>
</template>

<style scoped>
.article-cover-ph {
  position: relative;
  width: 100%;
  height: 100%;
  min-height: inherit;
  display: flex;
  align-items: center;
  justify-content: center;
  border-radius: inherit;
  overflow: hidden;
  container-type: size;
  box-shadow: inset 0 0 0 1px rgba(148, 163, 184, 0.22);
}

.article-cover-ph__wash {
  position: absolute;
  inset: 0;
  background: linear-gradient(155deg, #eff6ff 0%, #dbeafe 42%, #f8fafc 88%);
  pointer-events: none;
}

.article-cover-ph__wash::after {
  content: '';
  position: absolute;
  inset: 0;
  background:
    radial-gradient(circle at 28% 22%, rgba(255, 255, 255, 0.75) 0%, transparent 42%),
    radial-gradient(circle at 78% 78%, rgba(59, 130, 246, 0.12) 0%, transparent 48%);
  pointer-events: none;
}

.article-cover-ph__ico {
  position: relative;
  z-index: 1;
  color: #2563eb;
  opacity: 0.9;
  filter: drop-shadow(0 2px 8px rgba(37, 99, 235, 0.18));
}

/* 与用户端封面圆角区域同尺度：图标随容器最短边放大，贴近真实封面占比 */
.article-cover-ph[data-density='list'] .article-cover-ph__ico {
  font-size: clamp(56px, 62cqmin, 104px);
}

.article-cover-ph[data-density='compact'] .article-cover-ph__ico {
  font-size: clamp(44px, 58cqmin, 72px);
}

@supports not (font-size: 1cqmin) {
  .article-cover-ph[data-density='list'] .article-cover-ph__ico {
    font-size: clamp(56px, 24vmin, 104px);
  }

  .article-cover-ph[data-density='compact'] .article-cover-ph__ico {
    font-size: clamp(44px, 20vmin, 72px);
  }
}
</style>
