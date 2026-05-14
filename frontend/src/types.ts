export interface AnalysisResult {
  id: string
  subject: string
  sender: string
  timestamp: string
  body_preview: string
  labels: string[]
  is_unread: boolean
  is_important: boolean
  summary: string
  category: string
  urgency: string
  action_items: string[]
  suggested_reply: string | null
}

export interface Config {
  opencode_host: string
  opencode_port: number
  backend: string
  [key: string]: unknown
}

export interface InboxResponse {
  emails: AnalysisResult[]
}
