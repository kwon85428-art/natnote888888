import path from 'node:path'
import { readFileSync } from 'node:fs'
import { defineConfig } from 'vite'
import vue from '@vitejs/plugin-vue'
import AutoImport from 'unplugin-auto-import/vite'
import Components from 'unplugin-vue-components/vite'
import { ElementPlusResolver } from 'unplugin-vue-components/resolvers'

const elementPlusResolver = ElementPlusResolver({ importStyle: 'css' })

/** 将 ElButton -> button，供按需样式路径使用 */
function elementPlusKebab(name: string): string {
  return name.replace(/([a-z0-9])([A-Z])/g, '$1-$2').toLowerCase()
}

/** 从 components.d.ts 收集已用 EP 组件，避免 dev 时逐页 discover 触发反复 optimize + reload */
function elementPlusOptimizeDeps(): string[] {
  const dtsPath = path.resolve(__dirname, 'src/components.d.ts')
  let componentNames: string[] = []
  try {
    const dts = readFileSync(dtsPath, 'utf-8')
    componentNames = [...dts.matchAll(/\bEl([A-Z][A-Za-z]+):/g)].map((m) => m[1])
  } catch {
    // 首次 clone 尚未生成 dts 时的兜底
    componentNames = [
      'Alert', 'Aside', 'Avatar', 'Button', 'Card', 'Collapse', 'CollapseItem',
      'ConfigProvider', 'Container', 'Dialog', 'Divider', 'Drawer', 'Dropdown',
      'DropdownItem', 'DropdownMenu', 'Empty', 'Form', 'FormItem', 'Header', 'Icon',
      'Image', 'Input', 'InputNumber', 'Main', 'Menu', 'MenuItem', 'Option',
      'Pagination', 'Popover', 'Radio', 'RadioButton', 'RadioGroup', 'Select',
      'Switch', 'Table', 'TableColumn', 'TabPane', 'Tabs', 'Tag', 'Tooltip', 'Upload',
    ]
  }
  const styleDeps = componentNames.map(
    (name) => `element-plus/es/components/${elementPlusKebab(name)}/style/css`,
  )
  return [
    'element-plus/es',
    'element-plus/es/locale/lang/zh-cn',
    '@element-plus/icons-vue',
    'element-plus/es/components/base/style/css',
    'element-plus/es/components/loading/style/css',
    'element-plus/es/components/message/style/css',
    'element-plus/es/components/message-box/style/css',
    ...styleDeps,
  ]
}

export default defineConfig({
  plugins: [
    vue(),
    AutoImport({
      resolvers: [elementPlusResolver],
      dts: 'src/auto-imports.d.ts',
    }),
    Components({
      resolvers: [elementPlusResolver],
      dts: 'src/components.d.ts',
    }),
  ],
  resolve: {
    alias: {
      '@': path.resolve(__dirname, 'src'),
    },
  },
  optimizeDeps: {
    include: ['md-editor-v3', ...elementPlusOptimizeDeps()],
  },
  build: {
    rollupOptions: {
      output: {
        manualChunks(id) {
          if (id.includes('node_modules/vue/') || id.includes('node_modules/@vue/')) return 'vue-core'
          if (id.includes('node_modules/vue-router')) return 'vue-router'
          if (id.includes('node_modules/pinia')) return 'pinia'
          if (id.includes('node_modules/@element-plus/icons-vue')) return 'ep-icons'
          if (id.includes('node_modules/axios')) return 'axios'
          if (id.includes('codemirror') || id.includes('@codemirror')) return 'codemirror'
          if (id.includes('md-editor-v3')) return 'md-editor'
          if (id.includes('highlight.js')) return 'hljs'
        },
      },
    },
  },
  server: {
    port: 5173,
    headers: {
      'X-Content-Type-Options': 'nosniff',
      'X-Frame-Options': 'DENY',
      'Referrer-Policy': 'strict-origin-when-cross-origin',
    },
    proxy: {
      '/api': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/uploads': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/sitemap.xml': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/robots.txt': { target: 'http://127.0.0.1:8000', changeOrigin: true },
    },
  },
  preview: {
    port: 4173,
    headers: {
      'X-Content-Type-Options': 'nosniff',
      'X-Frame-Options': 'DENY',
      'Referrer-Policy': 'strict-origin-when-cross-origin',
    },
    proxy: {
      '/api': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/uploads': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/sitemap.xml': { target: 'http://127.0.0.1:8000', changeOrigin: true },
      '/robots.txt': { target: 'http://127.0.0.1:8000', changeOrigin: true },
    },
  },
})
