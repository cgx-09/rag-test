<script setup lang="ts">
defineProps<{
  fileName: string
  percent: number
  status: 'uploading' | 'processing' | 'done' | 'error'
  errorMessage?: string
}>()
</script>

<template>
  <div class="upload-progress card">
    <div class="progress-header">
      <span class="file-icon">{{ fileName.endsWith('.pdf') ? '📄' : '📝' }}</span>
      <span class="file-name">{{ fileName }}</span>
      <span class="file-status" :class="status">
        <template v-if="status === 'uploading'">上传中 {{ percent }}%</template>
        <template v-else-if="status === 'processing'">🔄 处理中...</template>
        <template v-else-if="status === 'done'">✅ 已完成</template>
        <template v-else-if="status === 'error'">❌ {{ errorMessage || '失败' }}</template>
      </span>
    </div>
    <div class="progress-bar" v-if="status === 'uploading' || status === 'processing'">
      <div
        class="progress-fill"
        :class="{ indeterminate: status === 'processing' }"
        :style="{ width: status === 'processing' ? '100%' : percent + '%' }"
      ></div>
    </div>
  </div>
</template>

<style scoped>
.upload-progress {
  padding: var(--space-md);
}

.progress-header {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  margin-bottom: var(--space-sm);
}

.file-icon {
  font-size: 18px;
}

.file-name {
  flex: 1;
  font-size: 14px;
  font-weight: 500;
  overflow: hidden;
  text-overflow: ellipsis;
  white-space: nowrap;
}

.file-status {
  font-size: 13px;
  color: var(--color-text-muted);
  flex-shrink: 0;
}

.file-status.done {
  color: var(--color-success);
}

.file-status.error {
  color: var(--color-error);
}

.progress-bar {
  height: 4px;
  background: var(--color-border-light);
  border-radius: 2px;
  overflow: hidden;
}

.progress-fill {
  height: 100%;
  background: var(--color-primary);
  border-radius: 2px;
  transition: width 0.3s ease;
}

.progress-fill.indeterminate {
  width: 40% !important;
  animation: indeterminate 1.2s ease-in-out infinite;
}

@keyframes indeterminate {
  0% { transform: translateX(-100%); }
  100% { transform: translateX(350%); }
}
</style>
