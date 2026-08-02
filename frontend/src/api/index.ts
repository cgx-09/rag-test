import type { Citation } from '@/types'

const BASE_URL = '/api'
const USE_MOCK = import.meta.env.VITE_USE_MOCK === 'true'

// ============ Mock 数据 ============

function mockStreamChat(
  _question: string,
  _threadId: string,
  onToken: (token: string) => void,
  onDone: (sources: Citation[]) => void,
  onError: (err: Error) => void
): () => void {
  const mockAnswer =
    '根据您提供的文档资料，以下是相关信息的总结：\n\n' +
    '## 主要发现\n\n' +
    '1. **LangChain** 是一个用于构建大语言模型应用的框架，提供了链（Chain）、Agent、工具（Tool）等核心组件。\n' +
    '2. RAG（检索增强生成）是 LangChain 最常用的应用场景之一。\n\n' +
    '> 提示：您可以通过上传更多文档来扩展知识库的范围。\n'

  const mockSources: Citation[] = [
    {
      documentName: 'test_sample.txt',
      chunkIndex: 1,
      content: 'LangChain 是一个用于构建大语言模型应用的框架。它提供了链（Chain）、Agent、工具（Tool）等核心组件。',
    },
    {
      documentName: 'test01.txt',
      chunkIndex: 3,
      content: 'RAG（检索增强生成）是 LangChain 最常用的应用场景之一。',
    },
  ]

  const chars = mockAnswer.split('')
  let index = 0
  let cancelled = false

  const interval = setInterval(() => {
    if (cancelled) {
      clearInterval(interval)
      return
    }
    if (index < chars.length) {
      // 每次输出 2-5 个字符，模拟流式效果
      const chunkSize = Math.floor(Math.random() * 4) + 2
      onToken(chars.slice(index, index + chunkSize).join(''))
      index += chunkSize
    } else {
      clearInterval(interval)
      setTimeout(() => onDone(mockSources), 200)
    }
  }, 40)

  return () => {
    cancelled = true
    clearInterval(interval)
  }
}

// ============ SSE 流式请求 ============

export function streamChat(
  question: string,
  threadId: string,
  onToken: (token: string) => void,
  onDone: (sources: Citation[]) => void,
  onError: (err: Error) => void
): () => void {
  if (USE_MOCK) {
    return mockStreamChat(question, threadId, onToken, onDone, onError)
  }

  const controller = new AbortController()
  let cancelled = false

  fetch(`${BASE_URL}/chat`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({ question, thread_id: threadId }),
    signal: controller.signal,
  })
    .then(async (response) => {
      if (!response.ok) {
        throw new Error(`HTTP ${response.status}`)
      }
      const reader = response.body!.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break

        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() || ''

        for (const line of lines) {
          if (line.startsWith('data: ')) {
            try {
              const data = JSON.parse(line.slice(6))
              if (data.type === 'token' && data.content) {
                if (!cancelled) onToken(data.content)
              } else if (data.type === 'done') {
                if (!cancelled) onDone(data.sources || [])
                return
              } else if (data.type === 'error') {
                if (!cancelled) onError(new Error(data.error || '未知错误'))
                return
              }
            } catch {
              // 忽略解析错误的行
            }
          }
        }
      }
    })
    .catch((err) => {
      if (err.name !== 'AbortError') {
        if (!cancelled) onError(err)
      }
    })

  return () => {
    cancelled = true
    controller.abort()
  }
}

// ============ 通用请求封装 ============

async function request<T>(path: string, options?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...options,
  })
  if (!res.ok) {
    throw new Error(`HTTP ${res.status}: ${res.statusText}`)
  }
  return res.json()
}

// ============ 文档管理 API ============

import type { DocumentInfo, KnowledgeStats, UploadResult } from '@/types'

export async function getDocuments(): Promise<DocumentInfo[]> {
  if (USE_MOCK) {
    return [
      { id: '1', name: 'test_sample.txt', size: 256, status: 'ready', chunksCount: 5, uploadedAt: '2026-08-01 10:30' },
      { id: '2', name: 'test01.txt', size: 2048, status: 'ready', chunksCount: 18, uploadedAt: '2026-08-01 09:15' },
      { id: '3', name: '产品手册.pdf', size: 1048576, status: 'indexing', chunksCount: 0, uploadedAt: '2026-08-01 11:00' },
    ]
  }
  return request<DocumentInfo[]>('/docs')
}

export async function getKnowledgeStats(): Promise<KnowledgeStats> {
  if (USE_MOCK) {
    return { totalDocs: 2, totalChunks: 23 }
  }
  return request<KnowledgeStats>('/kb/stats')
}

export async function deleteDocument(id: string): Promise<void> {
  if (USE_MOCK) {
    return
  }
  await request(`/docs/${id}`, { method: 'DELETE' })
}

export async function reindexDocument(id: string): Promise<void> {
  if (USE_MOCK) {
    return
  }
  await request(`/docs/${id}/reindex`, { method: 'POST' })
}

// ============ 上传 API ============

export function uploadDocument(
  file: File,
  onProgress: (percent: number) => void,
  onDone: (result: UploadResult) => void,
  onError: (err: Error) => void
): () => void {
  if (USE_MOCK) {
    let progress = 0
    let cancelled = false
    const interval = setInterval(() => {
      if (cancelled) {
        clearInterval(interval)
        return
      }
      progress += Math.random() * 30
      if (progress >= 100) {
        progress = 100
        clearInterval(interval)
        onProgress(100)
        setTimeout(() => {
          if (!cancelled) {
            onDone({ id: Date.now().toString(), name: file.name, status: 'ready' })
          }
        }, 500)
      } else {
        onProgress(Math.round(progress))
      }
    }, 300)
    return () => {
      cancelled = true
      clearInterval(interval)
    }
  }

  const xhr = new XMLHttpRequest()
  const formData = new FormData()
  formData.append('file', file)

  let cancelled = false

  xhr.upload.addEventListener('progress', (e) => {
    if (e.lengthComputable && !cancelled) {
      onProgress(Math.round((e.loaded / e.total) * 100))
    }
  })

  xhr.addEventListener('load', () => {
    if (cancelled) return
    if (xhr.status >= 200 && xhr.status < 300) {
      onDone(JSON.parse(xhr.responseText))
    } else {
      onError(new Error(`上传失败: HTTP ${xhr.status}`))
    }
  })

  xhr.addEventListener('error', () => {
    if (!cancelled) onError(new Error('网络错误'))
  })

  xhr.open('POST', `${BASE_URL}/upload`)
  xhr.send(formData)

  return () => {
    cancelled = true
    xhr.abort()
  }
}
