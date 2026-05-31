import { createApp } from 'vue'
import { createPinia } from 'pinia'
import { bootstrapPublicSettings } from './bootstrap/publicSettings'
import App from './App.vue'
import router from './router'
import './styles/public-shared.css'
import './style.css'

async function start() {
  const app = createApp(App)
  const pinia = createPinia()
  app.use(pinia)

  await bootstrapPublicSettings(pinia)

  app.use(router)
  await router.isReady()
  app.mount('#app')
}

void start()
