<script setup lang="ts">
import { ref, watch } from 'vue'
import QRCode from 'qrcode'
const props = defineProps<{
  visible: boolean
  url: string
  title?: string
}>()

const emit = defineEmits<{
  'update:visible': [value: boolean]
}>()

const qrDataUrl = ref('')
const loading = ref(false)

async function generate() {
  const target = props.url.trim()
  if (!target) {
    qrDataUrl.value = ''
    return
  }
  loading.value = true
  try {
    qrDataUrl.value = await QRCode.toDataURL(target, {
      width: 280,
      margin: 2,
      errorCorrectionLevel: 'M',
      color: { dark: '#0f172a', light: '#ffffff' },
    })
  } catch {
    qrDataUrl.value = ''
    ElMessage.error('生成二维码失败，请稍后重试')
  } finally {
    loading.value = false
  }
}

watch(
  () => [props.visible, props.url] as const,
  ([open]) => {
    if (open) void generate()
    else qrDataUrl.value = ''
  },
)

function close() {
  emit('update:visible', false)
}

async function copyUrl() {
  if (!props.url) return
  try {
    await navigator.clipboard.writeText(props.url)
    ElMessage.success('已复制文章链接')
  } catch {
    ElMessage.error('复制失败')
  }
}
</script>

<template>
  <el-dialog
    :model-value="visible"
    title="文章二维码"
    width="360px"
    class="article-qr-dialog"
    append-to-body
    align-center
    destroy-on-close
    @update:model-value="emit('update:visible', $event)"
    @close="close"
  >
    <p v-if="title" class="article-qr-dialog__title">{{ title }}</p>
    <p class="article-qr-dialog__hint">使用手机相机或微信等扫一扫，即可打开本文阅读。</p>

    <div v-loading="loading" class="article-qr-dialog__canvas">
      <img
        v-if="qrDataUrl"
        :src="qrDataUrl"
        width="280"
        height="280"
        alt="文章阅读二维码"
        class="article-qr-dialog__img"
      />
    </div>

    <p class="article-qr-dialog__url" :title="url">{{ url }}</p>

    <template #footer>
      <el-button @click="close">关闭</el-button>
      <el-button type="primary" plain :disabled="!url" @click="copyUrl">复制链接</el-button>
    </template>
  </el-dialog>
</template>
