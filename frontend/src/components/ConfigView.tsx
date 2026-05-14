import { useState, useEffect } from 'react'
import { Save, Loader2 } from 'lucide-react'
import type { Config } from '../types'

export function ConfigView() {
  const [config, setConfig] = useState<Config | null>(null)
  const [loading, setLoading] = useState(true)
  const [saving, setSaving] = useState(false)
  const [message, setMessage] = useState<{ type: 'success' | 'error'; text: string } | null>(null)
  const [form, setForm] = useState({
    opencode_host: '',
    opencode_port: '',
    opencode_password: '',
  })

  useEffect(() => {
    fetchConfig()
  }, [])

  async function fetchConfig() {
    setLoading(true)
    try {
      const res = await fetch('/api/config')
      if (!res.ok) throw new Error(`Server error: ${res.status}`)
      const data = await res.json()
      const cfg: Config = data.config || data
      setConfig(cfg)
      setForm({
        opencode_host: cfg.opencode_host || '',
        opencode_port: String(cfg.opencode_port || ''),
        opencode_password: '',
      })
    } catch (err) {
      setMessage({ type: 'error', text: err instanceof Error ? err.message : 'Failed to load config' })
    } finally {
      setLoading(false)
    }
  }

  async function handleSave(e: React.FormEvent) {
    e.preventDefault()
    setSaving(true)
    setMessage(null)
    try {
      const res = await fetch('/api/config', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          opencode_host: form.opencode_host,
          opencode_port: parseInt(form.opencode_port, 10) || 4096,
          opencode_password: form.opencode_password,
        }),
      })
      if (!res.ok) throw new Error(`Server error: ${res.status}`)
      setMessage({ type: 'success', text: 'Configuration saved' })
      await fetchConfig()
    } catch (err) {
      setMessage({ type: 'error', text: err instanceof Error ? err.message : 'Failed to save' })
    } finally {
      setSaving(false)
    }
  }

  if (loading) {
    return (
      <div className="flex items-center justify-center py-20">
        <Loader2 size={32} className="animate-spin text-gray-500" />
      </div>
    )
  }

  const sensitiveKeys = ['opencode_password', 'gmail_token_path', 'composio_key']

  return (
    <div>
      <h1 className="text-2xl font-bold text-gray-100 mb-6">Configuration</h1>

      {message && (
        <div className={`p-3 rounded-lg mb-4 text-sm ${
          message.type === 'success'
            ? 'bg-green-500/10 text-green-400 border border-green-500/30'
            : 'bg-red-500/10 text-red-400 border border-red-500/30'
        }`}>
          {message.text}
        </div>
      )}

      <div className="card p-5 mb-6">
        <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-3">Current Settings</h2>
        <div className="overflow-x-auto">
          <table className="w-full text-sm">
            <tbody className="divide-y divide-gray-800">
              {config && Object.entries(config).map(([key, value]) => (
                <tr key={key}>
                  <td className="py-2 pr-4 text-gray-400 font-mono text-xs">{key}</td>
                  <td className="py-2 text-gray-200 font-mono text-xs truncate max-w-0">
                    {sensitiveKeys.includes(key) && value
                      ? '••••••••'
                      : typeof value === 'object'
                        ? JSON.stringify(value)
                        : String(value ?? '')}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>

      <div className="card p-5">
        <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">Update Settings</h2>
        <form onSubmit={handleSave} className="space-y-4">
          <div>
            <label className="block text-sm text-gray-400 mb-1">OpenCode Host</label>
            <input
              type="text"
              value={form.opencode_host}
              onChange={(e) => setForm({ ...form, opencode_host: e.target.value })}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-gray-100 text-sm focus:outline-none focus:border-accent transition-colors"
              placeholder="localhost"
            />
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-1">OpenCode Port</label>
            <input
              type="number"
              value={form.opencode_port}
              onChange={(e) => setForm({ ...form, opencode_port: e.target.value })}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-gray-100 text-sm focus:outline-none focus:border-accent transition-colors"
              placeholder="4096"
            />
          </div>
          <div>
            <label className="block text-sm text-gray-400 mb-1">OpenCode Password</label>
            <input
              type="password"
              value={form.opencode_password}
              onChange={(e) => setForm({ ...form, opencode_password: e.target.value })}
              className="w-full bg-gray-800 border border-gray-700 rounded-lg px-3 py-2 text-gray-100 text-sm focus:outline-none focus:border-accent transition-colors"
              placeholder="Enter password"
            />
          </div>
          <button
            type="submit"
            disabled={saving}
            className="flex items-center gap-2 px-4 py-2 bg-accent hover:bg-accent-hover text-white rounded-lg text-sm font-medium transition-colors disabled:opacity-50"
          >
            <Save size={14} />
            {saving ? 'Saving...' : 'Save'}
          </button>
        </form>
      </div>
    </div>
  )
}
