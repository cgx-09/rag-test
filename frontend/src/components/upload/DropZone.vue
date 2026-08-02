<script setup lang="ts">
import { ref } from 'vue'

const emit = defineEmits<{
  fileSelect: [file: File]
}>()

const isDragging = ref(false)
const dragCounter = ref(0)

const ACCEPTED_TYPES = ['.pdf', '.txt', '.md']
const MAX_SIZE = 20 * 1024 * 1024 // 20MB

function validateFile(file: File): string | null {
  const ext = '.' + file.name.split('.').pop()?.toLowerCase()
  if (!ACCEPTED_TYPES.includes(ext)) {
    return `不支持的文件格式：${ext}，请上传 PDF、TXT 或 MD 文件`
  }
  if (file.size > MAX_SIZE) {
    return `文件过大（${(file.size / 1024 / 1024).toFixed(1)}MB），最大支持 20MB`
  }
  return null
}

function handleDragenter(e: DragEvent): void {
  e.preventDefault()
  dragCounter.value++
  isDragging.value = true
}

function handleDragleave(e: DragEvent): void {
  e.preventDefault()
  dragCounter.value--
  if (dragCounter.value === 0) {
    isDragging.value = false
  }
}

function handleDragover(e: DragEvent): void {
  e.preventDefault()
}

function handleDrop(e: DragEvent): void {
  e.preventDefault()
  isDragging.value = false
  dragCounter.value = 0

  const files = e.dataTransfer?.files
  if (files && files.length > 0) {
    const error = validateFile(files[0])
    if (error) {
      alert(error)
      return
    }
    emit('fileSelect', files[0])
  }
}

function handleFileInput(e: Event): void {
  const input = e.target as HTMLInputElement
  const files = input.files
  if (files && files.length > 0) {
    emit('fileSelect', files[0])
  }
  input.value = ''
}
</script>

<template>
  <div
    class="drop-zone card"
    :class="{ dragging: isDragging }"
    @dragenter="handleDragenter"
    @dragleave="handleDragleave"
    @dragover="handleDragover"
    @drop="handleDrop"
  >
    <div class="drop-content">
      <span class="drop-icon">📂</span>
      <h3 class="drop-title">拖拽文件到此处上传</h3>
      <p class="drop-desc">支持 PDF、TXT、MD 格式，单个文件最大 20MB</p>
      <label class="btn btn-primary">
        选择文件
        <input
          type="file"
          class="file-input"
          accept=".pdf,.txt,.md"
          @change="handleFileInput"
        />
      </label>
    </div>
  </div>
</template>

<style scoped>
.drop-zone {
  padding: var(--space-2xl);
  text-align: center;
  border: 2px dashed var(--color-border);
  border-radius: var(--radius-lg);
  transition: all var(--transition-base);
  cursor: pointer;
}

.drop-zone:hover,
.drop-zone.dragging {
  border-color: var(--color-primary);
  background: var(--color-primary-bg);
}

.drop-content {
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: var(--space-sm);
}

.drop-icon {
  font-size: 48px;
}

.drop-title {
  font-size: 18px;
  font-weight: 600;
}

.drop-desc {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin-bottom: var(--space-sm);
}

.file-input {
  display: none;
}
</style>
