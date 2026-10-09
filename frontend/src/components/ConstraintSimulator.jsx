import React, { useState } from 'react'
import { AlertTriangle, CloudLightning, Percent } from 'lucide-react'

export default function ConstraintSimulator({ itinerary, onRecalculate, loading }) {
  const [weatherDisruption, setWeatherDisruption] = useState({
    day_number: 2,
    condition: 'Thunderstorm'
  })
  const [budgetPercent, setBudgetPercent] = useState(20)

  if (!itinerary) return null

  const daysCount = itinerary.preferences.days

  const handleWeatherDisrupt = (e) => {
    e.preventDefault()
    onRecalculate({
      disruption_type: 'WEATHER',
      day_number: weatherDisruption.day_number,
      weather_condition: weatherDisruption.condition
    })
  }

  const handleBudgetDisrupt = (e) => {
    e.preventDefault()
    onRecalculate({
      disruption_type: 'BUDGET',
      budget_reduction_percent: budgetPercent
    })
  }

  // Pre-baked Quick Actions
  const quickActions = [
    {
      title: 'Thunderstorm on Day 2',
      icon: '⛈️',
      color: 'border-rose-500/30 hover:bg-rose-500/10 text-rose-300',
      action: () => onRecalculate({
        disruption_type: 'WEATHER',
        day_number: 2,
        weather_condition: 'Thunderstorm'
      })
    },
    {
      title: 'Heavy Rain on Day 3',
      icon: '🌧️',
      color: 'border-cyan-500/30 hover:bg-cyan-500/10 text-cyan-300',
      action: () => onRecalculate({
        disruption_type: 'WEATHER',
        day_number: Math.min(3, daysCount),
        weather_condition: 'Rainy'
      })
    },
    {
      title: 'Slash Budget by 20%',
      icon: '📉',
      color: 'border-amber-500/30 hover:bg-amber-500/10 text-amber-300',
      action: () => onRecalculate({
        disruption_type: 'BUDGET',
        budget_reduction_percent: 20
      })
    },
    {
      title: 'Cut Budget by 35%',
      icon: '💸',
      color: 'border-orange-500/30 hover:bg-orange-500/10 text-orange-300',
      action: () => onRecalculate({
        disruption_type: 'BUDGET',
        budget_reduction_percent: 35
      })
    }
  ]

  return (
    <section className="glass-panel rounded-2xl p-6 w-full relative overflow-hidden" aria-labelledby="disruption-simulator-heading">
      {/* Decorative pulse glow in simulator */}
      <div className="absolute top-0 right-0 w-2 h-2 rounded-full bg-rose-500 animate-ping mr-6 mt-6" aria-hidden="true"></div>
      
      <h2 id="disruption-simulator-heading" className="text-xl font-bold mb-6 flex items-center gap-2 text-white" style={{ fontFamily: 'Outfit' }}>
        <AlertTriangle className="w-5 h-5 text-rose-500" aria-hidden="true" />
        Disruption Simulator
      </h2>

      {/* Quick Triggers */}
      <div className="mb-6">
        <h3 className="block text-xs font-semibold uppercase tracking-wider text-slate-300 mb-3">
          Instant Quick Triggers
        </h3>
        <div className="grid grid-cols-2 gap-2">
          {quickActions.map((qa, index) => (
            <button
              key={index}
              type="button"
              disabled={loading}
              aria-label={`Recalculate itinerary: ${qa.title}`}
              onClick={qa.action}
              className={`p-3 rounded-xl border bg-white/2 hover:scale-[1.01] active:scale-[0.99] transition-all duration-300 flex flex-col items-center justify-center text-center gap-1.5 disabled:opacity-40 disabled:cursor-not-allowed ${qa.color}`}
            >
              <span className="text-2xl" aria-hidden="true">{qa.icon}</span>
              <span className="text-[10px] font-bold leading-tight truncate w-full">{qa.title}</span>
            </button>
          ))}
        </div>
      </div>

      <div className="h-px bg-white/10 my-5"></div>

      {/* Manual Controls */}
      <div className="space-y-5">
        {/* Custom Weather Disruption Form */}
        <form onSubmit={handleWeatherDisrupt} className="space-y-3">
          <h3 className="block text-xs font-semibold uppercase tracking-wider text-slate-300 flex items-center gap-1">
            <CloudLightning className="w-3.5 h-3.5 text-rose-500" aria-hidden="true" />
            Custom Weather Threat
          </h3>
          <div className="grid grid-cols-2 gap-2">
            <div>
              <label htmlFor="weather-day" className="text-[10px] text-slate-300 font-semibold uppercase">Trip Day</label>
              <select
                id="weather-day"
                name="weather_day"
                value={weatherDisruption.day_number}
                onChange={(e) => setWeatherDisruption({ ...weatherDisruption, day_number: parseInt(e.target.value) })}
                className="w-full glass-input rounded-xl px-3 py-2 text-xs"
              >
                {Array.from({ length: daysCount }, (_, i) => (
                  <option key={i + 1} value={i + 1} className="bg-brand-darkCard text-white">
                    Day {i + 1}
                  </option>
                ))}
              </select>
            </div>
            <div>
              <label htmlFor="weather-condition" className="text-[10px] text-slate-300 font-semibold uppercase">Condition</label>
              <select
                id="weather-condition"
                name="weather_condition"
                value={weatherDisruption.condition}
                onChange={(e) => setWeatherDisruption({ ...weatherDisruption, condition: e.target.value })}
                className="w-full glass-input rounded-xl px-3 py-2 text-xs"
              >
                <option value="Thunderstorm" className="bg-brand-darkCard text-white">⛈️ Thunderstorm</option>
                <option value="Rainy" className="bg-brand-darkCard text-white">🌧️ Heavy Rain</option>
                <option value="Cloudy" className="bg-brand-darkCard text-white">☁️ Severe Overcast</option>
              </select>
            </div>
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 px-4 bg-rose-950/40 hover:bg-rose-900/60 border border-rose-500/30 text-rose-200 text-xs font-bold rounded-xl flex items-center justify-center gap-2 transition-all duration-300 disabled:opacity-40"
          >
            <span>Inject Weather Threat</span>
            <span aria-hidden="true">⚡</span>
          </button>
        </form>

        <div className="h-px bg-white/5 my-4"></div>

        {/* Custom Budget Disruption Form */}
        <form onSubmit={handleBudgetDisrupt} className="space-y-3">
          <h3 className="block text-xs font-semibold uppercase tracking-wider text-slate-300 flex items-center gap-1">
            <Percent className="w-3.5 h-3.5 text-amber-500" aria-hidden="true" />
            Custom Budget Cut
          </h3>
          <div className="space-y-1">
            <div className="flex justify-between text-xs font-bold">
              <label htmlFor="budget-percent" className="text-slate-300">Slashing Amount</label>
              <span className="text-amber-400">{budgetPercent}%</span>
            </div>
            <input
              id="budget-percent"
              name="budget_percent"
              type="range"
              min="10"
              max="50"
              step="5"
              aria-valuemin="10"
              aria-valuemax="50"
              aria-valuenow={budgetPercent}
              aria-valuetext={`${budgetPercent}% budget cut`}
              value={budgetPercent}
              onChange={(e) => setBudgetPercent(parseInt(e.target.value))}
              className="w-full accent-amber-500 h-1.5 bg-white/10 rounded-lg cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-400 font-medium" aria-hidden="true">
              <span>10% (Minor Cut)</span>
              <span>50% (Extreme Cut)</span>
            </div>
          </div>
          <button
            type="submit"
            disabled={loading}
            className="w-full py-2.5 px-4 bg-amber-950/40 hover:bg-amber-900/60 border border-amber-500/30 text-amber-200 text-xs font-bold rounded-xl flex items-center justify-center gap-2 transition-all duration-300 disabled:opacity-40"
          >
            <span>Apply Budget Optimization</span>
            <span aria-hidden="true">⚡</span>
          </button>
        </form>
      </div>
    </section>
  )
}
