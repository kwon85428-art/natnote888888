<script setup lang="ts">
import { onMounted, watch } from 'vue'
import { useRoute } from 'vue-router'
import zhCn from 'element-plus/es/locale/lang/zh-cn'
import { trackPageVisit } from '@/api/public'

const route = useRoute()

onMounted(() => {
  if (!route.path.startsWith('/admin')) void trackPageVisit()
})

watch(
  () => route.path,
  (p) => {
    if (!p.startsWith('/admin')) void trackPageVisit()
  },
)
</script>

<template>
  <el-config-provider :locale="zhCn">
    <router-view />
  </el-config-provider>
</template>
