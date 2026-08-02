<script setup lang="ts">
import { ref, watch, nextTick } from 'vue'
import { useChatStore } from '@/stores/chat'
import { storeToRefs } from 'pinia'
import ChatMessage from './ChatMessage.vue'
import StreamingText from './StreamingText.vue'
import ChatInput from './ChatInput.vue'
import EmptyState from '@/components/common/EmptyState.vue'

const chatStore = useChatStore()
const { messages, isStreaming, streamingContent } = storeToRefs(chatStore)

const messagesContainer = ref<HTMLElement>()

// 自动滚动到底部
watch(
  () => [messages.value.length, streamingContent.value],
  async () => {
    await nextTick()
    if (messagesContainer.value) {
      messagesContainer.value.scrollTop = messagesContainer.value.scrollHeight
    }
  },
  { deep: false }
)

function handleSend(text: string): void {
  chatStore.sendMessage(text)
}
</script>

<template>
  <div class="chat-panel">
    <!-- 消息列表 -->
    <div ref="messagesContainer" class="messages-container">
      <EmptyState
        v-if="messages.length === 0 && !isStreaming"
        icon="💬"
        title="开始对话"
        description="在下方输入你的问题，助手将基于知识库中的文档为你解答"
      />

      <div v-else class="messages-list">
        <ChatMessage
          v-for="msg in messages"
          :key="msg.id"
          :message="msg"
        />

        <!-- 流式输出中的消息 -->
        <div v-if="isStreaming && streamingContent" class="chat-message assistant fade-in">
          <div class="message-avatar">🤖</div>
          <div class="message-body">
            <div class="message-role">助手</div>
            <div class="message-content">
              <StreamingText :text="streamingContent" />
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- 输入框 -->
    <ChatInput @send="handleSend" />
  </div>
</template>

<style scoped>
.chat-panel {
  display: flex;
  flex-direction: column;
  flex: 1;
  min-width: 0;
  height: 100%;
  background: var(--color-bg);
}

.messages-container {
  flex: 1;
  overflow-y: auto;
}

.messages-list {
  max-width: 800px;
  margin: 0 auto;
  padding: var(--space-lg);
}

/* 复用 ChatMessage 的样式结构（流式消息） */
.chat-message {
  display: flex;
  gap: var(--space-md);
  padding: var(--space-md) 0;
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

.message-body {
  max-width: 75%;
  min-width: 0;
}

.message-role {
  font-size: 12px;
  font-weight: 600;
  color: var(--color-text-muted);
  margin-bottom: 4px;
}

.message-content {
  padding: var(--space-sm) var(--space-md);
  border-radius: var(--radius-md);
  background: var(--color-surface);
  border: 1px solid var(--color-border-light);
  font-size: 14px;
}
</style>
