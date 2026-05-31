<script setup lang="ts">
import { computed } from 'vue'
import { boolCellTag, type BoolCellVariant } from '@/utils/boolDisplay'

const props = defineProps<{
  value: unknown
  variant: BoolCellVariant
}>()

const tag = computed(() => boolCellTag(props.variant, props.value))
</script>

<template>
  <el-tag v-if="tag" :type="tag.type" size="small">{{ tag.text }}</el-tag>
  <span v-else class="admin-cell-muted">—</span>
</template>
