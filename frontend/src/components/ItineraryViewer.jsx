import React from 'react'
import { 
  Plane, Sun, Cloud, CloudRain, CloudLightning, Calendar, Clock, 
  MapPin, Star, Sparkles, Check 
} from 'lucide-react'

export default function ItineraryViewer({ itinerary, originalItinerary }) {
  if (!itinerary) {
    return (
      <div className="glass-panel rounded-2xl p-8 flex flex-col items-center justify-center text-center min-h-[450px]">
        <div className="p-4 bg-white/5 rounded-full mb-4">
          <Plane className="w-12 h-12 text-slate-500 animate-pulse-slow" />
        </div>
        <h3 className="text-xl font-bold mb-2 text-white">No Active Itinerary</h3>
        <p className="text-slate-400 max-w-sm text-sm">
          Select your destination and preferences on the left to let the DuckDB constraint engine calculate your elite travel plan.
        </p>
      </div>
    )
  }

  // Helper to check if an activity was swapped/recalculated
  const isSwapped = (dayNum, slotName, currentActId) => {
    if (!originalItinerary) return false
    const origDay = originalItinerary.days.find(d => d.day_number === dayNum)
    if (!origDay) return false
    const origSlot = origDay.slots.find(s => s.time_slot === slotName)
    if (!origSlot || !origSlot.activity) return false
    return origSlot.activity.id !== currentActId
  }

  // Helper to get the original activity name if swapped
  const getOriginalActivityName = (dayNum, slotName) => {
    if (!originalItinerary) return null
    const origDay = originalItinerary.days.find(d => d.day_number === dayNum)
    if (!origDay) return null
    const origSlot = origDay.slots.find(s => s.time_slot === slotName)
    return origSlot?.activity?.name ?? null
  }

  // Helper to render weather icon
  const renderWeatherIcon = (condition) => {
    const cls = "w-5 h-5"
    switch (condition) {
      case 'Sunny':
        return <Sun className={`${cls} text-amber-400`} />
      case 'Cloudy':
        return <Cloud className={`${cls} text-slate-300`} />
      case 'Rainy':
        return <CloudRain className={`${cls} text-cyan-400`} />
      case 'Thunderstorm':
        return <CloudLightning className={`${cls} text-rose-500 animate-bounce`} />
      default:
        return <Sun className={`${cls} text-amber-400`} />
    }
  }

  const getWeatherClass = (condition) => {
    switch (condition) {
      case 'Thunderstorm':
        return 'bg-rose-500/10 border-rose-500/20 text-rose-300'
      case 'Rainy':
        return 'bg-cyan-500/10 border-cyan-500/20 text-cyan-300'
      case 'Cloudy':
        return 'bg-slate-500/10 border-slate-500/20 text-slate-300'
      default:
        return 'bg-amber-500/10 border-amber-500/20 text-amber-300'
    }
  }

  return (
    <div className="space-y-6">
      {/* Flight overview */}
      <div className="glass-panel rounded-2xl p-5 border-white/10">
        <h3 className="text-sm font-semibold uppercase tracking-wider text-slate-400 mb-4 flex items-center gap-2">
          <Plane className="w-4 h-4 text-violet-400" />
          Flights Booked (Outbound & Return)
        </h3>
        
        <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
          {/* Outbound Flight */}
          <div className="bg-white/5 border border-white/5 rounded-xl p-4 flex gap-4 items-center relative overflow-hidden group">
            <div className="absolute top-0 right-0 w-20 h-20 bg-violet-500/5 rounded-full blur-xl -mr-4 -mt-4 transition-transform group-hover:scale-125"></div>
            <div className="p-3 bg-violet-500/10 text-violet-400 rounded-xl">
              <Plane className="w-6 h-6 rotate-45" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex justify-between items-start">
                <span className="text-xs font-semibold uppercase tracking-wider text-violet-400">Outbound Flight</span>
                <span className="text-sm font-bold text-white">${itinerary.outbound_flight.price.toFixed(2)}</span>
              </div>
              <h4 className="text-sm font-bold text-white truncate mt-1">{itinerary.outbound_flight.airline}</h4>
              <p className="text-xs text-slate-400 mt-1 flex items-center gap-1">
                <span>{itinerary.outbound_flight.origin}</span>
                <span>➔</span>
                <span>{itinerary.preferences.destination_id.toUpperCase()}</span>
              </p>
              <p className="text-[10px] text-slate-500 mt-1">
                Departs: {itinerary.outbound_flight.departure_time} | Arrives: {itinerary.outbound_flight.arrival_time}
              </p>
            </div>
          </div>

          {/* Return Flight */}
          <div className="bg-white/5 border border-white/5 rounded-xl p-4 flex gap-4 items-center relative overflow-hidden group">
            <div className="absolute top-0 right-0 w-20 h-20 bg-cyan-500/5 rounded-full blur-xl -mr-4 -mt-4 transition-transform group-hover:scale-125"></div>
            <div className="p-3 bg-cyan-500/10 text-cyan-400 rounded-xl">
              <Plane className="w-6 h-6 -rotate-135" />
            </div>
            <div className="flex-1 min-w-0">
              <div className="flex justify-between items-start">
                <span className="text-xs font-semibold uppercase tracking-wider text-cyan-400">Return Flight</span>
                <span className="text-sm font-bold text-white">${itinerary.return_flight.price.toFixed(2)}</span>
              </div>
              <h4 className="text-sm font-bold text-white truncate mt-1">{itinerary.return_flight.airline}</h4>
              <p className="text-xs text-slate-400 mt-1 flex items-center gap-1">
                <span>{itinerary.preferences.destination_id.toUpperCase()}</span>
                <span>➔</span>
                <span>{itinerary.outbound_flight.origin}</span>
              </p>
              <p className="text-[10px] text-slate-500 mt-1">
                Departs: {itinerary.return_flight.departure_time} | Arrives: {itinerary.return_flight.arrival_time}
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* Day-by-Day Timeline */}
      <div className="space-y-6">
        {itinerary.days.map((day) => (
          <div key={day.day_number} className="relative">
            {/* Day Title and Weather */}
            <div className="flex flex-col sm:flex-row items-start sm:items-center justify-between gap-2 mb-4 bg-white/5 backdrop-blur-sm rounded-xl p-3 border border-white/5">
              <div className="flex items-center gap-2">
                <div className="w-8 h-8 rounded-lg bg-gradient-to-tr from-violet-600 to-cyan-500 flex items-center justify-center font-bold text-sm text-white shadow-md shadow-violet-600/10">
                  {day.day_number}
                </div>
                <h3 className="text-base font-extrabold text-white" style={{ fontFamily: 'Outfit' }}>
                  Day {day.day_number} Timeline
                </h3>
              </div>
              
              <div className={`flex items-center gap-2 px-3 py-1.5 rounded-full border text-xs font-semibold ${getWeatherClass(day.weather.condition)}`}>
                {renderWeatherIcon(day.weather.condition)}
                <span>{day.weather.condition}</span>
                <span className="w-1.5 h-1.5 rounded-full bg-white/20"></span>
                <span>{day.weather.temp_c}°C</span>
              </div>
            </div>

            {/* Slots Grid */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
              {day.slots.map((slot) => {
                const isItemSwapped = slot.activity && isSwapped(day.day_number, slot.time_slot, slot.activity.id)
                const originalName = getOriginalActivityName(day.day_number, slot.time_slot)
                
                return (
                  <div 
                    key={slot.time_slot} 
                    className={`relative rounded-xl p-4 transition-all duration-300 flex flex-col justify-between min-h-[170px] ${
                      isItemSwapped 
                        ? 'bg-emerald-950/20 border-2 border-emerald-500/40 shadow-lg shadow-emerald-500/5 hover:border-emerald-500/60 scale-[1.01]' 
                        : slot.activity 
                          ? 'bg-white/5 border border-white/5 hover:bg-white/10 hover:border-white/10' 
                          : 'bg-white/2 border border-dashed border-white/5 flex items-center justify-center text-center opacity-40'
                    }`}
                  >
                    {/* Swapped Glowing Badge */}
                    {isItemSwapped && (
                      <div className="absolute -top-2.5 right-4 px-2 py-0.5 bg-emerald-500 text-[10px] font-bold uppercase tracking-wider rounded-md text-slate-950 flex items-center gap-0.5 shadow-md shadow-emerald-500/20 animate-pulse">
                        <Sparkles className="w-3 h-3" />
                        <span>Swapped</span>
                      </div>
                    )}

                    {slot.activity ? (
                      <>
                        {/* Upper Details */}
                        <div>
                          <div className="flex justify-between items-start mb-2">
                            <span className="text-[10px] font-bold uppercase tracking-widest text-violet-400">
                              {slot.time_slot}
                            </span>
                            <span className="text-xs font-bold text-white bg-white/10 px-2 py-0.5 rounded-md">
                              {slot.activity.cost === 0 ? 'FREE' : `$${slot.activity.cost.toFixed(0)}`}
                            </span>
                          </div>
                          
                          <h4 className="text-sm font-bold text-white line-clamp-1 leading-snug">
                            {slot.activity.name}
                          </h4>
                          
                          <p className="text-[11px] text-slate-400 line-clamp-2 mt-1 leading-relaxed">
                            {slot.activity.description}
                          </p>
                        </div>

                        {/* Lower Badges */}
                        <div className="mt-4 pt-3 border-t border-white/5 flex items-center justify-between gap-1 flex-wrap">
                          <div className="flex items-center gap-2">
                            <span className="text-[10px] px-1.5 py-0.5 bg-white/5 rounded text-slate-300 font-semibold flex items-center gap-0.5">
                              {slot.activity.is_outdoor ? '🌲 Out' : '🏛️ In'}
                            </span>
                            <span className="text-[10px] px-1.5 py-0.5 bg-violet-500/10 text-violet-300 rounded font-semibold">
                              {slot.activity.vibe}
                            </span>
                          </div>
                          <span className="text-[10px] text-slate-400 flex items-center gap-0.5 font-bold">
                            <Star className="w-3 h-3 text-amber-400 fill-amber-400" />
                            {slot.activity.rating.toFixed(1)}
                          </span>
                        </div>

                        {/* Hover original name prompt if swapped */}
                        {isItemSwapped && originalName && (
                          <div className="mt-2 text-[9px] text-emerald-400 font-medium">
                            Was: <span className="line-through text-slate-400">{originalName}</span>
                          </div>
                        )}
                      </>
                    ) : (
                      <div className="flex flex-col items-center justify-center p-4">
                        <Clock className="w-5 h-5 text-slate-500 mb-1" />
                        <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500">
                          {slot.time_slot}
                        </span>
                        <span className="text-[10px] text-slate-600 mt-0.5">Flights / Transit</span>
                      </div>
                    )}
                  </div>
                )
              })}
            </div>
          </div>
        ))}
      </div>
    </div>
  )
}
