<script setup lang="ts">
import type { Citation } from '@/types'
import { ref } from 'vue'

defineProps<{
  sources: Citation[]
}>()

const expandedIndex = ref<number | null>(null)

function toggleExpand(index: number): void {
  expandedIndex.value = expandedIndex.value === index ? null : index
}
</script>

<template>
  <div class="source-citations">
    <div class="source-header">
      <span class="source-icon">📎</span>
      <span class="source-label">参考来源（{{ sources.length }}）</span>
    </div>
    <div class="source-list">
      <div
        v-for="(source, index) in sources"
        :key="index"
        class="source-item"
        :class="{ expanded: expandedIndex === index }"
        @click="toggleExpand(index)"
      >
        <div class="source-item-header">
          <span class="source-doc">{{ source.documentName }}</span>
          <span class="source-chunk">第 {{ source.chunkIndex }} 段</span>
          <span class="source-toggle">{{ expandedIndex === index ? '▲' : '▼' }}</span>
        </div>
        <div v-if="expandedIndex === index" class="source-content fade-in">
          {{ source.content }}
        </div>
      </div>
    </div>
  </div>
</template>

<style scoped>
.source-citations {
  margin-top: var(--space-md);
  padding-top: var(--space-md);
  border-top: 1px solid var(--color-border-light);
}

.source-header {
  display: flex;
  align-items: center;
  gap: var(--space-xs);
  margin-bottom: var(--space-sm);
}

.source-icon {
  font-size: 14px;
}

.source-label {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-text-muted);
}

.source-list {
  display: flex;
  flex-direction: column;
  gap: 4px;
}

.source-item {
  border: 1px solid var(--color-border-light);
  border-radius: var(--radius-sm);
  overflow: hidden;
  cursor: pointer;
  transition: border-color var(--transition-fast);
}

.source-item:hover {
  border-color: var(--color-primary-light);
}

.source-item.expanded {
  border-color: var(--color-primary);
}

.source-item-header {
  display: flex;
  align-items: center;
  gap: var(--space-sm);
  padding: var(--space-sm) var(--space-md);
  font-size: 13px;
}

.source-doc {
  flex: 1;
  font-weight: 500;
  color: var(--color-text);
}

.source-chunk {
  font-size: 11px;
  color: var(--color-text-muted);
  background: var(--color-border-light);
  padding: 1px 6px;
  border-radius: var(--radius-full);
}

.source-toggle {
  font-size: 10px;
  color: var(--color-text-muted);
}

.source-content {
  padding: var(--space-sm) var(--space-md) var(--space-md);
  font-size: 13px;
  color: var(--color-text-secondary);
  line-height: 1.7;
  background: var(--color-border-light);
  border-top: 1px solid var(--color-border-light);
}
</style>
