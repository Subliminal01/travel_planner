from typing import List, Optional, Set

from .db import Database
from .schemas import (
    ItineraryPreference, Itinerary, ItineraryDay, ItinerarySlot,
    Flight, Activity, WeatherForecast, DisruptionRequest
)

class ItineraryEngine:
    def __init__(self):
        self.db = Database()

    @staticmethod
    def _destination_label(pref: ItineraryPreference) -> str:
        return pref.destination_name or pref.destination_id.replace("-", " ").title()

    @staticmethod
    def _build_fallback_flights(pref: ItineraryPreference) -> tuple[Flight, Flight]:
        destination = pref.destination_id
        destination_name = pref.destination_name or destination.replace("-", " ").title()
        outbound_price = round(max(90.0, min(650.0, pref.budget * 0.18)), 2)
        return_price = round(max(90.0, min(650.0, pref.budget * 0.17)), 2)

        return (
            Flight(
                id=f"custom-{destination}-outbound",
                origin=pref.origin,
                destination_id=destination,
                airline="Aether Connect",
                price=outbound_price,
                departure_time="09:30 AM",
                arrival_time=f"02:15 PM ({destination_name})",
                direction="Outbound"
            ),
            Flight(
                id=f"custom-{destination}-return",
                origin=pref.origin,
                destination_id=destination,
                airline="Aether Connect",
                price=return_price,
                departure_time="05:45 PM",
                arrival_time=f"10:10 PM ({pref.origin})",
                direction="Return"
            )
        )

    @staticmethod
    def _build_fallback_activities(pref: ItineraryPreference) -> List[Activity]:
        destination = pref.destination_id
        destination_name = pref.destination_name or destination.replace("-", " ").title()
        templates = [
            ("old-town-walk", "Cultural", 0.0, 2.0, True, "Morning", "Historic Neighborhood Walk", "Explore landmark streets, markets, public squares, and local stories with a self-guided route.", 4.4),
            ("signature-viewpoint", "Adventure", 18.0, 2.0, True, "Morning", "Signature Viewpoint Hike", "Start the day with a scenic overlook, city panorama, or nature trail near the destination.", 4.5),
            ("local-museum", "Cultural", 24.0, 2.5, False, "Afternoon", "Local Culture Museum", "Spend the afternoon indoors learning the region's art, history, food, and design traditions.", 4.6),
            ("food-market", "Relaxing", 28.0, 2.0, False, "Afternoon", "Food Market Tasting Trail", "Sample approachable local snacks, coffee, sweets, and street-food favorites at a central market.", 4.5),
            ("outdoor-quarter", "Adventure", 35.0, 3.0, True, "Afternoon", "Outdoor Discovery Quarter", "Walk through parks, waterfronts, gardens, or active neighborhoods with flexible sightseeing stops.", 4.4),
            ("wellness-evening", "Relaxing", 38.0, 2.0, False, "Evening", "Wellness & Slow Evening", "Recharge with a spa, bathhouse, calm cafe, or scenic low-key evening after a busy day.", 4.5),
            ("night-food-tour", "Adventure", 45.0, 2.5, True, "Evening", "Night Food & Lights Tour", "Experience the destination after dark through safe, lively dining streets and illuminated landmarks.", 4.6),
            ("dining-experience", "Cultural", 55.0, 2.0, False, "Evening", "Regional Dinner Experience", "Reserve an evening meal centered on regional specialties and a relaxed cultural atmosphere.", 4.7),
            ("free-public-space", "Relaxing", 0.0, 1.5, True, "Afternoon", "Public Garden or Waterfront Break", "Keep the budget balanced with a calm open-air pause in a beautiful public space.", 4.3),
        ]

        return [
            Activity(
                id=f"custom-{destination}-{activity_id}",
                destination_id=destination,
                name=f"{destination_name} {name}",
                vibe=vibe,
                cost=cost,
                duration_hours=duration,
                is_outdoor=is_outdoor,
                typical_slot=slot,
                description=description,
                rating=rating
            )
            for activity_id, vibe, cost, duration, is_outdoor, slot, name, description, rating in templates
        ]

    @staticmethod
    def _activity_from_row(row) -> Activity:
        return Activity(
            id=row[0],
            destination_id=row[1],
            name=row[2],
            vibe=row[3],
            cost=row[4],
            duration_hours=row[5],
            is_outdoor=row[6],
            typical_slot=row[7],
            description=row[8],
            rating=row[9]
        )

    @staticmethod
    def _calculate_total_cost(days: List[ItineraryDay], flight_cost: float) -> float:
        return flight_cost + sum(slot.cost for day in days for slot in day.slots)

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

            if out_row and ret_row:
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
            else:
                outbound_flight, return_flight = self._build_fallback_flights(pref)

            flight_cost = outbound_flight.price + return_flight.price
            activity_budget = pref.budget - flight_cost

            # 2. Fetch all available activities
            activities_cursor = conn.execute(
                "SELECT id, destination_id, name, vibe, cost, duration_hours, is_outdoor, typical_slot, description, rating "
                "FROM activities WHERE destination_id = ?",
                [pref.destination_id]
            ).fetchall()

            activities_pool = [self._activity_from_row(row) for row in activities_cursor]
            if not activities_pool:
                activities_pool = self._build_fallback_activities(pref)

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
                            time_slot=slot,
                            activity=act,
                            cost=act.cost if act else 0.0
                        ))
                        
                        if act:
                            used_activities.add(act.id)
                            activity_budget -= act.cost

                days_list.append(ItineraryDay(day_number=d, weather=weather, slots=slots))

            # 4. Calculate total cost and balance
            total_cost = self._calculate_total_cost(days_list, flight_cost)
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
                              used: Set[str], max_cost: float, force_indoor: bool = False) -> Optional[Activity]:
        """Helper to score and select the best matching activity from the pool."""
        def score_activity(act: Activity) -> float:
            score = act.rating
            if act.vibe == preferred_vibe:
                score += 5.0
            return score

        candidates = (
            act for act in pool
            if act.id not in used
            and act.typical_slot == slot
            and act.cost <= max_cost
            and (not force_indoor or not act.is_outdoor)
        )

        best = max(candidates, key=score_activity, default=None)
        if best:
            return best

        if force_indoor:
            fallback_candidates = (
                act for act in pool
                if act.id not in used
                and not act.is_outdoor
                and act.cost <= max_cost
            )
            return max(fallback_candidates, key=score_activity, default=None)

        return None

    def _find_cheaper_activity(self, pool: List[Activity], slot_name: str, current_cost: float,
                               used: Set[str]) -> Optional[Activity]:
        return min(
            (
                act for act in pool
                if act.id not in used
                and act.typical_slot == slot_name
                and act.cost < current_cost
            ),
            key=lambda act: act.cost,
            default=None
        )

    def _find_free_activity(self, pool: List[Activity], used: Set[str]) -> Optional[Activity]:
        return next((act for act in pool if act.id not in used and act.cost == 0.0), None)

    def _optimize_budget_on_generation(self, days: List[ItineraryDay], budget: float, flight_cost: float,
                                       pool: List[Activity], used: Set[str]):
        """Performs greedy optimization to bring a generated itinerary within budget."""
        current_total = self._calculate_total_cost(days, flight_cost)

        while current_total > budget:
            most_expensive = None
            for d_idx, day in enumerate(days):
                for s_idx, slot in enumerate(day.slots):
                    if slot.activity and (most_expensive is None or slot.activity.cost > most_expensive[0]):
                        most_expensive = (slot.activity.cost, d_idx, s_idx, slot)

            if not most_expensive or most_expensive[0] <= 0.0:
                break

            max_cost, target_day_idx, target_slot_idx, most_expensive_slot = most_expensive
            old_act = most_expensive_slot.activity
            slot_name = days[target_day_idx].slots[target_slot_idx].time_slot

            alternative = self._find_cheaper_activity(pool, slot_name, max_cost, used)
            if alternative:
                used.discard(old_act.id)
                used.add(alternative.id)
                most_expensive_slot.activity = alternative
                most_expensive_slot.cost = alternative.cost
            else:
                free_alt = self._find_free_activity(pool, used)
                used.discard(old_act.id)
                if free_alt:
                    used.add(free_alt.id)
                    most_expensive_slot.activity = free_alt
                    most_expensive_slot.cost = 0.0
                else:
                    most_expensive_slot.activity = None
                    most_expensive_slot.cost = 0.0

            current_total = self._calculate_total_cost(days, flight_cost)

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

            activities_pool = [self._activity_from_row(row) for row in activities_cursor]
            if not activities_pool:
                activities_pool = self._build_fallback_activities(req.preferences)

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
                            used_activities.discard(old_act.id)
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
                        used_activities.discard(act.id)
                        alternative = self._find_cheaper_activity(
                            activities_pool, slot_name, act.cost, used_activities
                        )
                        
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
                            free_alt = self._find_free_activity(activities_pool, used_activities)
                            
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
            itinerary.total_cost = self._calculate_total_cost(itinerary.days, flight_cost)
            itinerary.budget_remaining = itinerary.preferences.budget - itinerary.total_cost
            
            return itinerary, decision_logs

        finally:
            conn.close()
