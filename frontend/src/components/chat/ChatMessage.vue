<script setup lang="ts">
import type { Message } from '@/types'
import SourceCitation from './SourceCitation.vue'

defineProps<{
  message: Message
}>()
</script>

<template>
  <div class="chat-message" :class="message.role">
    <div class="message-avatar">
      {{ message.role === 'user' ? '👤' : '🤖' }}
    </div>
    <div class="message-body">
      <div class="message-role">
        {{ message.role === 'user' ? '你' : '助手' }}
      </div>
      <div class="message-content markdown-body" v-text="message.content"></div>
      <SourceCitation
        v-if="message.sources && message.sources.length"
        :sources="message.sources"
      />
    </div>
  </div>
</template>

<style scoped>
.chat-message {
  display: flex;
  gap: var(--space-md);
  padding: var(--space-md) 0;
  animation: fadeIn var(--transition-base) ease forwards;
}

.chat-message.user {
  flex-direction: row-reverse;
}

.message-avatar {
  width: 36px;
  height: 36px;
  min-width: 36px;
  border-radius: var(--radius-full);
  background: var(--color-border-light);
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 18px;
}

.chat-message.user .message-avatar {
  background: var(--color-primary-bg);
}

.message-body {
  max-width: 75%;
  min-width: 0;
}

.chat-message.user .message-body {
  text-align: right;
}

.message-role {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-text-muted);
  margin-bottom: 4px;
}

.chat-message.user .message-role {
  color: var(--color-primary);
}

.message-content {
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  border: 1px solid var(--color-border-light);
  font-size: 14px;
}

.chat-message.user .message-content {
  background: var(--color-primary-bg);
  border-color: transparent;
  color: var(--color-text);
}
</style>
