<script setup lang="ts">
import { onMounted } from 'vue'
import { useKnowledgeStore } from '@/stores/knowledge'
import { storeToRefs } from 'pinia'
import DocsTable from '@/components/docs/DocsTable.vue'

const knowledgeStore = useKnowledgeStore()
const { documents, loading } = storeToRefs(knowledgeStore)

onMounted(() => {
  knowledgeStore.fetchDocuments()
})

function handleDelete(id: string): void {
  knowledgeStore.removeDocument(id)
}

function handleReindex(id: string): void {
  knowledgeStore.reindex(id)
}
</script>

<template>
  <div class="page-container">
    <div class="page-header">
      <h1 class="page-title">📋 文档管理</h1>
      <router-link to="/upload" class="btn btn-primary btn-sm">
        + 上传文档
      </router-link>
    </div>

    <DocsTable
      :documents="documents"
      :loading="loading"
      @delete="handleDelete"
      @reindex="handleReindex"
    />
  </div>
</template>

<style scoped>
.page-header {
  display: flex;
  align-items: center;
  justify-content: space-between;
  margin-bottom: var(--space-lg);
}

.page-header .page-title {
  margin-bottom: 0;
}
</style>
