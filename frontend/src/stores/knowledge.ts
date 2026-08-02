import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { DocumentInfo, KnowledgeStats, UploadResult } from '@/types'
import { getDocuments, getKnowledgeStats, deleteDocument, reindexDocument, uploadDocument } from '@/api'

export const useKnowledgeStore = defineStore('knowledge', () => {
  // ---- 状态 ----
  const documents = ref<DocumentInfo[]>([])
  const stats = ref<KnowledgeStats>({ totalDocs: 0, totalChunks: 0 })
  const loading = ref(false)
  const uploading = ref(false)
  const uploadProgress = ref(0)
  const uploadFileName = ref('')

  // ---- 计算属性 ----
  const readyDocs = computed(() => documents.value.filter((d) => d.status === 'ready'))
  const indexingDocs = computed(() => documents.value.filter((d) => d.status === 'indexing'))

  // ---- 方法 ----
  async function fetchDocuments(): Promise<void> {
    loading.value = true
    try {
      documents.value = await getDocuments()
    } catch (err) {
      console.error('获取文档列表失败:', err)
    } finally {
      loading.value = false
    }
  }

  async function fetchStats(): Promise<void> {
    try {
      stats.value = await getKnowledgeStats()
    } catch (err) {
      console.error('获取知识库统计失败:', err)
    }
  }

  async function removeDocument(id: string): Promise<void> {
    try {
      await deleteDocument(id)
      documents.value = documents.value.filter((d) => d.id !== id)
      await fetchStats()
    } catch (err) {
      console.error('删除文档失败:', err)
      throw err
    }
  }

  async function reindex(id: string): Promise<void> {
    try {
      await reindexDocument(id)
      const doc = documents.value.find((d) => d.id === id)
      if (doc) doc.status = 'indexing'
    } catch (err) {
      console.error('重新索引失败:', err)
      throw err
    }
  }

  function uploadFile(
    file: File,
    onDone?: (result: UploadResult) => void,
    onError?: (err: Error) => void
  ): void {
    uploading.value = true
    uploadProgress.value = 0
    uploadFileName.value = file.name

    uploadDocument(
      file,
      // onProgress
      (percent) => {
        uploadProgress.value = percent
      },
      // onDone
      (result) => {
        uploading.value = false
        uploadProgress.value = 0
        uploadFileName.value = ''
        onDone?.(result)
        fetchDocuments()
        fetchStats()
      },
      // onError
      (err) => {
        uploading.value = false
        uploadProgress.value = 0
        uploadFileName.value = ''
        onError?.(err)
      }
    )
  }

  return {
    documents,
    stats,
    loading,
    uploading,
    uploadProgress,
    uploadFileName,
    readyDocs,
    indexingDocs,
    fetchDocuments,
    fetchStats,
    removeDocument,
    reindex,
    uploadFile,
  }
})
