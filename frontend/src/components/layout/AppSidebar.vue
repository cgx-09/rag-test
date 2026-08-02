<script setup lang="ts">
import { useKnowledgeStore } from '@/stores/knowledge'
import { storeToRefs } from 'pinia'
import { onMounted } from 'vue'

const knowledgeStore = useKnowledgeStore()
const { documents, stats, loading } = storeToRefs(knowledgeStore)

onMounted(() => {
  knowledgeStore.fetchDocuments()
  knowledgeStore.fetchStats()
})
</script>

<template>
  <aside class="sidebar">
    <div class="sidebar-header">
      <h3 class="sidebar-title">📚 知识库</h3>
    </div>

    <div class="sidebar-stats">
      <div class="stat-item">
        <span class="stat-value">{{ stats.totalDocs }}</span>
        <span class="stat-label">文档</span>
      </div>
      <div class="stat-item">
        <span class="stat-value">{{ stats.totalChunks }}</span>
        <span class="stat-label">文本块</span>
      </div>
    </div>

    <div class="sidebar-divider"></div>

    <div class="sidebar-section">
      <div class="section-label">已上传文档</div>
      <div v-if="loading" class="sidebar-loading">加载中...</div>
      <ul v-else-if="documents.length" class="doc-list">
        <li v-for="doc in documents" :key="doc.id" class="doc-item">
          <span class="doc-icon">
            {{ doc.name.endsWith('.pdf') ? '📄' : '📝' }}
          </span>
          <span class="doc-name" :title="doc.name">{{ doc.name }}</span>
          <span class="doc-badge" :class="doc.status === 'ready' ? 'ready' : 'indexing'">
            {{ doc.status === 'ready' ? '✅' : '🔄' }}
          </span>
        </li>
      </ul>
      <div v-else class="sidebar-empty">暂无文档</div>
    </div>

    <div class="sidebar-footer">
      <router-link to="/upload" class="btn btn-primary btn-sm" style="width: 100%">
        + 上传文档
      </router-link>
    </div>
  </aside>
</template>

<style scoped>
.sidebar {
  width: 260px;
  min-width: 260px;
  height: 100%;
  background: var(--color-surface);
  border-right: 1px solid var(--color-border);
  display: flex;
  flex-direction: column;
  overflow: hidden;
}

.sidebar-header {
  padding: var(--space-md) var(--space-lg);
}

.sidebar-title {
  font-size: 15px;
  font-weight: 600;
}

.sidebar-stats {
  display: flex;
  gap: var(--space-sm);
  padding: 0 var(--space-lg) var(--space-md);
}

.stat-item {
  flex: 1;
  text-align: center;
  padding: var(--space-sm);
  background: var(--color-border-light);
  border-radius: var(--radius-sm);
}

.stat-value {
  display: block;
  font-size: 18px;
  font-weight: 700;
  color: var(--color-primary);
}

.stat-label {
  font-size: 11px;
  color: var(--color-text-muted);
}

.sidebar-divider {
  height: 1px;
  background: var(--color-border-light);
  margin: 0 var(--space-lg);
}

.sidebar-section {
  flex: 1;
  overflow-y: auto;
  padding: var(--space-md) var(--space-lg);
}

.section-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-text-muted);
  text-transform: uppercase;
  letter-spacing: 0.5px;
  margin-bottom: var(--space-sm);
}

.sidebar-loading {
  font-size: 13px;
  color: var(--color-text-muted);
  padding: var(--space-sm) 0;
}

.doc-list {
  display: flex;
  flex-direction: column;
  gap: 2px;
}

.doc-item {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: 6px 8px;
  border-radius: var(--radius-sm);
  font-size: 13px;
  transition: background var(--transition-fast);
}

.doc-item:hover {
  background: var(--color-border-light);
}

.doc-icon {
  font-size: 14px;
  flex-shrink: 0;
}

.doc-name {
  flex: 1;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
  color: var(--color-text-secondary);
}

.doc-badge {
  font-size: 12px;
  flex-shrink: 0;
}

.sidebar-empty {
  font-size: 13px;
  color: var(--color-text-muted);
  padding: var(--space-sm) 0;
}

.sidebar-footer {
  padding: var(--space-md) var(--space-lg);
  border-top: 1px solid var(--color-border-light);
}
</style>
