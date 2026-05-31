import sys
import os

# Append the project root so Python can locate the app module
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.engine import ItineraryEngine
from app.schemas import ItineraryPreference, DisruptionRequest

def run_tests():
    print("🚀 Starting Itinerary Engine Tests...")
    engine = ItineraryEngine()
    
    # Define preferences for a 4-day trip to Tokyo
    pref = ItineraryPreference(
        origin="New York",
        destination_id="tokyo",
        vibe="Adventure",
        budget=2000.0,
        days=4,
        start_date="2026-06-01"
    )
    
    # 1. Generate Itinerary
    print("\n--- Test 1: Initial Generation ---")
    itinerary = engine.generate_itinerary(pref)
    print(f"✅ Itinerary generated successfully!")
    print(f"Destination: {itinerary.preferences.destination_id.capitalize()}")
    print(f"Total Cost: ${itinerary.total_cost:.2f} (Budget: ${itinerary.preferences.budget:.2f})")
    print(f"Outbound Flight: {itinerary.outbound_flight.airline} (${itinerary.outbound_flight.price:.2f})")
    print(f"Return Flight: {itinerary.return_flight.airline} (${itinerary.return_flight.price:.2f})")
    
    assert itinerary.total_cost <= pref.budget, "Error: Generated itinerary exceeds budget!"
    print("✅ Initial Generation test passed!")

    # 2. Weather Disruption on Day 2
    print("\n--- Test 2: Weather Disruption on Day 2 (Thunderstorm) ---")
    # Find if there's any outdoor activity scheduled on Day 2 before disruption
    day2 = next(d for d in itinerary.days if d.day_number == 2)
    outdoor_before = [s.activity.name for s in day2.slots if s.activity and s.activity.is_outdoor]
    print(f"Outdoor activities on Day 2 BEFORE: {outdoor_before}")

    req_weather = DisruptionRequest(
        preferences=pref,
        current_itinerary=itinerary,
        disruption_type="WEATHER",
        day_number=2,
        weather_condition="Thunderstorm"
    )
    
    recalc_itin, logs = engine.recalculate_itinerary(req_weather)
    
    day2_recalc = next(d for d in recalc_itin.days if d.day_number == 2)
    outdoor_after = [s.activity.name for s in day2_recalc.slots if s.activity and s.activity.is_outdoor]
    print(f"Outdoor activities on Day 2 AFTER: {outdoor_after}")
    
    print("\nDecision Logs:")
    for log in logs:
        print(f"  {log}")
        
    assert len(outdoor_after) == 0 or len(outdoor_after) < len(outdoor_before), "Error: Outdoor activities were not successfully swapped out!"
    print("✅ Weather Disruption test passed!")

    # 3. Budget Cut Disruption (30%)
    print("\n--- Test 3: Budget Cut Disruption (30%) ---")
    cost_before = recalc_itin.total_cost
    budget_before = recalc_itin.preferences.budget
    print(f"Total Cost BEFORE: ${cost_before:.2f} (Budget: ${budget_before:.2f})")
    
    req_budget = DisruptionRequest(
        preferences=pref,
        current_itinerary=recalc_itin,
        disruption_type="BUDGET",
        budget_reduction_percent=30.0
    )
    
    final_itin, logs_budget = engine.recalculate_itinerary(req_budget)
    
    print(f"Total Cost AFTER: ${final_itin.total_cost:.2f} (New Budget: ${final_itin.preferences.budget:.2f})")
    print("\nDecision Logs:")
    for log in logs_budget:
        print(f"  {log}")
        
    assert final_itin.total_cost <= final_itin.preferences.budget, "Error: Optimized cost exceeds new budget limit!"
    print("✅ Budget Optimization test passed!")
    
    print("\n🎉 ALL TESTS PASSED SUCCESSFULLY!")

if __name__ == "__main__":
    run_tests()
