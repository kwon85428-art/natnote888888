<script setup lang="ts">
import PlatformLogoPlaceholder from '@/components/PlatformLogoPlaceholder.vue'
import { useSettingsAdminPage } from '@/composables/useSettingsAdminPage'
import { uploadUrl } from '@/utils/media'

const { platform, savePlatform, uploadLogo } = useSettingsAdminPage()

function onLogoChange(f: { raw?: File }) {
  if (f.raw) void uploadLogo(f.raw)
}
</script>

<template>
  <div class="admin-page settings-page">
    <header class="admin-page-head">
      <h1 class="admin-page-title">平台设置</h1>
      <p class="admin-page-desc">
        配置站点名称、Logo、页脚与备案信息；控制前台「网址 / 文章」模块开关、菜单显示名、默认落地页，以及各页「推荐网址 / 推荐文章」推广区块的显示。
      </p>
    </header>

    <div class="admin-panel">
      <el-form class="admin-form" label-width="136px" label-position="right">
        <el-form-item label="平台名称">
          <el-input v-model="platform.platform_name" clearable placeholder="如：NavNote" />
          <p class="admin-form-hint">显示在顶部导航、浏览器标题与 SEO 品牌名中。</p>
        </el-form-item>

        <el-form-item label="网址菜单名称">
          <el-input
            v-model="platform.menu_sites_label"
            clearable
            maxlength="32"
            show-word-limit
            placeholder="前台导航「网址」显示名"
          />
          <p class="admin-form-hint">主导航中「网址」入口的文字，建议 2～6 个字。</p>
        </el-form-item>

        <el-form-item label="文章菜单名称">
          <el-input
            v-model="platform.menu_articles_label"
            clearable
            maxlength="32"
            show-word-limit
            placeholder="前台导航「文章」显示名"
          />
          <p class="admin-form-hint">主导航中「文章」入口的文字，可与业务称呼一致（如博客、专栏等）。</p>
        </el-form-item>

        <el-form-item label="平台 Logo">
          <div class="admin-logo-row">
            <div class="admin-logo-row__preview">
              <el-avatar
                v-if="platform.logo_path"
                :size="64"
                :src="uploadUrl(platform.logo_path)"
                shape="square"
              />
              <PlatformLogoPlaceholder v-else />
            </div>
            <el-upload :auto-upload="false" :show-file-list="false" accept="image/*" @change="onLogoChange">
              <el-button>上传 Logo</el-button>
            </el-upload>
          </div>
          <p class="admin-form-hint">建议正方形 PNG/SVG，透明底更佳；上传后立即生效于前台导航。</p>
        </el-form-item>

        <el-form-item label="页脚 HTML">
          <el-input
            v-model="platform.footer_text"
            type="textarea"
            :rows="4"
            placeholder="支持简单 HTML，如版权、友情链接"
          />
          <p class="admin-form-hint">渲染在公开页底部；请勿嵌入不可信脚本。</p>
        </el-form-item>

        <el-form-item label="联系方式">
          <el-input
            v-model="platform.contact_info"
            type="textarea"
            :rows="2"
            placeholder="邮箱、微信、QQ 等，可多行"
          />
        </el-form-item>

        <el-form-item label="ICP 备案号">
          <el-input v-model="platform.icp_text" clearable placeholder="京ICP备xxxxxxxx号" />
        </el-form-item>

        <el-form-item label="ICP 链接">
          <el-input v-model="platform.icp_link_url" clearable placeholder="https://beian.miit.gov.cn/" />
          <p class="admin-form-hint">备案号可点击跳转的 URL，留空则仅展示文字。</p>
        </el-form-item>

        <el-divider content-position="left">前台模块</el-divider>

        <el-form-item label="默认落地页">
          <el-radio-group v-model="platform.default_home">
            <el-radio label="sites">网址导航</el-radio>
            <el-radio label="articles">文章列表</el-radio>
          </el-radio-group>
          <p class="admin-form-hint">访问根路径 <code>/</code> 时，在两大模块均开启的前提下跳转到哪一页。</p>
        </el-form-item>

        <el-form-item label="网址模块">
          <div class="admin-switch-row">
            <el-switch v-model="platform.public_sites_enabled" active-text="开启" inactive-text="关闭" />
            <span class="admin-form-hint admin-form-hint--inline">关闭后前台隐藏网址导航，且无法访问 <code>/sites</code>。</span>
          </div>
        </el-form-item>

        <el-form-item label="文章模块">
          <div class="admin-switch-row">
            <el-switch v-model="platform.public_articles_enabled" active-text="开启" inactive-text="关闭" />
            <span class="admin-form-hint admin-form-hint--inline">关闭后前台隐藏文章入口，且无法访问 <code>/articles</code>。</span>
          </div>
        </el-form-item>

        <el-divider content-position="left">推荐推广区块</el-divider>
        <p class="admin-form-hint" style="margin: 0 0 16px">
          仅展示后台标记为「推广」的网址与文章；对应模块关闭时，推荐区块无数据且不会显示。
        </p>

        <el-form-item label="网址页推荐网址">
          <div class="admin-switch-row">
            <el-switch v-model="platform.show_promoted_sites_on_sites" active-text="显示" inactive-text="隐藏" />
            <span class="admin-form-hint admin-form-hint--inline">在 <code>/sites</code> 主栏展示推广网址卡片。</span>
          </div>
        </el-form-item>

        <el-form-item label="网址页推荐文章">
          <div class="admin-switch-row">
            <el-switch v-model="platform.show_promoted_articles_on_sites" active-text="显示" inactive-text="隐藏" />
            <span class="admin-form-hint admin-form-hint--inline">在 <code>/sites</code> 主栏展示推广文章列表。</span>
          </div>
        </el-form-item>

        <el-form-item label="文章页推荐网址">
          <div class="admin-switch-row">
            <el-switch v-model="platform.show_promoted_sites_on_articles" active-text="显示" inactive-text="隐藏" />
            <span class="admin-form-hint admin-form-hint--inline">在 <code>/articles</code> 列表上方展示推广网址。</span>
          </div>
        </el-form-item>

        <el-form-item label="文章页推荐文章">
          <div class="admin-switch-row">
            <el-switch v-model="platform.show_promoted_articles_on_articles" active-text="显示" inactive-text="隐藏" />
            <span class="admin-form-hint admin-form-hint--inline">在 <code>/articles</code> 列表上方展示推广文章。</span>
          </div>
        </el-form-item>

        <el-form-item>
          <el-button type="primary" @click="savePlatform">保存平台信息</el-button>
        </el-form-item>
      </el-form>
    </div>
  </div>
</template>
