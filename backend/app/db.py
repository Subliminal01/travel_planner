import os
import duckdb

DB_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "travel_planner.db")

class Database:
    def __init__(self):
        self.db_path = DB_PATH
        self.conn = None
        self.initialize_db()

    def get_connection(self):
        """Returns a connection to the DuckDB database."""
        return duckdb.connect(self.db_path)

    def initialize_db(self):
        """Creates tables if they don't exist and seeds them with mock data."""
        conn = self.get_connection()
        try:
            # 1. Create Tables
            conn.execute("""
                CREATE TABLE IF NOT EXISTS destinations (
                    id VARCHAR PRIMARY KEY,
                    name VARCHAR NOT NULL,
                    country VARCHAR NOT NULL,
                    description VARCHAR,
                    image_url VARCHAR
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS activities (
                    id VARCHAR PRIMARY KEY,
                    destination_id VARCHAR NOT NULL,
                    name VARCHAR NOT NULL,
                    vibe VARCHAR NOT NULL,
                    cost DOUBLE NOT NULL,
                    duration_hours DOUBLE NOT NULL,
                    is_outdoor BOOLEAN NOT NULL,
                    typical_slot VARCHAR NOT NULL,
                    description VARCHAR,
                    rating DOUBLE NOT NULL
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS flights (
                    id VARCHAR PRIMARY KEY,
                    origin VARCHAR NOT NULL,
                    destination_id VARCHAR NOT NULL,
                    airline VARCHAR NOT NULL,
                    price DOUBLE NOT NULL,
                    departure_time VARCHAR NOT NULL,
                    arrival_time VARCHAR NOT NULL,
                    direction VARCHAR NOT NULL
                )
            """)

            conn.execute("""
                CREATE TABLE IF NOT EXISTS weather_forecast (
                    destination_id VARCHAR NOT NULL,
                    day_number INTEGER NOT NULL,
                    condition VARCHAR NOT NULL,
                    temp_c INTEGER NOT NULL,
                    PRIMARY KEY (destination_id, day_number)
                )
            """)

            # 2. Seed Data if destinations table is empty
            count = conn.execute("SELECT COUNT(*) FROM destinations").fetchone()[0]
            if count == 0:
                self.seed_data(conn)
        finally:
            conn.close()

    def seed_data(self, conn):
        """Seeds high-quality mock data into all tables."""
        # A. Destinations
        destinations = [
            ("tokyo", "Tokyo", "Japan", "A futuristic metropolis blending ultra-modern skyscrapers with historic temples, sensory culinary journeys, and serene gardens.", "https://images.unsplash.com/photo-1540959733332-eab4deceeaf7?auto=format&fit=crop&w=800&q=80"),
            ("paris", "Paris", "France", "The global center for art, fashion, gastronomy, and culture, defined by romantic streetscapes, charming bistros, and centuries-old monuments.", "https://images.unsplash.com/photo-1502602898657-3e91760cbb34?auto=format&fit=crop&w=800&q=80"),
            ("bali", "Bali", "Indonesia", "A tropical paradise famed for its forested volcanic mountains, iconic rice paddies, beaches, and vibrant spiritual culture.", "https://images.unsplash.com/photo-1537996194471-e657df975ab4?auto=format&fit=crop&w=800&q=80"),
            ("reykjavik", "Reykjavik", "Iceland", "A vibrant coastal city gateway to geothermal wonders, cascading waterfalls, massive glaciers, and the elusive Northern Lights.", "https://images.unsplash.com/photo-1504829857797-ddff28127792?auto=format&fit=crop&w=800&q=80"),
            ("nyc", "New York City", "USA", "The iconic cultural capital of the world, boasting monumental skyscrapers, Broadway theaters, Central Park, and bustling eclectic neighborhoods.", "https://images.unsplash.com/photo-1496442226666-8d4d0e62e6e9?auto=format&fit=crop&w=800&q=80")
        ]
        conn.executemany("INSERT INTO destinations VALUES (?, ?, ?, ?, ?)", destinations)

        # B. Flights (Outbound & Return)
        # Structure: id, origin, destination_id, airline, price, departure_time, arrival_time, direction
        flights = [
            # Tokyo Flights
            ("F-T-O1", "New York", "tokyo", "Japan Airlines", 650.00, "11:30 AM", "4:15 PM (+1 Day)", "Outbound"),
            ("F-T-O2", "New York", "tokyo", "United Airlines", 580.00, "08:00 AM", "12:30 PM (+1 Day)", "Outbound"),
            ("F-T-R1", "New York", "tokyo", "Japan Airlines", 680.00, "06:00 PM", "05:30 PM", "Return"),
            ("F-T-R2", "New York", "tokyo", "United Airlines", 590.00, "03:45 PM", "03:15 PM", "Return"),

            # Paris Flights
            ("F-P-O1", "New York", "paris", "Air France", 450.00, "07:30 PM", "08:45 AM (+1 Day)", "Outbound"),
            ("F-P-O2", "New York", "paris", "Delta Air Lines", 410.00, "05:00 PM", "06:20 AM (+1 Day)", "Outbound"),
            ("F-P-R1", "New York", "paris", "Air France", 470.00, "01:30 PM", "03:50 PM", "Return"),
            ("F-P-R2", "New York", "paris", "Delta Air Lines", 420.00, "10:30 AM", "12:45 PM", "Return"),

            # Bali Flights
            ("F-B-O1", "New York", "bali", "Singapore Airlines", 850.00, "09:00 AM", "08:30 PM (+1 Day)", "Outbound"),
            ("F-B-O2", "New York", "bali", "Qatar Airways", 790.00, "10:30 PM", "10:15 AM (+2 Days)", "Outbound"),
            ("F-B-R1", "New York", "bali", "Singapore Airlines", 890.00, "09:15 PM", "08:30 AM (+1 Day)", "Return"),
            ("F-B-R2", "New York", "bali", "Qatar Airways", 820.00, "11:45 AM", "09:30 PM", "Return"),

            # Reykjavik Flights
            ("F-R-O1", "New York", "reykjavik", "Icelandair", 320.00, "08:30 PM", "06:15 AM (+1 Day)", "Outbound"),
            ("F-R-O2", "New York", "reykjavik", "PLAY Airlines", 240.00, "07:00 PM", "04:45 AM (+1 Day)", "Outbound"),
            ("F-R-R1", "New York", "reykjavik", "Icelandair", 340.00, "05:00 PM", "07:10 PM", "Return"),
            ("F-R-R2", "New York", "reykjavik", "PLAY Airlines", 260.00, "03:15 PM", "05:30 PM", "Return"),

            # New York Flights (Assume Origin is Los Angeles)
            ("F-N-O1", "Los Angeles", "nyc", "JetBlue Airways", 180.00, "07:30 AM", "03:50 PM", "Outbound"),
            ("F-N-O2", "Los Angeles", "nyc", "American Airlines", 220.00, "11:00 AM", "07:25 PM", "Outbound"),
            ("F-N-R1", "Los Angeles", "nyc", "JetBlue Airways", 190.00, "06:00 PM", "09:15 PM", "Return"),
            ("F-N-R2", "Los Angeles", "nyc", "American Airlines", 230.00, "03:30 PM", "06:45 PM", "Return")
        ]
        conn.executemany("INSERT INTO flights VALUES (?, ?, ?, ?, ?, ?, ?, ?)", flights)

        # C. Activities
        # Structure: id, destination_id, name, vibe, cost, duration_hours, is_outdoor, typical_slot, description, rating
        activities = [
            # ================== TOKYO (14 Activities) ==================
            ("A-T-1", "tokyo", "Tokyo Skytree Observatory Tour", "Adventure", 35.00, 2.0, True, "Morning", "Breathtaking panoramic views of Mt. Fuji and the Tokyo skyline from 450 meters high.", 4.7),
            ("A-T-2", "tokyo", "teamLab Planets Digital Art Museum", "Cultural", 42.00, 3.0, False, "Afternoon", "An immersive body-on museum experience walking through water and giant floating flower gardens.", 4.9),
            ("A-T-3", "tokyo", "Shinjuku Gyoen National Garden Walking Tour", "Relaxing", 5.00, 2.5, True, "Afternoon", "Stroll through historic manicured French, English, and traditional Japanese garden landscapes.", 4.6),
            ("A-T-4", "tokyo", "Traditional Senso-ji Temple & Tea Ceremony", "Cultural", 45.00, 2.0, False, "Morning", "Explore Asakusa's oldest Buddhist temple followed by a private ceremonial matcha tea preparation.", 4.8),
            ("A-T-5", "tokyo", "Mount Takao Hiking Expedition", "Adventure", 15.00, 5.0, True, "Morning", "A scenic trek up a sacred mountain offering vibrant green forests, temples, and beautiful waterfalls.", 4.5),
            ("A-T-6", "tokyo", "Onsen Spa & Hot Springs Experience", "Relaxing", 55.00, 3.0, False, "Evening", "Soak in therapeutic mineral waters and experience traditional Japanese public bathing and saunas.", 4.7),
            ("A-T-7", "tokyo", "Private Sushi Making Masterclass", "Cultural", 95.00, 3.0, False, "Afternoon", "Learn the delicate art of slicing sashimi and forming nigiri from a certified local sushi chef.", 4.8),
            ("A-T-8", "tokyo", "Shibuya Neon Night Street Food Tour", "Adventure", 70.00, 3.5, True, "Evening", "Navigate Shibuya's hidden alleyways to taste yakitori, gyoza, and local draft beers under neon lights.", 4.9),
            ("A-T-9", "tokyo", "Ueno Zoo & Museum of Nature", "Relaxing", 12.00, 4.0, True, "Morning", "A relaxing morning visiting Tokyo's oldest zoo, giant pandas, and world-class historical exhibits.", 4.4),
            ("A-T-10", "tokyo", "Akihabara Indoor VR Gaming Arena", "Adventure", 40.00, 2.0, False, "Afternoon", "Experience cutting-edge Japanese virtual reality simulators and multiplayer high-tech gaming.", 4.6),
            ("A-T-11", "tokyo", "Meguro River Afternoon Cruise", "Relaxing", 30.00, 1.5, True, "Afternoon", "Glide along the famous canal lined with beautiful trees and cityscapes, absolute bliss.", 4.5),
            ("A-T-12", "tokyo", "Roppongi Hills Modern Art Gallery", "Cultural", 18.00, 2.0, False, "Morning", "A high-elevation contemporary art museum showing forward-thinking global works.", 4.4),
            ("A-T-13", "tokyo", "Japanese Cooking Class: Ramen & Gyoza", "Cultural", 65.00, 2.5, False, "Evening", "Prepare rich dashi broths and craft noodles from scratch in an intimate kitchen setting.", 4.7),
            ("A-T-14", "tokyo", "Yoyogi Park & Meiji Shrine Sanctuary Walk", "Relaxing", 0.00, 2.0, True, "Morning", "Stroll through a massive forested park to a grand wooden shrine dedicated to the deified spirits of the Emperor.", 4.7),

            # ================== PARIS (13 Activities) ==================
            ("A-P-1", "paris", "Louvre Museum Guided Masterpieces Tour", "Cultural", 65.00, 3.0, False, "Morning", "Skip the line to explore the world's largest art museum, from the Mona Lisa to the Venus de Milo.", 4.8),
            ("A-P-2", "paris", "Eiffel Tower Summit Access & Champagne", "Adventure", 75.00, 2.0, True, "Evening", "Ascend to the highest accessible platform in Europe for sparkling nighttime skyline views.", 4.7),
            ("A-P-3", "paris", "Seine River Gliding Sightseeing Cruise", "Relaxing", 20.00, 1.5, True, "Afternoon", "Sail past the Notre Dame, Louvre, and Orsay Museum under historic bridges in open-air boats.", 4.6),
            ("A-P-4", "paris", "Macaron Baking Masterclass at Galeries Lafayette", "Cultural", 59.00, 2.0, False, "Afternoon", "Uncover the delicate secrets of whipping meringue and shells for the perfect Parisian macaron.", 4.7),
            ("A-P-5", "paris", "Montmartre Artisanal Vineyard & Artists Walk", "Relaxing", 25.00, 2.5, True, "Morning", "Wander steep cobblestone steps past active vineyards and street portraitists to the Sacré-Cœur.", 4.5),
            ("A-P-6", "paris", "Palace of Versailles Guided Gardens Tour", "Cultural", 40.00, 4.0, True, "Morning", "Walk through spectacular grand fountains, geometric pathways, and the Queen's Hamlet.", 4.8),
            ("A-P-7", "paris", "Opera Garnier Architectural Tour", "Cultural", 15.00, 1.5, False, "Afternoon", "Explore the opulent grand staircase, velvet boxes, and the stage that inspired Phantom of the Opera.", 4.6),
            ("A-P-8", "paris", "Catacombs of Paris Underground Exploration", "Adventure", 35.00, 2.0, False, "Morning", "Descend 20 meters below street level into the beautifully arranged, historic labyrinth of bones.", 4.4),
            ("A-P-9", "paris", "Gourmet French Cheese & Wine Tasting Cellar", "Relaxing", 85.00, 2.0, False, "Evening", "Sip curated vintages matched with artisanal regional cheeses in a cozy 17th-century cellar.", 4.9),
            ("A-P-10", "paris", "Tuileries Gardens Afternoon Picnic", "Relaxing", 10.00, 2.0, True, "Afternoon", "Relax in signature green metal chairs among sculptures, ponds, and flowerbeds near the Louvre.", 4.5),
            ("A-P-11", "paris", "Outdoor Bike Ride Along the Seine", "Adventure", 30.00, 3.0, True, "Afternoon", "A lively guided cycling tour through traffic-free routes alongside historic river monuments.", 4.6),
            ("A-P-12", "paris", "Orsay Museum Impressionist Art Tour", "Cultural", 22.00, 2.5, False, "Afternoon", "Appreciate the world's largest collection of paintings by Monet, Van Gogh, and Renoir inside a grand station.", 4.8),
            ("A-P-13", "paris", "Paris Indoor Climbing Gym Pass", "Adventure", 20.00, 2.0, False, "Evening", "A high-octane bouldering session in a modern, vibrant climbing hall in the Bastille district.", 4.3),

            # ================== BALI (13 Activities) ==================
            ("A-B-1", "bali", "Mount Batur Sunrise Volcano Trek", "Adventure", 65.00, 6.0, True, "Morning", "An early-morning hike up an active volcano to watch the sunrise above the clouds and lake.", 4.9),
            ("A-B-2", "bali", "Ubud Sacred Monkey Forest Sanctuary", "Relaxing", 8.00, 2.0, True, "Morning", "Wander ancient paths under giant banyan trees home to over 700 gray long-tailed macaques.", 4.6),
            ("A-B-3", "bali", "Canggu Surf Lesson with Local Pros", "Adventure", 35.00, 2.0, True, "Afternoon", "Learn ocean safety, paddling, and pop-ups before riding the beginner-friendly waves of Batu Bolong.", 4.7),
            ("A-B-4", "bali", "Traditional Balinese Herbal Spa Treatment", "Relaxing", 45.00, 2.5, False, "Evening", "Unwind with full-body massages, volcanic clay scrubs, and a therapeutic hot flower bath.", 4.8),
            ("A-B-5", "bali", "Tegallalang Scenic Rice Terraces Walk", "Relaxing", 5.00, 2.0, True, "Afternoon", "Climb steep terraced fields and capture photos on world-famous giant valley swings.", 4.5),
            ("A-B-6", "bali", "Balinese Cooking Masterclass in organic farm", "Cultural", 50.00, 4.0, False, "Morning", "Harvest fresh lemongrass, ginger, and spices before cooking traditional chicken betutu and sambal.", 4.9),
            ("A-B-7", "bali", "Uluwatu Temple Cliff Walk & Kecak Dance", "Cultural", 25.00, 3.0, True, "Evening", "Witness a magnificent sunset atop a 70-meter ocean cliff followed by the traditional fire dance.", 4.8),
            ("A-B-8", "bali", "Nusa Penida Snorkeling: Manta Rays Search", "Adventure", 90.00, 6.0, True, "Morning", "Speedboat to clear waters to swim with giant, gentle oceanic manta rays and view pristine coral walls.", 4.7),
            ("A-B-9", "bali", "Ubud Royal Palace & Art Museum Tour", "Cultural", 15.00, 2.0, False, "Afternoon", "Appreciate beautiful stone carvings at the palace and curated Balinese paintings in the Agung Rai museum.", 4.5),
            ("A-B-10", "bali", "Yoga & Meditation Sanctuary Session", "Relaxing", 20.00, 1.5, False, "Morning", "An indoor therapeutic yoga practice looking out onto calm jungle ravines in Ubud.", 4.7),
            ("A-B-11", "bali", "Canggu Indoor Skatepark & Arcade", "Adventure", 15.00, 2.5, False, "Afternoon", "An action-packed afternoon in a dynamic indoor bowl, halfpipe, and classic retro arcade center.", 4.4),
            ("A-B-12", "bali", "Coffee Plantation & Tasting Experience", "Relaxing", 12.00, 1.5, True, "Afternoon", "Stroll through organic coffee crops and sample robust herbal teas, cocoas, and specialty brews.", 4.4),
            ("A-B-13", "bali", "Balian River Rafting Adventure", "Adventure", 40.00, 3.5, True, "Morning", "Rush down Grade II and III rapids past lush rainforests, gorges, and hidden waterfalls.", 4.6),

            # ================== REYKJAVIK (13 Activities) ==================
            ("A-R-1", "reykjavik", "Blue Lagoon Geothermal Luxury Spa", "Relaxing", 95.00, 4.0, True, "Afternoon", "Relax in warm, milky-blue mineral waters surrounded by dramatic, jet-black volcanic lava fields.", 4.8),
            ("A-R-2", "reykjavik", "Golden Circle Guided Day Tour", "Adventure", 80.00, 8.0, True, "Morning", "Witness the dramatic double-cascade Gullfoss waterfall, erupting geysers, and tectonic rifts.", 4.9),
            ("A-R-3", "reykjavik", "Northern Lights Yacht Hunting Cruise", "Adventure", 90.00, 3.0, True, "Evening", "Sail away from city light pollution into dark oceanic bays to watch vibrant green auroras dance.", 4.6),
            ("A-R-4", "reykjavik", "Perlan Museum: Wonders of Iceland Show", "Cultural", 38.00, 2.5, False, "Morning", "Walk through a real 100-meter indoor ice cave and experience a premium 8K Northern Lights planetarium show.", 4.7),
            ("A-R-5", "reykjavik", "Icelandic Lava Tunnel Spelunking", "Adventure", 75.00, 3.0, False, "Afternoon", "Walk along the pathway formed by flowing volcanic magma thousands of years ago in massive caves.", 4.8),
            ("A-R-6", "reykjavik", "National Museum of Iceland Exploration", "Cultural", 20.00, 2.0, False, "Morning", "Trace history from Viking settlement longhouses and broadswords to modern-day statehood.", 4.5),
            ("A-R-7", "reykjavik", "FlyOver Iceland Virtual Flight Simulator", "Adventure", 45.00, 1.5, False, "Afternoon", "A state-of-the-art motion theater taking you on a breathtaking aerial journey over glaciers and peaks.", 4.9),
            ("A-R-8", "reykjavik", "Laugardalslaug Geothermal Public Pools", "Relaxing", 10.00, 2.5, True, "Evening", "Soak like a true local in Reykjavik's largest outdoor heated pool, steam baths, and hot tubs.", 4.6),
            ("A-R-9", "reykjavik", "Charming Old Harbor Food & Brewery Walk", "Relaxing", 85.00, 3.0, True, "Evening", "Taste smoked puffin, lobster soup, and local craft microbrews along the historic waterfront docks.", 4.7),
            ("A-R-10", "reykjavik", "Hallgrimskirkja Cathedral & Pipe Organ Tour", "Cultural", 12.00, 1.0, False, "Morning", "Ascend the iconic concrete tower for spectacular city views and hear the 5,000-pipe organ.", 4.5),
            ("A-R-11", "reykjavik", "South Coast Glacier Hike & Waterfalls", "Adventure", 110.00, 9.0, True, "Morning", "Strap on crampons to walk across active glaciers and stand behind the roaring Seljalandsfoss waterfall.", 4.9),
            ("A-R-12", "reykjavik", "Harpa Concert Hall Architecture Tour", "Cultural", 15.00, 1.5, False, "Afternoon", "Explore the stunning modern glass facade reflecting harbor light, winner of architectural awards.", 4.6),
            ("A-R-13", "reykjavik", "Cozy Icelandic Wool Knitting Workshop", "Relaxing", 40.00, 2.0, False, "Afternoon", "Learn history and pattern designs of the famous Lopapeysa wool sweaters in a cozy tea shop.", 4.4),

            # ================== NEW YORK CITY (13 Activities) ==================
            ("A-N-1", "nyc", "Broadway Musical Orchestra Seat", "Cultural", 145.00, 3.0, False, "Evening", "Experience a world-class theater production with incredible performances in the heart of Times Square.", 4.9),
            ("A-N-2", "nyc", "Central Park Bike Tour & Picnic", "Relaxing", 40.00, 3.0, True, "Morning", "Cycle past Bethesda Fountain, Strawberry Fields, and sheep meadows, with a fresh gourmet picnic lunch.", 4.7),
            ("A-N-3", "nyc", "The Metropolitan Museum of Art Tour", "Cultural", 30.00, 3.5, False, "Afternoon", "Explore 5,000 years of global human history, from Egyptian temples to historic American wings.", 4.8),
            ("A-N-4", "nyc", "Top of the Rock Skyline Climbing Observatory", "Adventure", 45.00, 2.0, True, "Evening", "Stunning open-air, 360-degree views of the Empire State Building and sweeping Central Park vistas.", 4.6),
            ("A-N-5", "nyc", "Chelsea Market & High Line Walking Tour", "Relaxing", 20.00, 2.5, True, "Morning", "Walk along a historic elevated railway turned park, stopping to taste artisanal treats at the market.", 4.6),
            ("A-N-6", "nyc", "Statue of Liberty & Ellis Island Ferry", "Cultural", 25.00, 4.0, True, "Morning", "Take a scenic harbor cruise to stand before the monument of freedom and explore historical records.", 4.7),
            ("A-N-7", "nyc", "Intrepid Sea, Air & Space Museum", "Adventure", 33.00, 2.5, False, "Afternoon", "Step aboard a historic aircraft carrier, inspect fighter jets, and stand close to the Enterprise space shuttle.", 4.5),
            ("A-N-8", "nyc", "Brooklyn Bridge Sunset Bike Ride", "Adventure", 35.00, 2.0, True, "Evening", "Pedal along the dedicated boardwalk lane high above the river, catching magical Manhattan skyline lights.", 4.7),
            ("A-N-9", "nyc", "SoHo Artisanal Coffee & Pastry Crawl", "Relaxing", 15.00, 2.0, True, "Afternoon", "Sample classic New York bagels, cronuts, and single-origin espresso inside chic cast-iron lofts.", 4.4),
            ("A-N-10", "nyc", "Museum of Modern Art (MoMA) Ticket", "Cultural", 25.00, 2.5, False, "Afternoon", "View Starry Night, The Persistence of Memory, and iconic works of abstract expressionism.", 4.7),
            ("A-N-11", "nyc", "Spyscape: Interactive Spy Museum", "Adventure", 42.00, 2.0, False, "Afternoon", "Test your spy skills with laser mazes, lie detector tests, and cryptology puzzles.", 4.6),
            ("A-N-12", "nyc", "AIA Manhattan Architecture Yacht Cruise", "Relaxing", 65.00, 2.5, True, "Afternoon", "Circumnavigate Manhattan on an elegant 1920s-style yacht with detailed architecture commentary.", 4.8),
            ("A-N-13", "nyc", "Manhattan Indoor Trapeze & Acrobatics School", "Adventure", 75.00, 2.0, False, "Morning", "Learn to swing, hang, and catch on full-scale indoor flying trapezes with professional coaches.", 4.7)
        ]
        conn.executemany("INSERT INTO activities VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)", activities)

        # D. Weather Forecast
        # Seeding weather states for Day 1 to Day 10 for each destination.
        # Structure: destination_id, day_number, condition, temp_c
        weather = []
        for dest in ["tokyo", "paris", "bali", "reykjavik", "nyc"]:
            # Default weather
            if dest == "tokyo":
                weather.extend([
                    ("tokyo", 1, "Sunny", 22),
                    ("tokyo", 2, "Sunny", 23),
                    ("tokyo", 3, "Cloudy", 20),
                    ("tokyo", 4, "Sunny", 22),
                    ("tokyo", 5, "Sunny", 24),
                    ("tokyo", 6, "Rainy", 18),
                    ("tokyo", 7, "Sunny", 21)
                ])
            elif dest == "paris":
                weather.extend([
                    ("paris", 1, "Cloudy", 16),
                    ("paris", 2, "Sunny", 18),
                    ("paris", 3, "Rainy", 15),
                    ("paris", 4, "Sunny", 19),
                    ("paris", 5, "Sunny", 20),
                    ("paris", 6, "Cloudy", 17),
                    ("paris", 7, "Sunny", 18)
                ])
            elif dest == "bali":
                weather.extend([
                    ("bali", 1, "Sunny", 29),
                    ("bali", 2, "Sunny", 30),
                    ("bali", 3, "Sunny", 31),
                    ("bali", 4, "Rainy", 28),
                    ("bali", 5, "Sunny", 30),
                    ("bali", 6, "Sunny", 29),
                    ("bali", 7, "Sunny", 30)
                ])
            elif dest == "reykjavik":
                weather.extend([
                    ("reykjavik", 1, "Cloudy", 8),
                    ("reykjavik", 2, "Cloudy", 7),
                    ("reykjavik", 3, "Rainy", 6),
                    ("reykjavik", 4, "Sunny", 9),
                    ("reykjavik", 5, "Cloudy", 8),
                    ("reykjavik", 6, "Rainy", 5),
                    ("reykjavik", 7, "Sunny", 9)
                ])
            elif dest == "nyc":
                weather.extend([
                    ("nyc", 1, "Sunny", 20),
                    ("nyc", 2, "Sunny", 21),
                    ("nyc", 3, "Cloudy", 19),
                    ("nyc", 4, "Sunny", 22),
                    ("nyc", 5, "Sunny", 23),
                    ("nyc", 6, "Rainy", 18),
                    ("nyc", 7, "Sunny", 21)
                ])
        conn.executemany("INSERT INTO weather_forecast VALUES (?, ?, ?, ?)", weather)
