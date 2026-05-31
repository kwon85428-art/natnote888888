<script setup lang="ts">
import type { Component } from 'vue'
import { onMounted } from 'vue'
import AdminBoolCell from '@/components/admin/AdminBoolCell.vue'
import { articleCategoriesApi } from '@/api/admin/articleCategories'
import { useAdminCategoryCrud } from '@/composables/useAdminCategoryCrud'
import type { ArticleCategoryItem } from '@/types/models'
import CategoryIconPicker from '@/components/admin/CategoryIconPicker.vue'
import { categoryIconComponent } from '@/utils/categoryIcons'
import { Reading } from '@element-plus/icons-vue'

type ArticleCategoryForm = {
  id: number | null
  name: string
  icon_key: string
  description: string
  sort_order: number
  enabled: boolean
}

function toPayload(form: ArticleCategoryForm) {
  return {
    name: form.name,
    icon_key: form.icon_key || null,
    description: form.description.trim() || null,
    sort_order: form.sort_order,
    enabled: form.enabled,
  }
}

const {
  list,
  page,
  pageSize,
  total,
  dialog,
  form,
  load,
  openCreate,
  openEdit,
  save,
  removeRow,
  onPageSizeChange,
} = useAdminCategoryCrud<ArticleCategoryItem, ReturnType<typeof toPayload>, ArticleCategoryForm>({
  api: articleCategoriesApi,
  emptyForm: () => ({
    id: null,
    name: '',
    icon_key: '',
    description: '',
    sort_order: 0,
    enabled: true,
  }),
  formFromRow: (row) => ({
    id: row.id,
    name: row.name,
    icon_key: row.icon_key || '',
    description: row.description || '',
    sort_order: row.sort_order ?? 0,
    enabled: row.enabled ?? true,
  }),
  toPayload,
})

function iconComp(key: string | null | undefined): Component {
  return categoryIconComponent(key || undefined) || Reading
}

onMounted(() => {
  void load()
})
</script>

<template>
  <div class="admin-page">
    <header class="admin-page-head">
      <h1 class="admin-page-title">文章分类</h1>
      <p class="admin-page-desc">维护文章栏目的名称、描述、图标、排序与启用状态，用于前台侧栏与分类标签。</p>
    </header>
    <div class="admin-stack">
      <div class="toolbar">
        <el-button type="primary" @click="openCreate">新增文章分类</el-button>
      </div>
      <el-table :data="list" stripe class="admin-table" size="small">
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column label="图标" width="72" align="center">
        <template #default="{ row }">
          <span class="admin-icon-cell">
            <el-icon :size="18"><component :is="iconComp(row.icon_key)" /></el-icon>
          </span>
        </template>
      </el-table-column>
      <el-table-column prop="name" label="名称" min-width="140" />
      <el-table-column prop="description" label="描述" min-width="180" show-overflow-tooltip />
      <el-table-column prop="sort_order" label="排序" width="90" />
      <el-table-column label="启用" width="90" align="center">
        <template #default="{ row }">
          <AdminBoolCell :value="row.enabled" variant="yesno" />
        </template>
      </el-table-column>
      <el-table-column label="操作" width="160" fixed="right">
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
          background
          layout="total, sizes, prev, pager, next"
          :total="total"
          :page-size="pageSize"
          :current-page="page"
          :page-sizes="[10, 20, 50]"
          @size-change="onPageSizeChange"
          @current-change="(p: number) => { page = p; load() }"
        />
      </div>
    </div>

    <el-dialog
      v-model="dialog"
      :title="form.id ? '编辑文章分类' : '新增文章分类'"
      width="480px"
      class="admin-dialog"
      append-to-body
      align-center
      destroy-on-close
    >
      <el-form class="admin-form" label-width="96px" label-position="right">
        <el-form-item label="名称" required>
          <el-input v-model="form.name" />
        </el-form-item>
        <el-form-item label="图标">
          <CategoryIconPicker v-model="form.icon_key" />
        </el-form-item>
        <el-form-item label="描述">
          <el-input v-model="form.description" type="textarea" :rows="2" placeholder="前台侧栏与分类抽屉中展示" />
        </el-form-item>
        <el-form-item label="排序">
          <el-input-number v-model="form.sort_order" :min="0" />
        </el-form-item>
        <el-form-item label="启用">
          <el-switch v-model="form.enabled" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="dialog = false">取消</el-button>
        <el-button type="primary" @click="save">保存</el-button>
      </template>
    </el-dialog>
  </div>
</template>
