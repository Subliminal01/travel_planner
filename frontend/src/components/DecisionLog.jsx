import React from 'react'
import { Terminal, RefreshCw, Trash2 } from 'lucide-react'

export default function DecisionLog({ logs, onClear }) {
  const highlightLog = (line) => {
    if (!line) return null

    // Success line
    if (line.includes('Success:') || line.includes('Success') || line.includes('✅') || line.includes('🎉')) {
      return <span className="text-emerald-400 font-bold">{line}</span>
    }
    // Warning line
    if (line.includes('Warning:') || line.includes('⚠️') || line.includes('❌') || line.includes('cut') || line.includes('disrupted')) {
      return <span className="text-rose-400 font-semibold">{line}</span>
    }
    // Optimization detail line
    if (line.includes('Swapped') || line.includes('Saved') || line.includes('alternative')) {
      return <span className="text-cyan-300">{line}</span>
    }
    // Querying/Analyzing line
    if (line.includes('Analyzing') || line.includes('Searching') || line.includes('🔍')) {
      return <span className="text-violet-400">{line}</span>
    }
    // Standard text
    return <span className="text-slate-300">{line}</span>
  }

  return (
    <div className="glass-panel rounded-2xl overflow-hidden w-full border border-white/10 shadow-xl shadow-black/40">
      {/* Terminal Window Header */}
      <div className="bg-slate-900/90 px-4 py-3 border-b border-white/5 flex items-center justify-between">
        <div className="flex items-center gap-2">
          {/* OS Buttons */}
          <div className="flex gap-1.5 mr-2">
            <span className="w-3 h-3 rounded-full bg-rose-500/80"></span>
            <span className="w-3 h-3 rounded-full bg-amber-500/80"></span>
            <span className="w-3 h-3 rounded-full bg-emerald-500/80"></span>
          </div>
          <Terminal className="w-4 h-4 text-violet-400" />
          <span className="text-xs font-mono font-semibold tracking-wider text-slate-400 uppercase">
            Recalculation Decision Log
          </span>
        </div>
        
        {logs.length > 0 && (
          <button
            onClick={onClear}
            className="text-[10px] uppercase font-bold tracking-widest text-slate-500 hover:text-slate-300 transition-colors flex items-center gap-1"
          >
            <Trash2 className="w-3 h-3" />
            Clear console
          </button>
        )}
      </div>

      {/* Terminal Console Content */}
      <div className="bg-slate-950 p-5 font-mono text-xs leading-relaxed min-h-[180px] max-h-[300px] overflow-y-auto custom-scrollbar flex flex-col gap-2">
        {logs.length === 0 ? (
          <div className="flex-1 flex flex-col items-center justify-center text-center py-8 text-slate-600">
            <RefreshCw className="w-8 h-8 animate-pulse-slow mb-2" />
            <p className="font-sans text-xs italic">Console idle. Awaiting real-time constraint injection...</p>
          </div>
        ) : (
          logs.map((log, index) => (
            <div key={index} className="flex gap-2 items-start border-b border-white/2 pb-1 last:border-b-0">
              <span className="text-[10px] text-slate-600 select-none">
                [{new Date().toLocaleTimeString(undefined, { hour12: false })}]
              </span>
              <p className="flex-1 whitespace-pre-wrap">{highlightLog(log)}</p>
            </div>
          ))
        )}
      </div>
    </div>
  )
}
