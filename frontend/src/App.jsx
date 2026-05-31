import React, { useState } from 'react'
import axios from 'axios'
import DashboardHeader from './components/DashboardHeader'
import PreferenceForm from './components/PreferenceForm'
import ItineraryViewer from './components/ItineraryViewer'
import ConstraintSimulator from './components/ConstraintSimulator'
import DecisionLog from './components/DecisionLog'
import { Sparkles, RefreshCw, AlertTriangle } from 'lucide-react'

// Set axios base URL for convenience
axios.defaults.baseURL = 'http://127.0.0.1:8000'

export default function App() {
  const [preferences, setPreferences] = useState(null)
  const [itinerary, setItinerary] = useState(null)
  const [originalItinerary, setOriginalItinerary] = useState(null)
  const [logs, setLogs] = useState([])
  const [loading, setLoading] = useState(false)
  const [recalcLoading, setRecalcLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleGenerateItinerary = async (formData) => {
    setLoading(true)
    setError(null)
    setLogs([])
    try {
      const res = await axios.post('/api/itinerary', formData)
      setItinerary(res.data)
      setOriginalItinerary(JSON.parse(JSON.stringify(res.data))) // Deep copy
      setPreferences(formData)
    } catch (err) {
      console.error(err)
      setError(err.response?.data?.detail ?? 'Failed to generate itinerary. Please try again.')
    } finally {
      setLoading(false)
    }
  }

  const handleRecalculate = async (disruption) => {
    if (!itinerary || !preferences) return
    setRecalcLoading(true)
    setError(null)
    try {
      const payload = {
        preferences: preferences,
        current_itinerary: itinerary,
        disruption_type: disruption.disruption_type,
        day_number: disruption.day_number,
        weather_condition: disruption.weather_condition,
        budget_reduction_percent: disruption.budget_reduction_percent
      }

      const res = await axios.post('/api/itinerary/recalculate', payload)
      setItinerary(res.data.itinerary)
      
      // Prepend a separator log
      const separator = `=== PROCESS INITIATED AT ${new Date().toLocaleTimeString()} ===`
      setLogs(prev => [separator, ...res.data.decision_logs, ...prev])
    } catch (err) {
      console.error(err)
      setError(err.response?.data?.detail ?? 'Engine failed to recalculate. Check constraints.')
    } finally {
      setRecalcLoading(false)
    }
  }

  const handleClearLogs = () => {
    setLogs([])
  }

  return (
    <main className="min-h-screen px-4 md:px-8 py-8 max-w-7xl mx-auto flex flex-col gap-6 relative">
      
      {/* Decorative radial lighting in background */}
      <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[500px] h-[500px] bg-violet-600/5 rounded-full blur-3xl pointer-events-none"></div>

      {/* Header Metric Cards */}
      <DashboardHeader preferences={preferences} itinerary={itinerary} />

      {/* Main Error Notice */}
      {error && (
        <div className="bg-rose-500/10 border-2 border-rose-500/30 rounded-2xl p-4 flex items-start gap-3 text-rose-300 text-sm shadow-lg shadow-rose-950/10 animate-shake">
          <AlertTriangle className="w-5 h-5 text-rose-500 flex-shrink-0" />
          <div>
            <span className="font-extrabold block">Constraint Error Raised</span>
            <p className="opacity-90 mt-0.5">{error}</p>
          </div>
        </div>
      )}

      {/* Two Column Layout Grid */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
        {/* Left Side Config Columns (Preference & Simulator) */}
        <section className="lg:col-span-4 flex flex-col gap-6">
          <PreferenceForm onSubmit={handleGenerateItinerary} loading={loading} />
          
          {itinerary && (
            <ConstraintSimulator 
              itinerary={itinerary} 
              onRecalculate={handleRecalculate} 
              loading={recalcLoading} 
            />
          )}
        </section>

        {/* Right Side Main View Columns (Itinerary Timeline & Logs) */}
        <section className="lg:col-span-8 flex flex-col gap-6 relative min-w-0">
          
          {/* Recalculating overlay pulse */}
          {recalcLoading && (
            <div className="absolute inset-0 bg-brand-dark/60 backdrop-blur-sm rounded-2xl z-50 flex flex-col items-center justify-center gap-3 border border-white/5 shadow-2xl">
              <div className="relative flex items-center justify-center">
                <RefreshCw className="w-10 h-10 text-violet-400 animate-spin" />
                <Sparkles className="w-4 h-4 text-cyan-400 absolute animate-pulse" />
              </div>
              <span className="text-sm font-bold uppercase tracking-widest text-violet-400 animate-pulse">
                Recalculating Itinerary...
              </span>
              <p className="text-[10px] text-slate-400 font-medium italic">
                DuckDB query engine optimizing activity constraints
              </p>
            </div>
          )}

          {/* Timeline displaying day-by-day */}
          <ItineraryViewer 
            itinerary={itinerary} 
            originalItinerary={originalItinerary} 
          />

          {/* Decision Terminal Logging Console */}
          {itinerary && (
            <DecisionLog 
              logs={logs} 
              onClear={handleClearLogs} 
            />
          )}
        </section>
      </div>

      {/* Subtle brand footer */}
      <footer className="text-center py-8 text-[10px] uppercase font-bold tracking-widest text-slate-600 border-t border-white/5 mt-10">
        <span>Aether Travel Engine MVP • Antigravity AI pair-programmed</span>
      </footer>
    </main>
  )
}
