<script setup lang="ts">
import { ref, nextTick } from 'vue'

const emit = defineEmits<{
  send: [text: string]
}>()

const inputText = ref('')
const textareaRef = ref<HTMLTextAreaElement>()

function handleSend(): void {
  const text = inputText.value.trim()
  if (!text) return
  emit('send', text)
  inputText.value = ''
  nextTick(() => textareaRef.value?.focus())
}

function handleKeydown(e: KeyboardEvent): void {
  if (e.key === 'Enter' && !e.shiftKey) {
    e.preventDefault()
    handleSend()
  }
}

// 自动调整 textarea 高度
function autoResize(): void {
  const el = textareaRef.value
  if (!el) return
  el.style.height = 'auto'
  el.style.height = Math.min(el.scrollHeight, 150) + 'px'
}
</script>

<template>
  <div class="chat-input">
    <div class="input-wrapper">
      <textarea
        ref="textareaRef"
        v-model="inputText"
        class="input-textarea"
        placeholder="输入你的问题，按 Enter 发送，Shift+Enter 换行..."
        rows="1"
        @keydown="handleKeydown"
        @input="autoResize"
      ></textarea>
      <button
        class="send-btn"
        :disabled="!inputText.trim()"
        @click="handleSend"
        title="发送"
      >
        ➤
      </button>
    </div>
    <div class="input-hint">
      Enter 发送 · Shift+Enter 换行
    </div>
  </div>
</template>

<style scoped>
.chat-input {
  padding: var(--space-md) var(--space-lg);
  border-top: 1px solid var(--color-border);
  background: var(--color-surface);
}

.input-wrapper {
  display: flex;
  align-items: flex-end;
  gap: var(--space-sm);
  padding: var(--space-sm) var(--space-md);
  border: 1px solid var(--color-border);
  border-radius: var(--radius-md);
  background: var(--color-bg);
  transition: border-color var(--transition-fast);
}

.input-wrapper:focus-within {
  border-color: var(--color-primary);
  box-shadow: 0 0 0 3px var(--color-primary-bg);
}

.input-textarea {
  flex: 1;
  resize: none;
  background: transparent;
  font-size: 14px;
  line-height: 1.5;
  color: var(--color-text);
  padding: 4px 0;
  max-height: 150px;
}

.input-textarea::placeholder {
  color: var(--color-text-muted);
}

.send-btn {
  width: 32px;
  height: 32px;
  min-width: 32px;
  border-radius: var(--radius-full);
  background: var(--color-primary);
  color: #fff;
  font-size: 14px;
  display: flex;
  align-items: center;
  justify-content: center;
  transition: all var(--transition-fast);
}

.send-btn:hover:not(:disabled) {
  background: var(--color-primary-dark);
  transform: scale(1.05);
}

.send-btn:disabled {
  background: var(--color-border);
  color: var(--color-text-muted);
}

.input-hint {
  font-size: 11px;
  color: var(--color-text-muted);
  text-align: center;
  margin-top: 6px;
}
</style>
