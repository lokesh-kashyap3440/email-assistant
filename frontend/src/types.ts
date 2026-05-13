export interface Email {
  id: string
  threadId: string
  subject: string
  sender: string
  snippet: string
  body: string
  time: string
  timestamp: number
  labels: string[]
  isUnread: boolean
}

export interface ActionItem {
  description: string
  priority: 'high' | 'medium' | 'low'
}

export interface AnalysisResult {
  id: string
  subject: string
  sender: string
  time: string
  summary: string
  category:
    | 'billing'
    | 'security'
    | 'alert'
    | 'newsletter'
    | 'personal'
    | 'social'
    | 'promotion'
    | 'ai-tool'
    | 'other'
  urgency: 'urgent' | 'important' | 'normal'
  actionItems: ActionItem[]
  suggestedReply: string | null
  emailId: string
}

export interface Config {
  opencode_host: string
  opencode_port: number
  opencode_password: string
  opencode_model: string
  gmail_credentials_path: string
  gmail_token_path: string
  [key: string]: unknown
}

export interface HealthStatus {
  status: string
  opencode: string
  gmail: string
}

export interface InboxResponse {
  emails: AnalysisResult[]
  total: number
}
