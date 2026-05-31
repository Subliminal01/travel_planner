import duckdb
from typing import List, Set
from .db import Database
from .schemas import (
    ItineraryPreference, Itinerary, ItineraryDay, ItinerarySlot,
    Flight, Activity, WeatherForecast, DisruptionRequest
)

class ItineraryEngine:
    def __init__(self):
        self.db = Database()

    def _get_weather(self, conn, destination_id: str, day_number: int) -> WeatherForecast:
        """Fetches weather forecast for a destination and day from DuckDB."""
        row = conn.execute(
            "SELECT condition, temp_c FROM weather_forecast WHERE destination_id = ? AND day_number = ?",
            [destination_id, day_number]
        ).fetchone()
        
        if row:
            return WeatherForecast(
                destination_id=destination_id,
                day_number=day_number,
                condition=row[0],
                temp_c=int(row[1])
            )
        # Default fallback
        return WeatherForecast(
            destination_id=destination_id,
            day_number=day_number,
            condition="Sunny",
            temp_c=22
        )

    def generate_itinerary(self, pref: ItineraryPreference) -> Itinerary:
        """Generates a day-by-day itinerary based on user preferences."""
        conn = self.db.get_connection()
        try:
            # 1. Fetch Flights
            # Outbound flight
            out_row = conn.execute(
                "SELECT id, origin, destination_id, airline, price, departure_time, arrival_time, direction "
                "FROM flights WHERE destination_id = ? AND direction = 'Outbound' ORDER BY price ASC LIMIT 1",
                [pref.destination_id]
            ).fetchone()
            
            # Return flight
            ret_row = conn.execute(
                "SELECT id, origin, destination_id, airline, price, departure_time, arrival_time, direction "
                "FROM flights WHERE destination_id = ? AND direction = 'Return' ORDER BY price ASC LIMIT 1",
                [pref.destination_id]
            ).fetchone()

            if not out_row or not ret_row:
                raise ValueError(f"No flights found for destination {pref.destination_id}")

            outbound_flight = Flight(
                id=out_row[0], origin=out_row[1], destination_id=out_row[2],
                airline=out_row[3], price=out_row[4], departure_time=out_row[5],
                arrival_time=out_row[6], direction=out_row[7]
            )

            return_flight = Flight(
                id=ret_row[0], origin=ret_row[1], destination_id=ret_row[2],
                airline=ret_row[3], price=ret_row[4], departure_time=ret_row[5],
                arrival_time=ret_row[6], direction=ret_row[7]
            )

            flight_cost = outbound_flight.price + return_flight.price
            activity_budget = pref.budget - flight_cost

            # 2. Fetch all available activities
            activities_cursor = conn.execute(
                "SELECT id, destination_id, name, vibe, cost, duration_hours, is_outdoor, typical_slot, description, rating "
                "FROM activities WHERE destination_id = ?",
                [pref.destination_id]
            ).fetchall()

            activities_pool = []
            for r in activities_cursor:
                activities_pool.append(Activity(
                    id=r[0], destination_id=r[1], name=r[2], vibe=r[3], cost=r[4],
                    duration_hours=r[5], is_outdoor=r[6], typical_slot=r[7],
                    description=r[8], rating=r[9]
                ))

            # 3. Build Schedule Day-by-Day
            days_list: List[ItineraryDay] = []
            used_activities: Set[str] = set()

            for d in range(1, pref.days + 1):
                weather = self._get_weather(conn, pref.destination_id, d)
                slots = []

                if d == 1:
                    # Day 1: Arrival. Flight in afternoon. Only Evening Slot populated.
                    slots.append(ItinerarySlot(time_slot="Morning", activity=None, cost=0.0))
                    slots.append(ItinerarySlot(time_slot="Afternoon", activity=None, cost=0.0))
                    
                    # Evening activity - prefer Relaxing or Cultural and Indoor
                    eve_act = self._select_best_activity(
                        activities_pool, "Evening", pref.vibe, used_activities, max_cost=activity_budget
                    )
                    slots.append(ItinerarySlot(
                        time_slot="Evening", 
                        activity=eve_act, 
                        cost=eve_act.cost if eve_act else 0.0
                    ))
                    if eve_act:
                        used_activities.add(eve_act.id)
                        activity_budget -= eve_act.cost

                elif d == pref.days:
                    # Last Day: Departure. Flight in afternoon. Only Morning Slot populated.
                    morn_act = self._select_best_activity(
                        activities_pool, "Morning", pref.vibe, used_activities, max_cost=activity_budget
                    )
                    slots.append(ItinerarySlot(
                        time_slot="Morning", 
                        activity=morn_act, 
                        cost=morn_act.cost if morn_act else 0.0
                    ))
                    if morn_act:
                        used_activities.add(morn_act.id)
                        activity_budget -= morn_act.cost

                    slots.append(ItinerarySlot(time_slot="Afternoon", activity=None, cost=0.0))
                    slots.append(ItinerarySlot(time_slot="Evening", activity=None, cost=0.0))

                else:
                    # Full days
                    for slot in ["Morning", "Afternoon", "Evening"]:
                        act = self._select_best_activity(
                            activities_pool, slot, pref.vibe, used_activities, max_cost=activity_budget
                        )
                        slots.append(ItinerarySlot(
                            time_slot="Slot", 
                            activity=act, 
                            cost=act.cost if act else 0.0
                        ))
                        # Fix the slot name back to standard
                        slots[-1].time_slot = slot
                        
                        if act:
                            used_activities.add(act.id)
                            activity_budget -= act.cost

                days_list.append(ItineraryDay(day_number=d, weather=weather, slots=slots))

            # 4. Calculate total cost and balance
            total_activity_cost = sum(slot.cost for day in days_list for slot in day.slots)
            total_cost = flight_cost + total_activity_cost
            budget_remaining = pref.budget - total_cost

            # 5. Optimize if over budget
            if total_cost > pref.budget:
                days_list, total_cost = self._optimize_budget_on_generation(
                    days_list, pref.budget, flight_cost, activities_pool, used_activities
                )
                budget_remaining = pref.budget - total_cost

            return Itinerary(
                preferences=pref,
                outbound_flight=outbound_flight,
                return_flight=return_flight,
                days=days_list,
                total_cost=total_cost,
                budget_remaining=budget_remaining
            )
        finally:
            conn.close()

    def _select_best_activity(self, pool: List[Activity], slot: str, preferred_vibe: str, 
                              used: Set[str], max_cost: float, force_indoor: bool = False) -> Activity:
        """Helper to score and select the best matching activity from the pool."""
        candidates = []
        for act in pool:
            if act.id in used:
                continue
            if act.typical_slot != slot:
                continue
            if force_indoor and act.is_outdoor:
                continue
            if act.cost > max_cost:
                continue
            
            # Simple scoring: preferred vibe matches, higher rating is better, lower cost is better
            score = act.rating
            if act.vibe == preferred_vibe:
                score += 5.0  # Big boost for preferred vibe
            
            candidates.append((score, act))
        
        if not candidates:
            # Fallback to any slot if standard slot candidate is empty
            if force_indoor:
                # Try finding any indoor activity of same destination
                for act in pool:
                    if act.id not in used and not act.is_outdoor and act.cost <= max_cost:
                        score = act.rating
                        if act.vibe == preferred_vibe:
                            score += 5.0
                        candidates.append((score, act))

        if candidates:
            # Sort candidates by score descending
            candidates.sort(key=lambda x: x[0], reverse=True)
            return candidates[0][1]
        
        return None

    def _optimize_budget_on_generation(self, days: List[ItineraryDay], budget: float, flight_cost: float,
                                       pool: List[Activity], used: Set[str]):
        """Performs greedy optimization to bring a generated itinerary within budget."""
        current_total = flight_cost + sum(slot.cost for day in days for slot in day.slots)
        
        while current_total > budget:
            # Find the most expensive activity currently scheduled
            most_expensive_slot = None
            max_cost = -1
            target_day_idx = -1
            target_slot_idx = -1

            for d_idx, day in enumerate(days):
                for s_idx, slot in enumerate(day.slots):
                    if slot.activity and slot.activity.cost > max_cost:
                        max_cost = slot.activity.cost
                        most_expensive_slot = slot
                        target_day_idx = d_idx
                        target_slot_idx = s_idx

            if not most_expensive_slot or max_cost <= 0.0:
                # No activities with cost > 0 to swap
                break

            # Find a cheaper alternative for the same slot
            pref_vibe = days[target_day_idx].slots[target_slot_idx].activity.vibe
            slot_name = days[target_day_idx].slots[target_slot_idx].time_slot
            
            # Try to find an unused cheaper activity for the same slot
            alternative = None
            best_alt_cost = max_cost
            for act in pool:
                if act.id in used:
                    continue
                if act.typical_slot != slot_name:
                    continue
                if act.cost < best_alt_cost:
                    alternative = act
                    best_alt_cost = act.cost

            if alternative:
                # Swap it
                old_act = days[target_day_idx].slots[target_slot_idx].activity
                used.remove(old_act.id)
                used.add(alternative.id)
                
                days[target_day_idx].slots[target_slot_idx].activity = alternative
                days[target_day_idx].slots[target_slot_idx].cost = alternative.cost
                current_total = flight_cost + sum(s.cost for day in days for s in day.slots)
            else:
                # No cheaper alternative for slot. Force swap to a $0 placeholder or keep it
                # For safety, let's see if we can find a free activity in the pool
                free_alt = None
                for act in pool:
                    if act.id not in used and act.cost == 0.0:
                        free_alt = act
                        break
                
                if free_alt:
                    old_act = days[target_day_idx].slots[target_slot_idx].activity
                    used.remove(old_act.id)
                    used.add(free_alt.id)
                    
                    days[target_day_idx].slots[target_slot_idx].activity = free_alt
                    days[target_day_idx].slots[target_slot_idx].cost = 0.0
                    current_total = flight_cost + sum(s.cost for day in days for s in day.slots)
                else:
                    # Can't optimize further without removing activity entirely
                    # Set it to None to satisfy budget constraints (better than crashing!)
                    old_act = days[target_day_idx].slots[target_slot_idx].activity
                    used.remove(old_act.id)
                    days[target_day_idx].slots[target_slot_idx].activity = None
                    days[target_day_idx].slots[target_slot_idx].cost = 0.0
                    current_total = flight_cost + sum(s.cost for day in days for s in day.slots)

        return days, current_total

    def recalculate_itinerary(self, req: DisruptionRequest) -> Itinerary:
        """Handles a real-time constraint disruption and recalculates the itinerary instantly."""
        conn = self.db.get_connection()
        decision_logs = []
        itinerary = req.current_itinerary
        
        try:
            # Fetch all activities for query pool
            activities_cursor = conn.execute(
                "SELECT id, destination_id, name, vibe, cost, duration_hours, is_outdoor, typical_slot, description, rating "
                "FROM activities WHERE destination_id = ?",
                [req.preferences.destination_id]
            ).fetchall()

            activities_pool = []
            for r in activities_cursor:
                activities_pool.append(Activity(
                    id=r[0], destination_id=r[1], name=r[2], vibe=r[3], cost=r[4],
                    duration_hours=r[5], is_outdoor=r[6], typical_slot=r[7],
                    description=r[8], rating=r[9]
                ))

            # Maintain set of currently used activities to prevent duplication
            used_activities = set()
            for day in itinerary.days:
                for slot in day.slots:
                    if slot.activity:
                        used_activities.add(slot.activity.id)

            if req.disruption_type == "WEATHER":
                day_num = req.day_number
                condition = req.weather_condition or "Thunderstorm"
                
                decision_logs.append(f"⚠️ WEATHER DISRUPTION INJECTED: Severe {condition} forecast on Day {day_num}.")
                
                # Update weather condition for the target day
                target_day = next((d for d in itinerary.days if d.day_number == day_num), None)
                if target_day:
                    target_day.weather.condition = condition
                    target_day.weather.temp_c -= 3  # Drop temperature for bad weather
                    
                    # Look for outdoor activities on that day to swap
                    for slot_idx, slot in enumerate(target_day.slots):
                        if slot.activity and slot.activity.is_outdoor:
                            old_act = slot.activity
                            decision_logs.append(
                                f"🔍 Day {day_num} [{slot.time_slot}]: Scheduled activity '{old_act.name}' is OUTDOOR. Searching for indoor replacements..."
                            )
                            
                            # Find indoor replacement
                            used_activities.remove(old_act.id)
                            new_act = self._select_best_activity(
                                activities_pool, 
                                slot.time_slot, 
                                req.preferences.vibe, 
                                used_activities, 
                                max_cost=itinerary.budget_remaining + old_act.cost,
                                force_indoor=True
                            )
                            
                            if new_act:
                                slot.activity = new_act
                                slot.cost = new_act.cost
                                used_activities.add(new_act.id)
                                
                                cost_diff = new_act.cost - old_act.cost
                                sign = "+" if cost_diff >= 0 else ""
                                decision_logs.append(
                                    f"✅ Day {day_num} [{slot.time_slot}]: Swapped '{old_act.name}' (${old_act.cost}) with INDOOR '{new_act.name}' (${new_act.cost}). Cost change: {sign}${cost_diff:.2f}."
                                )
                            else:
                                # Keep old but log warnings
                                used_activities.add(old_act.id)
                                decision_logs.append(
                                    f"❌ Day {day_num} [{slot.time_slot}]: No suitable indoor activity found in the database. Kept '{old_act.name}' with hazard advisory."
                                )
                else:
                    decision_logs.append(f"❌ Error: Invalid day number {day_num} for weather disruption.")

            elif req.disruption_type == "BUDGET":
                pct = req.budget_reduction_percent or 20.0
                old_budget = itinerary.preferences.budget
                new_budget = old_budget * (1.0 - pct / 100.0)
                itinerary.preferences.budget = new_budget
                
                decision_logs.append(f"⚠️ BUDGET CUT INJECTED: Total budget reduced by {pct}% (From ${old_budget:.2f} to ${new_budget:.2f}).")
                
                flight_cost = itinerary.outbound_flight.price + itinerary.return_flight.price
                current_total = flight_cost + sum(slot.cost for day in itinerary.days for slot in day.slots)
                
                if current_total <= new_budget:
                    decision_logs.append(f"✅ Current itinerary cost (${current_total:.2f}) is already within the new budget limit of ${new_budget:.2f}. No optimizations needed!")
                else:
                    savings_needed = current_total - new_budget
                    decision_logs.append(f"📉 Optimization required: Need to slash at least ${savings_needed:.2f} from activities.")
                    
                    # Greedily swap expensive activities with cheaper ones
                    # Create a flat list of scheduled activities with references
                    scheduled_items = []
                    for day_idx, day in enumerate(itinerary.days):
                        for slot_idx, slot in enumerate(day.slots):
                            if slot.activity and slot.activity.cost > 0.0:
                                scheduled_items.append((slot.activity.cost, day_idx, slot_idx, slot.activity))
                    
                    # Sort scheduled items by cost descending
                    scheduled_items.sort(key=lambda x: x[0], reverse=True)
                    
                    for cost, day_idx, slot_idx, act in scheduled_items:
                        if savings_needed <= 0.0:
                            break
                        
                        slot_name = itinerary.days[day_idx].slots[slot_idx].time_slot
                        decision_logs.append(f"🔍 Analyzing Day {day_idx+1} [{slot_name}] '{act.name}' (${act.cost}). Searching for cheaper alternatives...")
                        
                        # Find cheaper alternative
                        used_activities.remove(act.id)
                        alternative = None
                        best_alt_cost = act.cost
                        
                        for p_act in activities_pool:
                            if p_act.id in used_activities:
                                continue
                            if p_act.typical_slot != slot_name:
                                continue
                            if p_act.cost < best_alt_cost:
                                alternative = p_act
                                best_alt_cost = p_act.cost
                        
                        if alternative:
                            # Swap
                            itinerary.days[day_idx].slots[slot_idx].activity = alternative
                            itinerary.days[day_idx].slots[slot_idx].cost = alternative.cost
                            used_activities.add(alternative.id)
                            
                            saved = act.cost - alternative.cost
                            savings_needed -= saved
                            decision_logs.append(
                                f"✅ Day {day_idx+1} [{slot_name}]: Swapped '{act.name}' (${act.cost}) with cheaper '{alternative.name}' (${alternative.cost}). Saved ${saved:.2f}!"
                            )
                        else:
                            # If no direct slot alternative is cheaper, look for any $0 free activity
                            free_alt = None
                            for p_act in activities_pool:
                                if p_act.id not in used_activities and p_act.cost == 0.0:
                                    free_alt = p_act
                                    break
                            
                            if free_alt:
                                itinerary.days[day_idx].slots[slot_idx].activity = free_alt
                                itinerary.days[day_idx].slots[slot_idx].cost = 0.0
                                used_activities.add(free_alt.id)
                                
                                saved = act.cost
                                savings_needed -= saved
                                decision_logs.append(
                                    f"✅ Day {day_idx+1} [{slot_name}]: Swapped '{act.name}' (${act.cost}) with FREE activity '{free_alt.name}' ($0.00). Saved ${saved:.2f}!"
                                )
                            else:
                                # Re-add original since we couldn't swap
                                used_activities.add(act.id)
                                decision_logs.append(f"❌ No cheaper alternatives found for Day {day_idx+1} [{slot_name}]. Original activity kept.")

                    # Final cost tally
                    current_total = flight_cost + sum(slot.cost for day in itinerary.days for slot in day.slots)
                    if current_total <= new_budget:
                        decision_logs.append(f"🎉 Success: Budget optimization complete! Final cost is ${current_total:.2f}, within the new budget limit of ${new_budget:.2f}.")
                    else:
                        decision_logs.append(f"⚠️ Warning: We swapped all possible activities, but final cost (${current_total:.2f}) still exceeds the new budget limit of ${new_budget:.2f} by ${current_total - new_budget:.2f}.")

            # Update final costs
            flight_cost = itinerary.outbound_flight.price + itinerary.return_flight.price
            total_activity_cost = sum(slot.cost for day in itinerary.days for slot in day.slots)
            itinerary.total_cost = flight_cost + total_activity_cost
            itinerary.budget_remaining = itinerary.preferences.budget - itinerary.total_cost
            
            return itinerary, decision_logs

        finally:
            conn.close()
