import { useState, useEffect } from 'react'
import { CheckCircle, XCircle, Loader2, Upload } from 'lucide-react'

export function SetupView() {
  const [gmailAuth, setGmailAuth] = useState<boolean | null>(null)
  const [opencodeOk, setOpencodeOk] = useState<boolean | null>(null)
  const [checking, setChecking] = useState(true)
  const [credentialsPath, setCredentialsPath] = useState('')
  const [uploading, setUploading] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)

  async function checkStatus() {
    setChecking(true)
    try {
      const [authRes, healthRes] = await Promise.all([
        fetch('/api/auth/status'),
        fetch('/api/health'),
      ])
      const auth = await authRes.json()
      const health = await healthRes.json()

      setGmailAuth(auth.authenticated === true)
      setOpencodeOk(health.opencode === true || health.status === 'ok')
    } catch {
      setGmailAuth(false)
      setOpencodeOk(false)
    } finally {
      setChecking(false)
    }
  }

  useEffect(() => {
    checkStatus()
  }, [])

  async function handleSetup(e: React.FormEvent) {
    e.preventDefault()
    if (!credentialsPath.trim()) return
    setUploading(true)
    setMessage(null)
    try {
      const res = await fetch('/api/auth/setup', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ creds_path: credentialsPath.trim() }),
      })
      const data = await res.json()
      if (res.ok) {
        setMessage({ type: 'success', text: data.message || 'Setup initiated. Check the auth URL in the server console.' })
        await checkStatus()
      } else {
        setMessage({ type: 'error', text: data.detail || 'Setup failed' })
      }
    } catch (err) {
      setMessage({ type: 'error', text: err instanceof Error ? err.message : 'Setup failed' })
    } finally {
      setUploading(false)
    }
  }

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-100 mb-6">Setup</h1>

      <div className="card p-5 mb-6">
        <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">Service Status</h2>
        {checking ? (
          <div className="flex items-center gap-2 text-gray-400">
            <Loader2 size={16} className="animate-spin" />
            <span className="text-sm">Checking status...</span>
          </div>
        ) : (
          <div className="space-y-3">
            <div className="flex items-center gap-3">
              {opencodeOk ? (
                <CheckCircle size={18} className="text-green-400" />
              ) : (
                <XCircle size={18} className="text-red-400" />
              )}
              <span className="text-sm">
                <span className="text-gray-400">OpenCode Server:</span>{' '}
                <span className={opencodeOk ? 'text-green-400' : 'text-red-400'}>
                  {opencodeOk ? 'Connected' : 'Disconnected'}
                </span>
              </span>
            </div>
            <div className="flex items-center gap-3">
              {gmailAuth ? (
                <CheckCircle size={18} className="text-green-400" />
              ) : (
                <XCircle size={18} className="text-red-400" />
              )}
              <span className="text-sm">
                <span className="text-gray-400">Gmail API:</span>{' '}
                <span className={gmailAuth ? 'text-green-400' : 'text-red-400'}>
                  {gmailAuth ? 'Authenticated' : 'Not authenticated'}
                </span>
              </span>
            </div>
          </div>
        )}
      </div>

      {!gmailAuth && (
        <div className="card p-5">
          <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">Gmail OAuth Setup</h2>
          <p className="text-sm text-gray-500 mb-4">
            Provide the path to your Gmail API credentials.json file to set up OAuth authentication.
          </p>

          {message && (
            <div className={`p-3 rounded-lg mb-4 text-sm ${
              message.type === 'success'
                ? 'bg-green-500/10 text-green-400 border border-green-500/30'
                : 'bg-red-500/10 text-red-400 border border-red-500/30'
            }`}>
              {message.text}
            </div>
          )}

          <form onSubmit={handleSetup} className="space-y-4">
            <div>
              <label className="block text-sm text-gray-400 mb-1">Credentials Path</label>
              <input
                type="text"
                value={credentialsPath}
                onChange={(e) => setCredentialsPath(e.target.value)}
                className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-gray-100 text-sm focus:outline-none focus:border-accent transition-colors"
                placeholder="/path/to/credentials.json"
              />
            </div>
            <button
              type="submit"
              disabled={uploading || !credentialsPath.trim()}
              className="flex items-center gap-2 px-4 py-2 bg-accent hover:bg-accent-hover text-white rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
            >
              <Upload size={14} />
              {uploading ? 'Setting up...' : 'Start OAuth Setup'}
            </button>
          </form>
        </div>
      )}

      {gmailAuth && (
        <div className="card p-5">
          <div className="flex items-center gap-3">
            <CheckCircle size={20} className="text-green-400" />
            <div>
              <p className="text-sm font-medium text-gray-200">Gmail is authenticated</p>
              <p className="text-xs text-gray-500 mt-0.5">You can use the inbox feature</p>
            </div>
          </div>
        </div>
      )}
    </div>
  )
}
