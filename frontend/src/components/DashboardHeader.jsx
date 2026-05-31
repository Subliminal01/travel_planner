import React from 'react'
import { Compass, Wallet, Calendar, Percent, CheckCircle2 } from 'lucide-react'

export default function DashboardHeader({ preferences, itinerary }) {
  const budget = itinerary?.preferences?.budget ?? preferences?.budget ?? 0
  const totalCost = itinerary?.total_cost ?? 0
  const remaining = itinerary?.budget_remaining ?? (budget - totalCost)
  const days = itinerary?.preferences?.days ?? preferences?.days ?? 0
  const spendPercent = budget > 0 ? (totalCost / budget) * 100 : 0

  const getProgressBarColor = () => {
    if (spendPercent > 95) return 'bg-rose-500'
    if (spendPercent > 80) return 'bg-amber-500'
    return 'bg-teal-500'
  }

  return (
    <header className="w-full mb-8">
      {/* Title Bar */}
      <div className="flex flex-col md:flex-row items-center justify-between gap-4 border-b border-white/10 pb-6 mb-6">
        <div className="flex items-center gap-3">
          <div className="p-3 bg-gradient-to-tr from-violet-600 to-cyan-500 rounded-2xl shadow-lg shadow-violet-500/20 animate-glow-pulse">
            <Compass className="w-8 h-8 text-white" />
          </div>
          <div>
            <h1 className="text-3xl font-extrabold tracking-tight bg-gradient-to-r from-white via-slate-100 to-slate-400 bg-clip-text text-transparent font-sans" style={{ fontFamily: 'Outfit' }}>
              AETHER
            </h1>
            <p className="text-xs font-semibold uppercase tracking-widest text-violet-400">
              Travel Planning & Experience Engine
            </p>
          </div>
        </div>
        <div className="flex items-center gap-2 px-4 py-2 rounded-full glass-panel text-xs text-slate-300">
          <span className="w-2 h-2 rounded-full bg-emerald-500 animate-ping"></span>
          <span>DuckDB Engine Core: Online</span>
        </div>
      </div>

      {/* KPI Cards Grid */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-4">
        {/* Destination / Active Preferences */}
        <div className="glass-panel rounded-2xl p-5 relative overflow-hidden group">
          <div className="absolute top-0 right-0 w-32 h-32 bg-violet-500/5 rounded-full blur-2xl -mr-8 -mt-8 transition-transform group-hover:scale-125"></div>
          <div className="flex justify-between items-start mb-3">
            <span className="text-sm text-slate-400 font-medium">Destination</span>
            <Compass className="w-5 h-5 text-violet-400" />
          </div>
          <h3 className="text-2xl font-bold tracking-tight text-white mb-1">
            {itinerary ? itinerary.days[0]?.weather?.destination_id.toUpperCase() : 'None Selected'}
          </h3>
          <p className="text-xs text-slate-400">
            Vibe: <span className="text-violet-400 font-semibold">{preferences?.vibe ?? 'N/A'}</span>
          </p>
        </div>

        {/* Budget Limit */}
        <div className="glass-panel rounded-2xl p-5 relative overflow-hidden group">
          <div className="absolute top-0 right-0 w-32 h-32 bg-cyan-500/5 rounded-full blur-2xl -mr-8 -mt-8 transition-transform group-hover:scale-125"></div>
          <div className="flex justify-between items-start mb-3">
            <span className="text-sm text-slate-400 font-medium">Trip Budget</span>
            <Wallet className="w-5 h-5 text-cyan-400" />
          </div>
          <h3 className="text-2xl font-bold tracking-tight text-white mb-1">
            ${budget.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </h3>
          <p className="text-xs text-slate-400">Max threshold allowed</p>
        </div>

        {/* Total Cost / Spent */}
        <div className="glass-panel rounded-2xl p-5 relative overflow-hidden group">
          <div className="absolute top-0 right-0 w-32 h-32 bg-teal-500/5 rounded-full blur-2xl -mr-8 -mt-8 transition-transform group-hover:scale-125"></div>
          <div className="flex justify-between items-start mb-3">
            <span className="text-sm text-slate-400 font-medium">Scheduled Cost</span>
            <Percent className="w-5 h-5 text-teal-400" />
          </div>
          <h3 className="text-2xl font-bold tracking-tight text-white mb-1">
            ${totalCost.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </h3>
          {/* Progress bar inside card */}
          <div className="w-full bg-white/5 rounded-full h-1.5 mt-2">
            <div 
              className={`h-1.5 rounded-full transition-all duration-500 ${getProgressBarColor()}`} 
              style={{ width: `${Math.min(spendPercent, 100)}%` }}
            ></div>
          </div>
          <p className="text-[10px] text-slate-400 mt-1 text-right font-medium">
            {spendPercent.toFixed(0)}% of budget utilized
          </p>
        </div>

        {/* Budget Balance */}
        <div className="glass-panel rounded-2xl p-5 relative overflow-hidden group">
          <div className={`absolute top-0 right-0 w-32 h-32 ${remaining >= 0 ? 'bg-emerald-500/5' : 'bg-rose-500/5'} rounded-full blur-2xl -mr-8 -mt-8 transition-transform group-hover:scale-125`}></div>
          <div className="flex justify-between items-start mb-3">
            <span className="text-sm text-slate-400 font-medium">Remaining Cash</span>
            <CheckCircle2 className={`w-5 h-5 ${remaining >= 0 ? 'text-emerald-400' : 'text-rose-400'}`} />
          </div>
          <h3 className={`text-2xl font-bold tracking-tight mb-1 ${remaining >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
            ${remaining.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })}
          </h3>
          <p className="text-xs text-slate-400">
            {remaining >= 0 ? 'Surplus balance' : 'Budget exceeded!'}
          </p>
        </div>
      </div>
    </header>
  )
}
