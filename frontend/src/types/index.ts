// ============ 对话相关 ============

export interface Citation {
  documentName: string
  chunkIndex: number
  content: string
}

export interface Message {
  id: string
  role: 'user' | 'assistant'
  content: string
  sources?: Citation[]
  timestamp: number
}

export interface ChatRequest {
  question: string
  thread_id: string
}

export interface ChatEvent {
  type: 'token' | 'done' | 'error'
  content?: string
  sources?: Citation[]
  error?: string
}

// ============ 文档相关 ============

export type DocStatus = 'indexing' | 'ready' | 'error'

export interface DocumentInfo {
  id: string
  name: string
  size: number
  status: DocStatus
  chunksCount: number
  uploadedAt: string
}

export interface KnowledgeStats {
  totalDocs: number
  totalChunks: number
}

export interface UploadResult {
  id: string
  name: string
  status: DocStatus
  message?: string
}
