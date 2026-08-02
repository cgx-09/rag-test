import { defineStore } from 'pinia'
import { ref, computed } from 'vue'
import type { Message, Citation } from '@/types'
import { streamChat } from '@/api'

function genId(): string {
  return Date.now().toString(36) + Math.random().toString(36).slice(2, 8)
}

export const useChatStore = defineStore('chat', () => {
  // ---- 状态 ----
  const threadId = ref(genId())
  const messages = ref<Message[]>([])
  const isStreaming = ref(false)
  const streamingContent = ref('')
  let cancelStreamFn: (() => void) | null = null

  // ---- 计算属性 ----
  const lastMessage = computed(() => messages.value[messages.value.length - 1] || null)

  // ---- 方法 ----
  function addUserMessage(content: string): void {
    messages.value.push({
      id: genId(),
      role: 'user',
      content,
      timestamp: Date.now(),
    })
  }

  function addAssistantMessage(content: string, sources?: Citation[]): void {
    messages.value.push({
      id: genId(),
      role: 'assistant',
      content,
      sources,
      timestamp: Date.now(),
    })
  }

  function sendMessage(question: string): void {
    if (isStreaming.value) return

    addUserMessage(question)
    isStreaming.value = true
    streamingContent.value = ''

    cancelStreamFn = streamChat(
      question,
      threadId.value,
      // onToken
      (token) => {
        streamingContent.value += token
      },
      // onDone
      (sources) => {
        addAssistantMessage(streamingContent.value, sources)
        streamingContent.value = ''
        isStreaming.value = false
        cancelStreamFn = null
      },
      // onError
      (err) => {
        addAssistantMessage(`❌ 出错了：${err.message}`)
        streamingContent.value = ''
        isStreaming.value = false
        cancelStreamFn = null
      }
    )
  }

  function cancelStreaming(): void {
    if (cancelStreamFn) {
      cancelStreamFn()
      // 保留已输出的内容
      if (streamingContent.value) {
        addAssistantMessage(streamingContent.value + '\n\n*[已中断]*')
      }
      streamingContent.value = ''
      isStreaming.value = false
      cancelStreamFn = null
    }
  }

  function newConversation(): void {
    if (isStreaming.value) {
      cancelStreaming()
    }
    messages.value = []
    threadId.value = genId()
  }

  function clearMessages(): void {
    messages.value = []
  }

  return {
    threadId,
    messages,
    isStreaming,
    streamingContent,
    lastMessage,
    sendMessage,
    cancelStreaming,
    newConversation,
    clearMessages,
  }
})
