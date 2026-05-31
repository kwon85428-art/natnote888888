<script setup lang="ts">
import { defineAsyncComponent, defineComponent, h } from 'vue'
import AdminBoolCell from '@/components/admin/AdminBoolCell.vue'
import { useArticlesAdminPage } from '@/composables/useArticlesAdminPage'
import { uploadUrl } from '@/utils/media'
import { formatZhDateTime } from '@/utils/datetime'
import { articleContentTypeLabel } from '@/utils/text'

const {
  list,
  cats,
  dialog,
  q,
  filterCat,
  filterType,
  page,
  pageSize,
  total,
  form,
  tagInput,
  load,
  openCreate,
  openEdit,
  save,
  removeRow,
  onPageSizeChange,
  uploadCover,
  onUploadImg,
  addTag,
} = useArticlesAdminPage()

function onUploadCover(f: { raw?: File }) {
  if (f.raw) void uploadCover(f.raw)
}

const MdEditor = defineAsyncComponent({
  loader: () =>
    Promise.all([import('md-editor-v3/lib/style.css'), import('md-editor-v3'), import('../../config/mdEditor')]).then(
      ([, mod, mdSetup]) => {
        mdSetup.ensureMdEditorLocalExtensions()
        return mod.MdEditor
      },
    ),
  loadingComponent: defineComponent({
    name: 'MdEditorLoading',
    setup() {
      return () => h('div', { class: 'article-md-loading' }, '正在加载 Markdown 编辑器…')
    },
  }),
  delay: 0,
  timeout: 120000,
})
</script>

<template>
  <div class="admin-page">
    <header class="admin-page-head">
      <h1 class="admin-page-title">文章管理</h1>
      <p class="admin-page-desc">发布与编辑站内文章，支持外链与 Markdown 正文、置顶与推广展示。</p>
    </header>
    <div class="admin-stack">
      <div class="toolbar">
      <el-input
        v-model="q"
        class="toolbar-field--q-sm"
        placeholder="标题搜索"
        clearable
        @clear="load({ resetPage: true })"
        @keyup.enter="load({ resetPage: true })"
      />
      <el-select v-model="filterCat" class="toolbar-field--cat" placeholder="分类" clearable @change="load({ resetPage: true })">
        <el-option v-for="c in cats" :key="c.id" :label="c.name" :value="c.id" />
      </el-select>
      <el-select v-model="filterType" class="toolbar-field--type" placeholder="内容形式" clearable @change="load({ resetPage: true })">
        <el-option label="外链" value="external" />
        <el-option label="原创" value="original" />
      </el-select>
      <el-button @click="load({ resetPage: true })">筛选</el-button>
      <span class="toolbar__spacer" />
      <el-button type="primary" @click="openCreate">发布文章</el-button>
    </div>

    <el-table :data="list" stripe class="admin-table" size="small">
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column label="封面" width="80">
        <template #default="{ row }">
          <el-image
            v-if="row.cover_path"
            class="article-cover-thumb"
            :src="uploadUrl(row.cover_path)"
            fit="cover"
          />
        </template>
      </el-table-column>
      <el-table-column prop="title" label="标题" min-width="160" />
      <el-table-column prop="article_category_name" label="分类" min-width="100" show-overflow-tooltip />
      <el-table-column label="形式" width="90">
        <template #default="{ row }">{{ articleContentTypeLabel(row) }}</template>
      </el-table-column>
      <el-table-column label="置顶" width="80" align="center">
        <template #default="{ row }">
          <AdminBoolCell :value="row.is_pinned" variant="pin" />
        </template>
      </el-table-column>
      <el-table-column label="推广" width="80" align="center">
        <template #default="{ row }">
          <AdminBoolCell :value="row.is_promoted" variant="promote" />
        </template>
      </el-table-column>
      <el-table-column prop="visit_count" label="阅读量" width="90" />
      <el-table-column label="发布时间" width="170" show-overflow-tooltip>
        <template #default="{ row }">{{ formatZhDateTime(row.published_at) }}</template>
      </el-table-column>
      <el-table-column label="操作" width="140" fixed="right">
        <template #default="{ row }">
          <div class="admin-table-actions">
            <el-button link type="primary" @click="openEdit(row)">编辑</el-button>
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
      :title="form.id ? '编辑文章' : '发布文章'"
      width="min(1120px, 96vw)"
      class="admin-dialog article-dialog"
      append-to-body
      align-center
      destroy-on-close
    >
      <el-form class="admin-form" label-width="120px" label-position="right">
        <el-form-item label="标题"><el-input v-model="form.title" /></el-form-item>
        <el-form-item label="摘要"><el-input v-model="form.summary" type="textarea" :rows="2" placeholder="可选，用于 SEO 或运营备注" /></el-form-item>
        <el-form-item label="分类">
          <el-select v-model="form.article_category_id" style="width: 100%">
            <el-option v-for="c in cats" :key="c.id" :label="c.name" :value="c.id" />
          </el-select>
        </el-form-item>
        <el-form-item label="标签">
          <div style="display: flex; gap: 6px; flex-wrap: wrap">
            <el-tag
              v-for="t in form.tags"
              :key="t"
              closable
              @close="form.tags = form.tags.filter((x: string) => x !== t)"
              >{{ t }}</el-tag
            >
            <el-input v-model="tagInput" style="width: 140px" @keyup.enter="addTag" />
            <el-button @click="addTag">添加</el-button>
          </div>
        </el-form-item>
        <el-form-item label="发布时间">
          <el-input v-model="form.published_at" placeholder="YYYY-MM-DD HH:mm:ss" />
        </el-form-item>
        <el-form-item label="封面">
          <el-upload :auto-upload="false" :show-file-list="false" accept="image/*" @change="onUploadCover">
            <el-button>上传封面</el-button>
          </el-upload>
          <span v-if="form.cover_path" style="margin-left: 8px">{{ form.cover_path }}</span>
        </el-form-item>
        <el-form-item label="内容形式">
          <el-radio-group v-model="form.content_type">
            <el-radio label="external">外部文章（有原文链接时详情页展示「阅读原文」）</el-radio>
            <el-radio label="original">原创文章（Markdown，站内渲染）</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="原文链接" v-if="form.content_type === 'external'">
          <el-input v-model="form.source_url" placeholder="https://…" />
        </el-form-item>
        <el-form-item v-if="form.content_type === 'original'" label="正文 Markdown" class="article-md-form-item">
          <p class="article-md-hint">支持工具栏插入图片、表格、代码等；也可粘贴截图自动上传。</p>
          <div class="article-md-editor-wrap">
            <MdEditor
              id="admin-article-md"
              v-model="form.body_markdown"
              language="zh-CN"
              preview-theme="github"
              :preview="true"
              :scroll-auto="true"
              no-prettier
              no-mermaid
              no-katex
              placeholder="在此编写正文…"
              :style="{ height: 'min(520px, 62vh)' }"
              @on-upload-img="onUploadImg"
            />
          </div>
        </el-form-item>
        <el-form-item label="置顶">
          <el-switch v-model="form.is_pinned" />
          <el-input-number v-model="form.pin_order" :min="0" :max="2" style="margin-left: 12px" />
          <span class="admin-form-hint--dialog">最多 3 条置顶</span>
        </el-form-item>
        <el-form-item label="是否推广">
          <el-switch v-model="form.is_promoted" />
          <span class="admin-form-hint--dialog">推广文章在列表中优先展示</span>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>

<style scoped>
.article-cover-thumb {
  width: 56px;
  height: 40px;
  border-radius: 6px;
  border: 1px solid var(--admin-border-soft, #eef2f6);
}
.article-md-form-item {
  align-items: flex-start;
}
.article-md-form-item :deep(.el-form-item__content) {
  display: block;
  width: 100%;
}
.article-md-hint {
  margin: 0 0 8px;
  font-size: var(--fs-caption);
  color: #94a3b8;
  line-height: 1.5;
}
.article-md-editor-wrap {
  width: 100%;
  border-radius: 8px;
  overflow: hidden;
  border: 1px solid var(--el-border-color);
}
.article-md-editor-wrap :deep(.md-editor) {
  border-radius: 8px;
}
.article-md-loading {
  padding: 28px 16px;
  text-align: center;
  color: #64748b;
  font-size: var(--fs-small);
  background: #f8fafc;
  border-radius: 8px;
}
</style>

<style>
/* 对话框内编辑器需突破 scoped，保证全宽与 z-index 正常 */
.el-dialog.admin-dialog.article-dialog .el-dialog__body {
  padding-top: 8px;
}

.el-dialog.admin-dialog.article-dialog {
  max-height: min(94vh, 960px);
}
</style>
