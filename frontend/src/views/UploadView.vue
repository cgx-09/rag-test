<script setup lang="ts">
import { ref, onMounted } from 'vue'
import { useKnowledgeStore } from '@/stores/knowledge'
import { storeToRefs } from 'pinia'
import DropZone from '@/components/upload/DropZone.vue'
import UploadProgress from '@/components/upload/UploadProgress.vue'
import UploadHistory from '@/components/upload/UploadHistory.vue'

const knowledgeStore = useKnowledgeStore()
const { documents, uploading, uploadProgress, uploadFileName } = storeToRefs(knowledgeStore)

const uploadStatus = ref<'uploading' | 'processing' | 'done' | 'error'>('done')
const errorMessage = ref('')

onMounted(() => {
  knowledgeStore.fetchDocuments()
})

function handleFileSelect(file: File): void {
  uploadStatus.value = 'uploading'
  errorMessage.value = ''

  knowledgeStore.uploadFile(
    file,
    () => {
      uploadStatus.value = 'done'
      // 3 秒后隐藏完成状态
      setTimeout(() => {
        uploadStatus.value = 'done'
      }, 3000)
    },
    (err) => {
      uploadStatus.value = 'error'
      errorMessage.value = err.message
    }
  )
}
</script>

<template>
  <div class="upload-page">
    <div class="upload-header">
      <h1 class="page-title">📤 上传文档</h1>
    </div>

    <div class="upload-layout">
      <DropZone @file-select="handleFileSelect" />

      <UploadProgress
        v-if="uploadStatus !== 'done' || uploading"
        :file-name="uploadFileName"
        :percent="uploadProgress"
        :status="uploadStatus"
        :error-message="errorMessage"
      />

      <UploadHistory :documents="documents" />
    </div>
  </div>
</template>

<style scoped>
.upload-page {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  height: 100%;
  padding: var(--space-lg);
}

.upload-header {
  text-align: center;
  margin-bottom: var(--space-lg);
}

.upload-header .page-title {
  margin-bottom: 0;
}

.upload-layout {
  width: 100%;
  max-width: 600px;
  display: flex;
  flex-direction: column;
  gap: var(--space-md);
}
</style>
