import { AlertCircle, AlertTriangle, ArrowRight, ChevronRight, Reply } from 'lucide-react'
import type { AnalysisResult } from '../types'

const categoryColors: Record<string, string> = {
  billing: 'bg-red-500/10 text-red-400 border-red-500/30',
  security: 'bg-yellow-500/10 text-yellow-400 border-yellow-500/30',
  alert: 'bg-red-500/10 text-red-400 border-red-500/30',
  newsletter: 'bg-blue-500/10 text-blue-400 border-blue-500/30',
  personal: 'bg-green-500/10 text-green-400 border-green-500/30',
  social: 'bg-cyan-500/10 text-cyan-400 border-cyan-500/30',
  promotion: 'bg-blue-500/10 text-blue-400 border-blue-500/30',
  'ai-tool': 'bg-fuchsia-500/10 text-fuchsia-400 border-fuchsia-500/30',
  other: 'bg-gray-500/10 text-gray-400 border-gray-500/30',
}

const priorityColors: Record<string, string> = {
  high: 'text-red-400',
  medium: 'text-yellow-400',
  low: 'text-gray-400',
}

interface EmailCardProps {
  analysis: AnalysisResult
}

export function EmailCard({ analysis }: EmailCardProps) {
  const catColor = categoryColors[analysis.category] || categoryColors.other

  return (
    <div className="card p-5 hover:border-gray-700 transition-colors">
      <div className="flex items-start justify-between gap-4">
        <div className="flex-1 min-w-0">
          <div className="flex items-center gap-2 mb-1">
            {analysis.urgency === 'urgent' && (
              <span className="flex items-center gap-0.5 text-xs font-bold text-red-400" title="Urgent">
                <AlertCircle size={14} />
                <span>!!</span>
              </span>
            )}
            {analysis.urgency === 'important' && (
              <span className="flex items-center gap-0.5 text-xs font-bold text-yellow-400" title="Important">
                <AlertTriangle size={14} />
                <span>!</span>
              </span>
            )}
            <h3 className="text-base font-semibold text-gray-100 truncate">
              {analysis.subject || '(No Subject)'}
            </h3>
          </div>

          <div className="flex items-center gap-3 text-sm text-gray-400 mb-3">
            <span className="truncate">{analysis.sender}</span>
            <span className="shrink-0">{analysis.time}</span>
          </div>

          <p className="text-sm text-gray-300 leading-relaxed mb-3">
            {analysis.summary}
          </p>

          {analysis.actionItems && analysis.actionItems.length > 0 && (
            <div className="mb-3 space-y-1">
              {analysis.actionItems.map((item, i) => (
                <div key={i} className="flex items-start gap-2 text-sm">
                  <ArrowRight size={14} className="mt-0.5 shrink-0 text-gray-500" />
                  <span className={`${priorityColors[item.priority]}`}>
                    {item.description}
                  </span>
                </div>
              ))}
            </div>
          )}

          {analysis.suggestedReply && (
            <div className="flex items-start gap-2 p-3 bg-gray-800/50 rounded-lg border border-gray-700/50">
              <Reply size={14} className="mt-0.5 shrink-0 text-gray-500" />
              <p className="text-sm text-gray-400 italic leading-relaxed">
                {analysis.suggestedReply}
              </p>
            </div>
          )}
        </div>

        <div className="flex flex-col items-end gap-2 shrink-0">
          <span className={`text-xs font-medium px-2.5 py-1 rounded-full border ${catColor}`}>
            {analysis.category}
          </span>
          <ChevronRight size={16} className="text-gray-600" />
        </div>
      </div>
    </div>
  )
}
