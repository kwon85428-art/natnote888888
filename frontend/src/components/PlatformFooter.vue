<script setup lang="ts">
import { computed, onMounted, ref, watch } from 'vue'
import { usePublicSettingsStore } from '@/stores/publicSettings'

const props = defineProps<{
  /** 若传入则不再请求接口（首页已与设置一并加载） */
  prefetch?: {
    footer_text?: string | null
    contact_info?: string | null
    icp_text?: string | null
    icp_link_url?: string | null
  } | null
}>()

const footerHtml = ref('')
const contactText = ref('')
const icpText = ref('')
const icpLink = ref('https://beian.miit.gov.cn/')

const hasAny = computed(
  () =>
    !!(footerHtml.value?.trim() || contactText.value?.trim() || icpText.value?.trim()),
)

function applyFromData(data: {
  footer_text?: string | null
  contact_info?: string | null
  icp_text?: string | null
  icp_link_url?: string | null
}) {
  footerHtml.value = data.footer_text || ''
  contactText.value = data.contact_info || ''
  icpText.value = data.icp_text || ''
  const link = (data.icp_link_url || '').trim()
  icpLink.value = link || 'https://beian.miit.gov.cn/'
}

async function loadRemote() {
  try {
    const data = await usePublicSettingsStore().loadFromApi()
    applyFromData(data)
  } catch {
    /* ignore */
  }
}

onMounted(() => {
  if (props.prefetch) applyFromData(props.prefetch)
  else void loadRemote()
})

watch(
  () => props.prefetch,
  (p) => {
    if (p) applyFromData(p)
  },
  { deep: true },
)
</script>

<template>
  <footer v-if="hasAny" class="platform-footer">
    <div class="platform-footer__inner">
      <div v-if="footerHtml" class="platform-footer__chunk platform-footer__html" v-html="footerHtml" />
      <div v-if="contactText.trim()" class="platform-footer__chunk platform-footer__contact">{{ contactText }}</div>
      <div v-if="icpText.trim()" class="platform-footer__chunk platform-footer__icp">
        <a class="platform-footer__icp-link" :href="icpLink" target="_blank" rel="noopener noreferrer">{{ icpText }}</a>
      </div>
    </div>
  </footer>
</template>

<style scoped>
.platform-footer {
  text-align: center;
  padding: 0;
  color: var(--text-muted, #64748b);
  font-size: var(--fs-small);
  line-height: 1.6;
  border-top: 1px solid var(--nav-border, #e2e8f0);
  background: linear-gradient(180deg, rgba(248, 250, 252, 0.95) 0%, #eef2f6 100%);
}

.platform-footer__inner {
  width: 100%;
  max-width: var(--content-max, 1200px);
  margin: 0 auto;
  padding: 14px var(--pub-content-pad-x, clamp(12px, 3vw, 20px)) calc(18px + var(--safe-bottom));
  box-sizing: border-box;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 8px;
}

.platform-footer__chunk {
  max-width: 100%;
}

.platform-footer__html {
  word-break: break-word;
}

.platform-footer__html :deep(a) {
  color: var(--accent, #1d4ed8);
}
.platform-footer__html :deep(p) {
  margin: 0 0 6px;
}
.platform-footer__html :deep(p:last-child) {
  margin-bottom: 0;
}

.platform-footer__contact {
  margin: 0;
  white-space: pre-wrap;
  word-break: break-word;
  color: #64748b;
}

.platform-footer__icp {
  margin: 0;
}

.platform-footer__icp-link {
  color: #64748b;
  text-decoration: none;
  border-bottom: 1px solid transparent;
  transition: color 0.15s, border-color 0.15s;
}
.platform-footer__icp-link:hover {
  color: var(--accent, #1d4ed8);
  border-bottom-color: #bfdbfe;
}

@media (min-width: 901px) {
  .platform-footer__inner {
    flex-direction: row;
    flex-wrap: wrap;
    justify-content: center;
    align-items: center;
    column-gap: 0;
    row-gap: 6px;
    padding-top: 10px;
    padding-bottom: calc(12px + var(--safe-bottom));
  }

  .platform-footer__inner > .platform-footer__chunk + .platform-footer__chunk {
    border-left: 1px solid #cbd5e1;
    padding-left: 14px;
    margin-left: 14px;
  }

  .platform-footer__html {
    flex: 0 1 auto;
    max-width: min(480px, 38vw);
    text-align: center;
  }

  .platform-footer__html :deep(p) {
    display: inline;
    margin: 0 0.35em 0 0;
  }
  .platform-footer__html :deep(p:last-child) {
    margin-right: 0;
  }

  .platform-footer__contact {
    flex: 0 1 auto;
    max-width: min(360px, 30vw);
    text-align: left;
    white-space: pre-wrap;
  }

  .platform-footer__icp {
    flex: 0 0 auto;
    white-space: nowrap;
  }
}

@media (max-width: 900px) {
  .platform-footer__inner {
    padding-top: 12px;
    padding-bottom: calc(16px + var(--safe-bottom));
    font-size: var(--fs-small);
    line-height: 1.65;
  }
}
</style>
