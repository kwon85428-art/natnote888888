<script setup lang="ts">
import type { Component } from 'vue'
import { onMounted } from 'vue'
import AdminBoolCell from '@/components/admin/AdminBoolCell.vue'
import { siteCategoriesApi } from '@/api/admin/siteCategories'
import { useAdminCategoryCrud } from '@/composables/useAdminCategoryCrud'
import type { SiteCategoryItem } from '@/types/models'
import CategoryIconPicker from '@/components/admin/CategoryIconPicker.vue'
import { categoryIconComponent } from '@/utils/categoryIcons'
import { Compass } from '@element-plus/icons-vue'

type SiteCategoryForm = {
  id: number | null
  name: string
  icon_key: string
  description: string
  sort_order: number
  enabled: boolean
}

function toPayload(form: SiteCategoryForm) {
  return {
    name: form.name,
    icon_key: form.icon_key || null,
    description: form.description,
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
} = useAdminCategoryCrud<SiteCategoryItem, ReturnType<typeof toPayload>, SiteCategoryForm>({
  api: siteCategoriesApi,
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
    sort_order: row.sort_order,
    enabled: row.enabled,
  }),
  toPayload,
  deleteConfirm: '确定删除？下属网站将移入未分类。',
})

function iconComp(key: string | null | undefined): Component | null {
  return categoryIconComponent(key || undefined)
}

onMounted(() => {
  void load()
})
</script>

<template>
  <div class="admin-page">
    <header class="admin-page-head">
      <h1 class="admin-page-title">网址分类</h1>
      <p class="admin-page-desc">维护前台导航中的网址分组、排序与启用状态；系统内置分类不可删除。</p>
    </header>
    <div class="admin-stack">
      <div class="toolbar">
        <el-button type="primary" @click="openCreate">新增分类</el-button>
      </div>
      <el-table :data="list" stripe class="admin-table" size="small">
      <el-table-column prop="id" label="ID" width="70" />
      <el-table-column label="图标" width="72" align="center">
        <template #default="{ row }">
          <span v-if="iconComp(row.icon_key)" class="admin-icon-cell">
            <el-icon :size="18"><component :is="iconComp(row.icon_key)" /></el-icon>
          </span>
          <span v-else class="admin-icon-cell admin-icon-cell--muted">
            <el-icon :size="18"><Compass /></el-icon>
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
            <el-button v-if="!row.is_system" link type="danger" @click="removeRow(row)">删除</el-button>
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
      :title="form.id ? '编辑分类' : '新增分类'"
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
          <el-input v-model="form.description" type="textarea" :rows="2" />
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
