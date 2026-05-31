<script setup lang="ts">
import AdminBoolCell from '@/components/admin/AdminBoolCell.vue'
import SiteLogoPlaceholder from '@/components/SiteLogoPlaceholder.vue'
import { useSitesAdminPage } from '@/composables/useSitesAdminPage'
import { uploadUrl } from '@/utils/media'

const {
  sites,
  siteCategories,
  q,
  siteCategoryId,
  page,
  pageSize,
  total,
  dialog,
  fetchDialog,
  fetchUrl,
  fetchPreview,
  form,
  tagInput,
  selection,
  load,
  onPageSizeChange,
  openCreate,
  openEdit,
  save,
  removeRow,
  openFetch,
  doFetchPreview,
  applyFetchToForm,
  uploadLogo,
  checkOne,
  checkBatch,
  addTag,
  removeTag,
  onSelectionChange,
} = useSitesAdminPage()

function onUploadLogo(f: { raw?: File }) {
  if (f.raw) void uploadLogo(f.raw)
}
</script>

<template>
  <div class="admin-page">
    <header class="admin-page-head">
      <h1 class="admin-page-title">网站管理</h1>
      <p class="admin-page-desc">维护收录站点、分类归属与推广展示；支持批量校验链接可访问性。</p>
    </header>
    <div class="admin-stack">
      <div class="toolbar">
      <el-input
        v-model="q"
        class="toolbar-field--grow"
        placeholder="名称/URL 搜索"
        clearable
        @clear="load({ resetPage: true })"
        @keyup.enter="load({ resetPage: true })"
      />
      <el-select v-model="siteCategoryId" class="toolbar-field--cat" placeholder="分类" clearable @change="load({ resetPage: true })">
        <el-option v-for="c in siteCategories" :key="c.id" :label="c.name" :value="c.id" />
      </el-select>
      <el-button @click="load({ resetPage: true })">筛选</el-button>
      <span class="toolbar__spacer" />
      <el-button :disabled="!selection.length" @click="checkBatch">批量校验</el-button>
      <el-button type="primary" @click="openCreate">新增网站</el-button>
    </div>

    <el-table :data="sites" stripe class="admin-table" size="small" @selection-change="onSelectionChange">
      <el-table-column type="selection" width="45" />
      <el-table-column label="图标" width="70">
        <template #default="{ row }">
          <el-avatar
            shape="square"
            :size="36"
            :src="row.logo_path || row.favicon_path ? uploadUrl(row.logo_path || row.favicon_path) : undefined"
          >
            <SiteLogoPlaceholder />
          </el-avatar>
        </template>
      </el-table-column>
      <el-table-column prop="name" label="名称" min-width="140" />
      <el-table-column prop="site_category_name" label="分类" min-width="100" show-overflow-tooltip />
      <el-table-column prop="url" label="URL" min-width="200" show-overflow-tooltip />
      <el-table-column label="有效" width="80" align="center">
        <template #default="{ row }">
          <AdminBoolCell :value="row.is_valid" variant="valid" />
        </template>
      </el-table-column>
      <el-table-column prop="invalid_note" label="失效说明" min-width="120" show-overflow-tooltip>
        <template #default="{ row }">
          <span v-if="row.invalid_note" class="admin-cell-muted">{{ row.invalid_note }}</span>
          <span v-else class="admin-cell-muted">—</span>
        </template>
      </el-table-column>
      <el-table-column label="推广" width="80" align="center">
        <template #default="{ row }">
          <AdminBoolCell :value="row.is_promoted" variant="promote" />
        </template>
      </el-table-column>
      <el-table-column prop="visit_count" label="访问" width="80" />
      <el-table-column label="操作" width="220" fixed="right">
        <template #default="{ row }">
          <div class="admin-table-actions">
            <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
            <el-button link @click="checkOne(row)">校验</el-button>
            <el-button link type="danger" @click="removeRow(row)">删除</el-button>
          </div>
        </template>
      </el-table-column>
    </el-table>

    <div class="pager-row">
      <el-pagination
        v-model:current-page="page"
        v-model:page-size="pageSize"
        :total="total"
        :page-sizes="[10, 20, 50, 100]"
        layout="total, sizes, prev, pager, next, jumper"
        background
        @current-change="() => void load()"
        @size-change="onPageSizeChange"
      />
    </div>
    </div>

    <el-dialog
      v-model="dialog"
      :title="form.id ? '编辑网站' : '新增网站'"
      width="640px"
      class="admin-dialog"
      append-to-body
      align-center
      destroy-on-close
    >
      <el-form class="admin-form" label-width="120px" label-position="right">
        <el-form-item label="名称"><el-input v-model="form.name" /></el-form-item>
        <el-form-item label="URL">
          <el-input v-model="form.url" />
          <el-button style="margin-top: 6px" @click="openFetch">自动获取信息</el-button>
        </el-form-item>
        <el-form-item label="分类">
          <el-select v-model="form.site_category_id" style="width: 100%">
            <el-option v-for="c in siteCategories" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="标签">
          <div style="display: flex; gap: 6px; flex-wrap: wrap">
            <el-tag v-for="t in form.tags" :key="t" closable @close="removeTag(t)">{{ t }}</el-tag>
            <el-input v-model="tagInput" style="width: 140px" @keyup.enter="addTag" />
            <el-button @click="addTag">添加</el-button>
          </div>
        </el-form-item>
        <el-form-item label="简介"><el-input v-model="form.description" type="textarea" /></el-form-item>
        <el-form-item label="Favicon">
          <el-input v-model="form.favicon_path" placeholder="相对 uploads 路径，如 favicons/xxx.ico" />
        </el-form-item>
        <el-form-item label="自定义 Logo">
          <el-upload :auto-upload="false" :show-file-list="false" accept="image/*" @change="onUploadLogo">
            <el-button>上传替换</el-button>
          </el-upload>
          <span v-if="form.logo_path" style="margin-left: 8px">{{ form.logo_path }}</span>
        </el-form-item>
        <el-form-item label="排序"><el-input-number v-model="form.sort_order" /></el-form-item>
        <el-form-item label="是否推广">
          <el-switch v-model="form.is_promoted" />
          <span class="admin-form-hint--dialog">推广网址在分类列表与「推荐网址」中优先展示</span>
        </el-form-item>
        <el-form-item label="标记有效"><el-switch v-model="form.is_valid" /></el-form-item>
        <el-form-item v-if="!form.is_valid" label="失效说明">
          <el-input
            v-model="form.invalid_note"
            type="textarea"
            :rows="2"
            placeholder="可选，记录校验失败原因等"
            maxlength="512"
            show-word-limit
          />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog
      v-model="fetchDialog"
      title="自动抓取"
      width="560px"
      class="admin-dialog"
      append-to-body
      align-center
      destroy-on-close
    >
      <p class="admin-dialog-hint">输入站点 URL，抓取标题、图标等信息并填入表单。</p>
      <el-input v-model="fetchUrl" placeholder="https://example.com" clearable />
      <div class="admin-dialog-actions">
        <el-button type="primary" @click="doFetchPreview">抓取并填充</el-button>
        <el-button @click="applyFetchToForm">关闭</el-button>
      </div>
      <pre v-if="fetchPreview" class="admin-code-block">{{ JSON.stringify(fetchPreview, null, 2) }}</pre>
    </el-dialog>
  </div>
</template>

