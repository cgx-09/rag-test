<script setup lang="ts">
import type { DocumentInfo } from '@/types'
import { ref } from 'vue'
import DeleteConfirm from './DeleteConfirm.vue'

const props = defineProps<{
  documents: DocumentInfo[]
  loading: boolean
}>()

const emit = defineEmits<{
  delete: [id: string]
  reindex: [id: string]
}>()

const deleteTarget = ref<{ id: string; name: string } | null>(null)

function formatSize(bytes: number): string {
  if (bytes < 1024) return bytes + ' B'
  if (bytes < 1024 * 1024) return (bytes / 1024).toFixed(1) + ' KB'
  return (bytes / 1024 / 1024).toFixed(1) + ' MB'
}

function handleConfirmDelete(): void {
  if (deleteTarget.value) {
    emit('delete', deleteTarget.value.id)
    deleteTarget.value = null
  }
}

function statusLabel(status: string): string {
  switch (status) {
    case 'ready': return '已就绪'
    case 'indexing': return '索引中'
    case 'error': return '失败'
    default: return status
  }
}
</script>

<template>
  <div class="docs-table card">
    <table>
      <thead>
        <tr>
          <th>文档名称</th>
          <th>大小</th>
          <th>状态</th>
          <th>上传时间</th>
          <th>操作</th>
        </tr>
      </thead>
      <tbody>
        <tr v-if="loading">
          <td colspan="5" class="loading-cell">加载中...</td>
        </tr>
        <tr v-else-if="documents.length === 0">
          <td colspan="5" class="empty-cell">
            暂无文档，<router-link to="/upload">去上传</router-link>
          </td>
        </tr>
        <tr v-for="doc in documents" :key="doc.id">
          <td class="name-cell">
            <span class="doc-icon">{{ doc.name.endsWith('.pdf') ? '📄' : '📝' }}</span>
            <span class="doc-name" :title="doc.name">{{ doc.name }}</span>
          </td>
          <td class="size-cell">{{ formatSize(doc.size) }}</td>
          <td>
            <span class="badge" :class="{
              'badge-success': doc.status === 'ready',
              'badge-warning': doc.status === 'indexing',
              'badge-error': doc.status === 'error',
            }">
              {{ statusLabel(doc.status) }}
            </span>
          </td>
          <td class="date-cell">{{ doc.uploadedAt }}</td>
          <td class="actions-cell">
            <button
              v-if="doc.status === 'ready'"
              class="btn btn-secondary btn-sm"
              @click="emit('reindex', doc.id)"
            >
              重新索引
            </button>
            <button
              class="btn btn-secondary btn-sm"
              style="color: var(--color-error)"
              @click="deleteTarget = { id: doc.id, name: doc.name }"
            >
              🗑
            </button>
          </td>
        </tr>
      </tbody>
    </table>
  </div>

  <DeleteConfirm
    :visible="deleteTarget !== null"
    :doc-name="deleteTarget?.name || ''"
    @cancel="deleteTarget = null"
    @confirm="handleConfirmDelete"
  />
</template>

<style scoped>
.docs-table {
  overflow: hidden;
}

table {
  width: 100%;
  border-collapse: collapse;
}

th {
  text-align: left;
  padding: var(--space-sm) var(--space-md);
  font-size: 12px;
  font-weight: 600;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  background: var(--color-border-light);
  border-bottom: 1px solid var(--color-border);
}

td {
  padding: var(--space-sm) var(--space-md);
  font-size: 14px;
  border-bottom: 1px solid var(--color-border-light);
}

tr:last-child td {
  border-bottom: none;
}

tr:hover td {
  background: var(--color-border-light);
}

.name-cell {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
}

.doc-icon {
  font-size: 16px;
  flex-shrink: 0;
}

.doc-name {
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  max-width: 300px;
}

.size-cell,
.date-cell {
  color: var(--color-text-secondary);
  font-size: 13px;
}

.actions-cell {
  display: flex;
  gap: var(--space-xs);
}

.loading-cell,
.empty-cell {
  text-align: center;
  padding: var(--space-xl);
  color: var(--color-text-muted);
}
</style>
