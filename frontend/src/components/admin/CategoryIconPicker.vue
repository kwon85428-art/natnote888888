<script setup lang="ts">
import { computed, ref } from 'vue'
import { ArrowDown, Close, Search } from '@element-plus/icons-vue'
import {
  CATEGORY_ICONS,
  categoryIconComponent,
  categoryIconLabel,
} from '@/utils/categoryIcons'

const model = defineModel<string>({ default: '' })

const open = ref(false)
const query = ref('')

const filteredIcons = computed(() => {
  const q = query.value.trim().toLowerCase()
  if (!q) return CATEGORY_ICONS
  return CATEGORY_ICONS.filter(
    (item) => item.label.toLowerCase().includes(q) || item.key.toLowerCase().includes(q),
  )
})

const selectedComponent = computed(() => categoryIconComponent(model.value || undefined))
const selectedLabel = computed(() => categoryIconLabel(model.value || undefined))

function selectIcon(key: string) {
  model.value = key
  open.value = false
  query.value = ''
}

function clearIcon() {
  model.value = ''
  open.value = false
  query.value = ''
}

function onPopoverShow() {
  query.value = ''
}
</script>

<template>
  <el-popover
    v-model:visible="open"
    :width="380"
    trigger="click"
    placement="bottom-start"
    :show-arrow="false"
    popper-class="category-icon-picker-popper"
    @show="onPopoverShow"
  >
    <template #reference>
      <button type="button" class="icon-picker-trigger" :class="{ 'is-empty': !model }">
        <span class="icon-picker-trigger__preview">
          <el-icon v-if="selectedComponent" :size="20" class="icon-picker-trigger__ico">
            <component :is="selectedComponent" />
          </el-icon>
          <span v-else class="icon-picker-trigger__placeholder">选图标</span>
        </span>
        <span class="icon-picker-trigger__label">{{ selectedLabel }}</span>
        <el-icon class="icon-picker-trigger__arrow" :size="14"><ArrowDown /></el-icon>
      </button>
    </template>

    <div class="icon-picker-panel">
      <div class="icon-picker-panel__search">
        <el-input
          v-model="query"
          placeholder="搜索图标名称或 key"
          clearable
          size="small"
          :prefix-icon="Search"
        />
      </div>

      <div v-if="filteredIcons.length === 0" class="icon-picker-panel__empty">无匹配图标</div>

      <div v-else class="icon-picker-grid" role="listbox" aria-label="分类图标">
        <button
          type="button"
          class="icon-picker-cell icon-picker-cell--none"
          :class="{ 'is-selected': !model }"
          role="option"
          :aria-selected="!model"
          @click="clearIcon"
        >
          <el-icon :size="20"><Close /></el-icon>
          <span class="icon-picker-cell__label">无</span>
        </button>

        <button
          v-for="item in filteredIcons"
          :key="item.key"
          type="button"
          class="icon-picker-cell"
          :class="{ 'is-selected': model === item.key }"
          role="option"
          :aria-selected="model === item.key"
          :title="item.label"
          @click="selectIcon(item.key)"
        >
          <el-icon :size="20" class="icon-picker-cell__ico">
            <component :is="item.component" />
          </el-icon>
          <span class="icon-picker-cell__label">{{ item.label }}</span>
        </button>
      </div>
    </div>
  </el-popover>
</template>

<style scoped>
.icon-picker-trigger {
  display: inline-flex;
  align-items: center;
  gap: 10px;
  width: 100%;
  max-width: 280px;
  padding: 8px 12px;
  border: 1px solid var(--admin-border, #e5e7eb);
  border-radius: 8px;
  background: #fff;
  color: var(--admin-text, #0f172a);
  cursor: pointer;
  transition:
    border-color 0.15s ease,
    box-shadow 0.15s ease;
}

.icon-picker-trigger:hover {
  border-color: #93c5fd;
}

.icon-picker-trigger:focus-visible {
  outline: 2px solid #93c5fd;
  outline-offset: 1px;
}

.icon-picker-trigger.is-empty .icon-picker-trigger__label {
  color: var(--admin-muted, #64748b);
}

.icon-picker-trigger__preview {
  display: inline-flex;
  align-items: center;
  justify-content: center;
  width: 32px;
  height: 32px;
  border-radius: 8px;
  background: var(--admin-accent-soft, #eff6ff);
  flex-shrink: 0;
}

.icon-picker-trigger__ico {
  color: var(--admin-accent, #1d4ed8);
}

.icon-picker-trigger__placeholder {
  font-size: var(--fs-micro);
  color: var(--admin-muted, #64748b);
}

.icon-picker-trigger__label {
  flex: 1;
  min-width: 0;
  text-align: left;
  font-size: var(--fs-small);
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}

.icon-picker-trigger__arrow {
  color: var(--admin-muted, #64748b);
  flex-shrink: 0;
}

.icon-picker-panel__search {
  margin-bottom: 10px;
}

.icon-picker-panel__empty {
  padding: 24px 8px;
  text-align: center;
  font-size: var(--fs-caption);
  color: var(--admin-muted, #64748b);
}

.icon-picker-grid {
  display: grid;
  grid-template-columns: repeat(5, minmax(0, 1fr));
  gap: 6px;
  max-height: 280px;
  overflow-y: auto;
  padding: 2px;
}

.icon-picker-cell {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: 4px;
  min-height: 68px;
  padding: 6px 4px;
  border: 1px solid transparent;
  border-radius: 8px;
  background: #f8fafc;
  color: #334155;
  cursor: pointer;
  transition:
    background 0.12s ease,
    border-color 0.12s ease,
    color 0.12s ease;
}

.icon-picker-cell:hover {
  background: #eff6ff;
  border-color: #bfdbfe;
}

.icon-picker-cell.is-selected {
  background: var(--admin-accent-soft, #eff6ff);
  border-color: var(--admin-accent, #1d4ed8);
  color: var(--admin-accent, #1d4ed8);
}

.icon-picker-cell--none {
  background: #fff;
  border-style: dashed;
  border-color: #cbd5e1;
  color: #64748b;
}

.icon-picker-cell--none.is-selected {
  border-style: solid;
}

.icon-picker-cell__ico {
  flex-shrink: 0;
}

.icon-picker-cell__label {
  max-width: 100%;
  font-size: var(--fs-micro);
  line-height: 1.2;
  text-align: center;
  white-space: nowrap;
  overflow: hidden;
  text-overflow: ellipsis;
}
</style>

<style>
.category-icon-picker-popper.el-popover.el-popper {
  padding: 12px;
  border-radius: 10px;
  box-shadow: 0 8px 24px rgba(15, 23, 42, 0.12);
}
</style>
