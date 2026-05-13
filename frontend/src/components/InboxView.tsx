import { useState, useEffect, useCallback } from 'react'
import { RefreshCw, Mail, MailOpen, Loader2 } from 'lucide-react'
import { EmailCard } from './EmailCard'
import type { AnalysisResult, InboxResponse } from '../types'

export function InboxView() {
  const [emails, setEmails] = useState<AnalysisResult[]>([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState<string | null>(null)
  const [filter, setFilter] = useState<'all' | 'unread'>('all')
  const [refreshing, setRefreshing] = useState(false)

  const fetchEmails = useCallback(async (showRefresh = false) => {
    if (showRefresh) setRefreshing(true)
    else setLoading(true)
    setError(null)

    try {
      const res = await fetch('/api/inbox?count=10')
      if (!res.ok) throw new Error(`Server error: ${res.status}`)
      const data: InboxResponse = await res.json()
      setEmails(data.emails || [])
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch emails')
    } finally {
      setLoading(false)
      setRefreshing(false)
    }
  }, [])

  useEffect(() => {
    fetchEmails()
  }, [fetchEmails])

  const filtered = filter === 'unread'
    ? emails.filter((e) => {
        const emailField = (e as unknown as Record<string, unknown>).isUnread
        return emailField === true
      })
    : emails

  return (
    <div>
      <div className="flex items-center justify-between mb-6">
        <h1 className="text-2xl font-bold text-gray-100">Inbox</h1>
        <div className="flex items-center gap-3">
          <div className="flex bg-gray-900 rounded-lg border border-gray-800 p-0.5">
            <button
              onClick={() => setFilter('all')}
              className={`flex items-center gap-1.5 px-3 py-1.5 text-sm rounded-md transition-colors ${
                filter === 'all'
                  ? 'bg-accent text-white'
                  : 'text-gray-400 hover:text-gray-200'
              }`}
            >
              <Mail size={14} />
              All
            </button>
            <button
              onClick={() => setFilter('unread')}
              className={`flex items-center gap-1.5 px-3 py-1.5 text-sm rounded-md transition-colors ${
                filter === 'unread'
                  ? 'bg-accent text-white'
                  : 'text-gray-400 hover:text-gray-200'
              }`}
            >
              <MailOpen size={14} />
              Unread
            </button>
          </div>
          <button
            onClick={() => fetchEmails(true)}
            disabled={refreshing}
            className="flex items-center gap-1.5 px-3 py-1.5 text-sm bg-gray-800 hover:bg-gray-700 border border-gray-700 rounded-lg transition-colors disabled:opacity-50"
          >
            <RefreshCw size={14} className={refreshing ? 'animate-spin' : ''} />
            Refresh
          </button>
        </div>
      </div>

      {loading && (
        <div className="flex items-center justify-center py-20">
          <Loader2 size={32} className="animate-spin text-gray-500" />
        </div>
      )}

      {error && (
        <div className="card p-6 text-center">
          <p className="text-red-400 mb-2">Failed to load inbox</p>
          <p className="text-sm text-gray-500 mb-4">{error}</p>
          <button
            onClick={() => fetchEmails()}
            className="px-4 py-2 bg-gray-800 hover:bg-gray-700 border border-gray-700 rounded-lg text-sm transition-colors"
          >
            Try Again
          </button>
        </div>
      )}

      {!loading && !error && filtered.length === 0 && (
        <div className="card p-10 text-center">
          <Mail size={40} className="mx-auto text-gray-600 mb-3" />
          <p className="text-gray-400">No emails found</p>
          <p className="text-sm text-gray-600 mt-1">
            {filter === 'unread' ? 'No unread emails' : 'Your inbox is empty'}
          </p>
        </div>
      )}

      {!loading && !error && filtered.length > 0 && (
        <div className="space-y-3">
          {filtered.map((email) => (
            <EmailCard key={email.id} analysis={email} />
          ))}
        </div>
      )}
    </div>
  )
}
