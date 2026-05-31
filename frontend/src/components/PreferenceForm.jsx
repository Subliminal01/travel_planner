import React, { useState, useEffect } from 'react'
import axios from 'axios'
import { Compass, Calendar, DollarSign, Clock, Heart, Loader2 } from 'lucide-react'

export default function PreferenceForm({ onSubmit, loading }) {
  const [destinations, setDestinations] = useState([])
  const [destLoading, setDestLoading] = useState(true)

  const [formData, setFormData] = useState({
    origin: 'New York',
    destination_id: '',
    vibe: 'Adventure',
    budget: 1500,
    days: 4,
    start_date: new Date().toISOString().split('T')[0]
  })

  useEffect(() => {
    // Fetch available destinations from FastAPI
    axios.get('/api/destinations')
      .then(res => {
        setDestinations(res.data)
        if (res.data.length > 0) {
          setFormData(prev => ({ ...prev, destination_id: res.data[0].id }))
        }
        setDestLoading(false)
      })
      .catch(err => {
        console.error("Error fetching destinations:", err)
        setDestLoading(false)
      })
  }, [])

  const handleSubmit = (e) => {
    e.preventDefault()
    if (!formData.destination_id) return
    onSubmit(formData)
  }

  const vibes = [
    { name: 'Adventure', icon: '🧗', desc: 'Thrilling treks and action-packed exploration' },
    { name: 'Cultural', icon: '🏛️', desc: 'Museums, ancient temples, and local culinary classes' },
    { name: 'Relaxing', icon: '🧘', desc: 'Thermal hot springs, coastal walks, and wellness spas' }
  ]

  if (destLoading) {
    return (
      <div className="glass-panel rounded-2xl p-6 flex flex-col items-center justify-center min-h-[300px]">
        <Loader2 className="w-8 h-8 text-violet-500 animate-spin mb-2" />
        <p className="text-slate-400 text-sm">Loading destinations...</p>
      </div>
    )
  }

  return (
    <div className="glass-panel rounded-2xl p-6 w-full relative overflow-hidden">
      {/* Decorative gradient corner */}
      <div className="absolute top-0 right-0 w-24 h-24 bg-violet-600/10 rounded-bl-full border-b border-l border-white/5"></div>
      
      <h2 className="text-xl font-bold mb-6 flex items-center gap-2 text-white" style={{ fontFamily: 'Outfit' }}>
        <Compass className="w-5 h-5 text-violet-400" />
        Configure Your Trip
      </h2>

      <form onSubmit={handleSubmit} className="space-y-5">
        {/* Destination Select */}
        <div>
          <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
            Select Destination
          </label>
          <div className="relative">
            <select
              value={formData.destination_id}
              onChange={(e) => setFormData({ ...formData, destination_id: e.target.value })}
              className="w-full glass-input rounded-xl px-4 py-3 text-sm appearance-none cursor-pointer"
            >
              {destinations.map(dest => (
                <option key={dest.id} value={dest.id} className="bg-brand-darkCard text-white">
                  {dest.name} ({dest.country})
                </option>
              ))}
            </select>
            <div className="absolute right-4 top-1/2 -translate-y-1/2 pointer-events-none text-slate-400 text-xs">
              ▼
            </div>
          </div>
        </div>

        {/* Origin */}
        <div>
          <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2">
            Departure Airport (Origin)
          </label>
          <input
            type="text"
            value={formData.origin}
            onChange={(e) => setFormData({ ...formData, origin: e.target.value })}
            className="w-full glass-input rounded-xl px-4 py-3 text-sm"
            placeholder="City or Airport (e.g. New York)"
            required
          />
        </div>

        {/* Start Date & Days */}
        <div className="grid grid-cols-2 gap-4">
          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2 flex items-center gap-1">
              <Calendar className="w-3.5 h-3.5 text-violet-400" />
              Start Date
            </label>
            <input
              type="date"
              value={formData.start_date}
              onChange={(e) => setFormData({ ...formData, start_date: e.target.value })}
              className="w-full glass-input rounded-xl px-4 py-3 text-sm"
              required
            />
          </div>

          <div>
            <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2 flex items-center gap-1">
              <Clock className="w-3.5 h-3.5 text-violet-400" />
              Duration ({formData.days} Days)
            </label>
            <div className="flex items-center gap-3">
              <input
                type="range"
                min="3"
                max="7"
                value={formData.days}
                onChange={(e) => setFormData({ ...formData, days: parseInt(e.target.value) })}
                className="w-full accent-violet-500 h-1.5 bg-white/10 rounded-lg cursor-pointer"
              />
            </div>
          </div>
        </div>

        {/* Budget Limit */}
        <div>
          <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2 flex items-center gap-1">
            <DollarSign className="w-3.5 h-3.5 text-violet-400" />
            Budget Cap
          </label>
          <div className="relative">
            <span className="absolute left-4 top-1/2 -translate-y-1/2 text-slate-400 text-sm font-semibold">$</span>
            <input
              type="number"
              min="300"
              max="10000"
              step="50"
              value={formData.budget}
              onChange={(e) => setFormData({ ...formData, budget: parseFloat(e.target.value) })}
              className="w-full glass-input rounded-xl pl-8 pr-4 py-3 text-sm"
              required
            />
          </div>
        </div>

        {/* Vibe Selection Pills */}
        <div>
          <label className="block text-xs font-semibold uppercase tracking-wider text-slate-400 mb-2 flex items-center gap-1">
            <Heart className="w-3.5 h-3.5 text-violet-400" />
            Trip Vibe
          </label>
          <div className="grid grid-cols-3 gap-2">
            {vibes.map(v => (
              <button
                key={v.name}
                type="button"
                onClick={() => setFormData({ ...formData, vibe: v.name })}
                className={`py-3 px-2 rounded-xl flex flex-col items-center justify-center transition-all duration-300 ${
                  formData.vibe === v.name
                    ? 'bg-gradient-to-tr from-violet-600 to-violet-500 text-white font-bold border-transparent ring-2 ring-violet-400/40 shadow-lg shadow-violet-500/20 scale-[1.03]'
                    : 'bg-white/5 border border-white/5 hover:bg-white/10 hover:border-white/10 text-slate-300'
                }`}
              >
                <span className="text-xl mb-1">{v.icon}</span>
                <span className="text-xs">{v.name}</span>
              </button>
            ))}
          </div>
          <p className="text-[10px] text-slate-400 mt-2 italic leading-relaxed text-center">
            {vibes.find(v => v.name === formData.vibe)?.desc}
          </p>
        </div>

        {/* Submit button */}
        <button
          type="submit"
          disabled={loading}
          className="w-full mt-2 py-3 px-4 bg-gradient-to-r from-violet-600 to-cyan-500 hover:from-violet-500 hover:to-cyan-400 text-white font-bold rounded-xl shadow-lg shadow-violet-600/20 flex items-center justify-center gap-2 transition-all duration-300 hover:scale-[1.01] active:scale-[0.99] disabled:opacity-50 disabled:cursor-not-allowed"
        >
          {loading ? (
            <>
              <Loader2 className="w-5 h-5 animate-spin" />
              <span>Generating Itinerary...</span>
            </>
          ) : (
            <>
              <span>Generate Engine Plan</span>
              <span>⚡</span>
            </>
          )}
        </button>
      </form>
    </div>
  )
}
