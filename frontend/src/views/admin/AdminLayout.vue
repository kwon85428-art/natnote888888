<script setup lang="ts">
import {
  DataAnalysis,
  Document,
  Expand,
  Fold,
  FolderOpened,
  Link,
  Setting,
  Tickets,
} from '@element-plus/icons-vue'
import { useAdminLayout } from '@/composables/useAdminLayout'
import '@/styles/admin-shared.css'

const {
  auth,
  asideCollapsed,
  pwdDialog,
  pwdSaving,
  pwdForm,
  toggleAside,
  openPwdDialog,
  onPwdDialogClosed,
  submitPwd,
  logout,
} = useAdminLayout()
</script>

<template>
  <el-container class="admin-app admin-app--fill">
    <el-aside :width="asideCollapsed ? '64px' : '220px'" class="aside" :class="{ 'aside--collapsed': asideCollapsed }">
      <div class="logo">
        <span class="logo__mark" aria-hidden="true">N</span>
        <span v-if="!asideCollapsed" class="logo__text">NavNote</span>
        <span v-else class="logo__text logo__text--solo" title="NavNote 管理后台">N</span>
      </div>
      <el-menu
        router
        :collapse="asideCollapsed"
        :collapse-transition="false"
        :default-active="$route.path"
        class="admin-menu"
      >
        <el-menu-item index="/admin/site-categories">
          <el-icon><FolderOpened /></el-icon>
          <template #title>网址分类</template>
        </el-menu-item>
        <el-menu-item index="/admin/sites">
          <el-icon><Link /></el-icon>
          <template #title>网站管理</template>
        </el-menu-item>
        <el-menu-item index="/admin/article-categories">
          <el-icon><Tickets /></el-icon>
          <template #title>文章分类</template>
        </el-menu-item>
        <el-menu-item index="/admin/articles">
          <el-icon><Document /></el-icon>
          <template #title>文章管理</template>
        </el-menu-item>
        <el-menu-item index="/admin/settings">
          <el-icon><Setting /></el-icon>
          <template #title>平台设置</template>
        </el-menu-item>
        <el-menu-item index="/admin/stats">
          <el-icon><DataAnalysis /></el-icon>
          <template #title>统计与日志</template>
        </el-menu-item>
      </el-menu>
      <div class="aside__collapse-wrap">
        <el-tooltip :content="asideCollapsed ? '展开菜单' : '收起菜单'" placement="right" :disabled="!asideCollapsed">
          <el-button
            class="aside__collapse-btn"
            :aria-expanded="!asideCollapsed"
            aria-label="收起或展开侧栏菜单"
            text
            @click="toggleAside"
          >
            <el-icon :size="18"><Fold v-if="!asideCollapsed" /><Expand v-else /></el-icon>
          </el-button>
        </el-tooltip>
      </div>
    </el-aside>
    <el-container class="admin-body">
      <el-header class="header" height="56px">
        <el-button class="header__menu-toggle" text aria-label="收起或展开侧栏菜单" @click="toggleAside">
          <el-icon :size="18"><Fold v-if="!asideCollapsed" /><Expand v-else /></el-icon>
        </el-button>
        <span class="header__title">控制台</span>
        <div class="header__actions">
          <span class="header__user">{{ auth.username }}</span>
          <el-button type="primary" link @click="openPwdDialog">修改密码</el-button>
          <el-button type="danger" plain size="small" @click="logout">退出</el-button>
        </div>
      </el-header>
      <el-main class="admin-main">
        <div class="admin-main-inner">
          <router-view />
        </div>
      </el-main>
    </el-container>

    <el-dialog
      v-model="pwdDialog"
      title="修改登录密码"
      width="440px"
      class="admin-dialog admin-pwd-dialog"
      append-to-body
      align-center
      destroy-on-close
      @closed="onPwdDialogClosed"
    >
      <el-form label-position="top" @submit.prevent>
        <el-form-item label="当前密码">
          <el-input v-model="pwdForm.current_password" type="password" show-password autocomplete="current-password" />
        </el-form-item>
        <el-form-item label="新密码">
          <el-input v-model="pwdForm.new_password" type="password" show-password autocomplete="new-password" />
        </el-form-item>
        <el-form-item label="确认新密码">
          <el-input v-model="pwdForm.new_password2" type="password" show-password autocomplete="new-password" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="pwdDialog = false">取消</el-button>
        <el-button type="primary" :loading="pwdSaving" @click="submitPwd">保存</el-button>
      </template>
    </el-dialog>
  </el-container>
</template>

<style scoped>
.admin-app--fill {
  min-height: 100vh;
  min-height: 100dvh;
}

.aside {
  display: flex;
  flex-direction: column;
  overflow: hidden;
  border-right: none;
  background: linear-gradient(180deg, #0f172a 0%, #1e293b 52%, #172554 100%);
  box-shadow: 4px 0 24px rgba(15, 23, 42, 0.12);
  transition: width 0.22s ease;
}

.logo {
  flex-shrink: 0;
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 16px 14px 14px;
  border-bottom: 1px solid rgba(255, 255, 255, 0.08);
}

.logo__mark {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 10px;
  font-size: var(--fs-small);
  font-weight: 800;
  color: #fff;
  background: linear-gradient(135deg, #3b82f6 0%, #2563eb 100%);
  box-shadow: 0 4px 12px rgba(37, 99, 235, 0.45);
  flex-shrink: 0;
}

.logo__text {
  font-size: var(--fs-body);
  font-weight: 700;
  color: #f8fafc;
  letter-spacing: -0.02em;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.logo__text--solo {
  display: none;
}

.aside--collapsed .logo {
  justify-content: center;
  padding-left: 10px;
  padding-right: 10px;
}

.aside--collapsed .logo__mark {
  width: 36px;
  height: 36px;
}

.admin-menu {
  flex: 1 1 auto;
  min-height: 0;
  overflow-x: hidden;
  overflow-y: auto;
  border-right: none;
  padding: 10px 8px 12px;
  background: transparent;
}

.admin-menu :deep(.el-menu) {
  border-right: none;
  background: transparent;
}

.admin-menu :deep(.el-menu-item) {
  height: 42px;
  line-height: 42px;
  margin: 2px 0;
  border-radius: 10px;
  font-weight: 500;
  font-size: var(--fs-small);
  color: #94a3b8;
  transition:
    background 0.15s ease,
    color 0.15s ease;
}

.admin-menu :deep(.el-menu-item .el-icon) {
  color: inherit;
}

.admin-menu :deep(.el-menu-item:hover) {
  color: #e2e8f0;
  background: rgba(255, 255, 255, 0.06);
}

.admin-menu :deep(.el-menu-item.is-active) {
  color: #fff;
  font-weight: 600;
  background: rgba(37, 99, 235, 0.35) !important;
  box-shadow: inset 3px 0 0 #60a5fa;
}

.aside__collapse-wrap {
  flex-shrink: 0;
  padding: 8px 8px 12px;
  border-top: 1px solid rgba(255, 255, 255, 0.08);
}

.aside__collapse-btn {
  width: 100%;
  height: 36px;
  justify-content: center;
  color: #94a3b8;
}

.aside__collapse-btn:hover {
  color: #e2e8f0;
  background: rgba(255, 255, 255, 0.08);
}

.admin-body {
  min-width: 0;
}

.header {
  display: flex;
  align-items: center;
  gap: 10px;
  padding: 0 18px;
  background: rgba(255, 255, 255, 0.92);
  backdrop-filter: blur(10px);
  border-bottom: 1px solid var(--admin-border, #e2e8f0);
  box-shadow: 0 1px 0 rgba(255, 255, 255, 0.8);
}

.header__menu-toggle {
  padding: 8px;
  color: #64748b;
}

.header__menu-toggle:hover {
  color: var(--admin-accent, #2563eb);
}

.header__title {
  margin-right: auto;
  font-size: var(--fs-small);
  font-weight: 600;
  color: #64748b;
  letter-spacing: 0.01em;
}

.header__actions {
  display: flex;
  align-items: center;
  gap: 8px 12px;
  flex-wrap: wrap;
}

.header__user {
  font-size: var(--fs-caption);
  font-weight: 600;
  color: #0f172a;
  max-width: 160px;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  padding: 6px 12px;
  border-radius: 999px;
  background: #f1f5f9;
  border: 1px solid #e2e8f0;
}

@media (max-width: 520px) {
  .admin-pwd-dialog.el-dialog {
    width: min(440px, 92vw) !important;
  }

  .header__user {
    display: none;
  }
}
</style>
