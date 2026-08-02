<script setup lang="ts">
import type { DocumentInfo } from '@/types'

defineProps<{
  documents: DocumentInfo[]
}>()
</script>

<template>
  <div class="upload-history">
    <h3 class="history-title">最近上传</h3>

    <div v-if="documents.length === 0" class="history-empty">
      暂无上传记录
    </div>

    <div v-else class="history-list">
      <div
        v-for="doc in documents.slice().reverse()"
        :key="doc.id"
        class="history-item"
      >
        <span class="doc-icon">{{ doc.name.endsWith('.pdf') ? '📄' : '📝' }}</span>
        <span class="doc-name">{{ doc.name }}</span>
        <span class="doc-size">{{ (doc.size / 1024).toFixed(1) }} KB</span>
        <span class="doc-status" :class="doc.status">
          {{ doc.status === 'ready' ? '✅' : doc.status === 'indexing' ? '🔄' : '❌' }}
        </span>
        <span class="doc-date">{{ doc.uploadedAt }}</span>
      </div>
    </div>
  </div>
</template>

<style scoped>
.upload-history {
  margin-top: var(--space-xl);
}

.history-title {
  font-size: 15px;
  font-weight: 600;
  margin-bottom: var(--space-md);
}

.history-empty {
  font-size: 14px;
  color: var(--color-text-muted);
  text-align: center;
  padding: var(--space-lg);
}

.history-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.history-item {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-sm) var(--space-md);
  background: var(--color-surface);
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-sm);
  font-size: 13px;
}

.doc-icon {
  font-size: 16px;
}

.doc-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--color-text);
}

.doc-size {
  color: var(--color-text-muted);
  font-size: 12px;
}

.doc-date {
  color: var(--color-text-muted);
  font-size: 12px;
}
</style>
