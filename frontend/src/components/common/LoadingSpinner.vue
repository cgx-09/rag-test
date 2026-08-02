<script setup lang="ts">
defineProps<{
  size?: 'sm' | 'md' | 'lg'
  text?: string
}>()
</script>

<template>
  <div class="spinner-container" :class="size || 'md'">
    <div class="spinner"></div>
    <span v-if="text" class="spinner-text">{{ text }}</span>
  </div>
</template>

<style scoped>
.spinner-container {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  gap: var(--space-sm);
  padding: var(--space-lg);
}

.spinner-container.sm { padding: var(--space-sm); }
.spinner-container.md { padding: var(--space-lg); }
.spinner-container.lg { padding: var(--space-xl); }

.spinner {
  width: 28px;
  height: 28px;
  border: 3px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 0.7s linear infinite;
}

.spinner-container.sm .spinner {
  width: 18px;
  height: 18px;
  border-width: 2px;
}

.spinner-container.lg .spinner {
  width: 40px;
  height: 40px;
  border-width: 4px;
}

.spinner-text {
  font-size: 13px;
  color: var(--color-text-muted);
}

@keyframes spin {
  to { transform: rotate(360deg); }
}
</style>
