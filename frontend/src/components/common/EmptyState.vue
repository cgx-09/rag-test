<script setup lang="ts">
defineProps<{
  icon?: string
  title: string
  description?: string
  action?: string
  actionTo?: string
}>()

defineEmits<{
  actionClick: []
}>()
</script>

<template>
  <div class="empty-state">
    <span class="empty-icon">{{ icon || '📭' }}</span>
    <h3 class="empty-title">{{ title }}</h3>
    <p v-if="description" class="empty-desc">{{ description }}</p>
    <router-link
      v-if="action && actionTo"
      :to="actionTo"
      class="btn btn-primary btn-sm"
    >
      {{ action }}
    </router-link>
    <button
      v-else-if="action"
      class="btn btn-primary btn-sm"
      @click="$emit('actionClick')"
    >
      {{ action }}
    </button>
  </div>
</template>

<style scoped>
.empty-state {
  display: flex;
  flex-direction: column;
  align-items: center;
  justify-content: center;
  padding: var(--space-2xl) var(--space-lg);
  text-align: center;
}

.empty-icon {
  font-size: 48px;
  margin-bottom: var(--space-md);
}

.empty-title {
  font-size: 16px;
  font-weight: 600;
  margin-bottom: var(--space-xs);
}

.empty-desc {
  font-size: 14px;
  color: var(--color-text-secondary);
  margin-bottom: var(--space-md);
  max-width: 300px;
}
</style>
