# weather_collector.py - Collecting and storing weather data
import requests
import sqlite3
from datetime import datetime
import time

class WeatherCollector:
    """
    Collects weather data from API and stores in database
    IMPROVED VERSION: Handles location ambiguity properly
    """
    
    def __init__(self, db_name='weather.db'):
        self.db_name = db_name
        self.base_url = "https://wttr.in"
        self._init_database()
    
    def _init_database(self):
        """Create weather data table with country and coordinates"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weather_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city TEXT NOT NULL,
                country TEXT NOT NULL,
                latitude REAL,
                longitude REAL,
                date TEXT NOT NULL,
                temp_c REAL,
                feels_like_c REAL,
                condition TEXT,
                humidity INTEGER,
                wind_speed_kmph REAL,
                pressure_mb REAL,
                visibility_km REAL,
                uv_index INTEGER,
                timestamp TEXT NOT NULL,
                UNIQUE(city, country, date, timestamp)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✓ Database initialized")
    
    def fetch_weather(self, city, country=None, lat=None, lon=None):
        """
        Fetch weather with multiple ways to specify location
        
        Parameters:
        - city: City name (required)
        - country: Country name (recommended to avoid ambiguity)
        - lat: Latitude (most precise, optional)
        - lon: Longitude (most precise, optional)
        
        Priority:
        1. lat/lon (most precise)
        2. city,country (specific)
        3. city only (might be ambiguous)
        """
        
        # Build location string based on what's provided
        if lat is not None and lon is not None:
            location = f"{lat},{lon}"
            print(f"📍 Using coordinates: {location}")
        elif country:
            location = f"{city},{country}"
            print(f"📍 Using city and country: {location}")
        else:
            location = city
            print(f"⚠️  Using city only (might be ambiguous): {location}")
        
        url = f"{self.base_url}/{location}?format=j1"
        
        try:
            print(f"Fetching weather data from API...")
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # Extract and verify what location was actually returned
                nearest = data.get('nearest_area', [{}])[0]
                returned_city = nearest.get('areaName', [{}])[0].get('value', 'Unknown')
                returned_country = nearest.get('country', [{}])[0].get('value', 'Unknown')
                returned_lat = nearest.get('latitude', 'Unknown')
                returned_lon = nearest.get('longitude', 'Unknown')
                
                print(f"✓ API returned: {returned_city}, {returned_country}")
                print(f"  Coordinates: {returned_lat}, {returned_lon}")
                
                # Warn if there's a mismatch
                if country and returned_country.lower() != country.lower():
                    print(f"⚠️  WARNING: Expected {country}, got {returned_country}")
                    print(f"  This might not be the location you wanted!")
                
                # Store the verified location info in the data
                data['_verified_location'] = {
                    'city': returned_city,
                    'country': returned_country,
                    'latitude': returned_lat,
                    'longitude': returned_lon
                }
                
                return data
            else:
                print(f"❌ Error: Status code {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            print("❌ Request timed out")
            return None
        except requests.exceptions.ConnectionError:
            print("❌ Connection error - check internet")
            return None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def parse_weather_data(self, data, requested_city, requested_country=None):
        """
        Extract relevant information from API response
        Uses verified location from API response
        """
        try:
            current = data['current_condition'][0]
            verified = data.get('_verified_location', {})
            
            weather_record = {
                'city': verified.get('city', requested_city),
                'country': verified.get('country', requested_country or 'Unknown'),
                'latitude': verified.get('latitude'),
                'longitude': verified.get('longitude'),
                'date': datetime.now().strftime('%Y-%m-%d'),
                'temp_c': float(current['temp_C']),
                'feels_like_c': float(current['FeelsLikeC']),
                'condition': current['weatherDesc'][0]['value'],
                'humidity': int(current['humidity']),
                'wind_speed_kmph': float(current['windspeedKmph']),
                'pressure_mb': float(current['pressure']),
                'visibility_km': float(current['visibility']),
                'uv_index': int(current['uvIndex']),
                'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            }
            
            return weather_record
            
        except Exception as e:
            print(f"❌ Error parsing data: {e}")
            return None
    
    def save_weather_data(self, weather_record):
        """Save weather data to database with location verification"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO weather_data 
                (city, country, latitude, longitude, date, temp_c, feels_like_c, 
                 condition, humidity, wind_speed_kmph, pressure_mb, 
                 visibility_km, uv_index, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                weather_record['city'],
                weather_record['country'],
                weather_record['latitude'],
                weather_record['longitude'],
                weather_record['date'],
                weather_record['temp_c'],
                weather_record['feels_like_c'],
                weather_record['condition'],
                weather_record['humidity'],
                weather_record['wind_speed_kmph'],
                weather_record['pressure_mb'],
                weather_record['visibility_km'],
                weather_record['uv_index'],
                weather_record['timestamp']
            ))
            
            conn.commit()
            print(f"✓ Weather data saved: {weather_record['city']}, {weather_record['country']}")
            return True
            
        except sqlite3.IntegrityError:
            print(f"⚠️  Data already exists for {weather_record['city']}, {weather_record['country']} at this time")
            return False
        except Exception as e:
            print(f"❌ Error saving data: {e}")
            return False
        finally:
            conn.close()
    
    def collect_and_store(self, city, country=None, lat=None, lon=None):
        """
        Complete pipeline: fetch, parse, and store weather data
        
        Examples:
        - collect_and_store('Athens', country='Greece')
        - collect_and_store('Paris', country='France')
        - collect_and_store('Athens', lat=37.9838, lon=23.7275)
        """
        print("\n" + "=" * 70)
        print(f"COLLECTING WEATHER DATA FOR {city.upper()}")
        if country:
            print(f"Country: {country}")
        if lat and lon:
            print(f"Coordinates: {lat}, {lon}")
        print("=" * 70)
        
        # Step 1: Fetch from API
        data = self.fetch_weather(city, country, lat, lon)
        if not data:
            print("❌ Failed to fetch data")
            return False
        
        # Step 2: Parse the data
        weather_record = self.parse_weather_data(data, city, country)
        if not weather_record:
            print("❌ Failed to parse data")
            return False
        
        # Step 3: Store in database
        success = self.save_weather_data(weather_record)
        
        # Step 4: Display summary
        if success:
            print("\n📊 Collected Weather Data:")
            print(f"  Location: {weather_record['city']}, {weather_record['country']}")
            print(f"  Coordinates: {weather_record['latitude']}, {weather_record['longitude']}")
            print(f"  Temperature: {weather_record['temp_c']}°C")
            print(f"  Feels like: {weather_record['feels_like_c']}°C")
            print(f"  Condition: {weather_record['condition']}")
            print(f"  Humidity: {weather_record['humidity']}%")
            print(f"  Wind: {weather_record['wind_speed_kmph']} km/h")
            print(f"  Timestamp: {weather_record['timestamp']}")
        
        return success
    
    def get_all_weather_data(self):
        """Retrieve all stored weather data"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT city, country, date, temp_c, condition, timestamp 
            FROM weather_data 
            ORDER BY timestamp DESC
        """)
        rows = cursor.fetchall()
        
        conn.close()
        return rows
    
    def get_weather_count(self):
        """Get total number of weather records"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute("SELECT COUNT(*) FROM weather_data")
        count = cursor.fetchone()[0]
        
        conn.close()
        return count
    
    def get_cities_tracked(self):
        """Get list of unique cities being tracked"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT DISTINCT city, country 
            FROM weather_data 
            ORDER BY city
        """)
        cities = cursor.fetchall()
        
        conn.close()
        return cities


# ===== TEST SCENARIOS =====

def test_location_handling():
    """Test different ways of specifying locations"""
    print("\n" + "=" * 70)
    print("TESTING LOCATION HANDLING")
    print("=" * 70)
    
    collector = WeatherCollector()
    
    # Scenario 1: Ambiguous - just city name
    print("\n### SCENARIO 1: Ambiguous - just 'Athens' ###")
    print("Expected: Might get Athens, GA, USA (API's default)")
    collector.collect_and_store('Athens')
    time.sleep(2)
    
    # Scenario 2: Specific - city + country
    print("\n### SCENARIO 2: Specific - 'Athens, Greece' ###")
    print("Expected: Athens, Greece")
    collector.collect_and_store('Athens', country='Greece')
    time.sleep(2)
    
    # Scenario 3: Most precise - coordinates
    print("\n### SCENARIO 3: Most Precise - Athens, Greece coordinates ###")
    print("Expected: Athens, Greece (guaranteed)")
    collector.collect_and_store('Athens', country='Greece', lat=37.9838, lon=23.7275)
    time.sleep(2)
    
    # Scenario 4: Another Athens for comparison
    print("\n### SCENARIO 4: Athens, USA for comparison ###")
    print("Expected: Athens, GA, USA")
    collector.collect_and_store('Athens', country='USA')
    time.sleep(2)
    
    # Show summary
    print("\n" + "=" * 70)
    print("COLLECTION SUMMARY")
    print("=" * 70)
    print(f"Total records: {collector.get_weather_count()}")
    
    print("\nCities tracked:")
    for city, country in collector.get_cities_tracked():
        print(f"  • {city}, {country}")
    
    print("\nRecent weather data:")
    print("-" * 70)
    for row in collector.get_all_weather_data()[:10]:
        city, country, date, temp, condition, timestamp = row
        print(f"  {city}, {country} on {date}: {temp}°C - {condition}")


def collect_multiple_cities():
    """Collect data for multiple specific cities"""
    print("\n" + "=" * 70)
    print("COLLECTING DATA FOR MULTIPLE CITIES")
    print("=" * 70)
    
    collector = WeatherCollector()
    
    # Define cities with their countries to avoid ambiguity
    cities = [
        {'city': 'Athens', 'country': 'Greece'},
        {'city': 'London', 'country': 'UK'},
        {'city': 'Paris', 'country': 'France'},
        {'city': 'Berlin', 'country': 'Germany'},
        {'city': 'Rome', 'country': 'Italy'},
        {'city': 'Madrid', 'country': 'Spain'},
    ]
    
    for location in cities:
        collector.collect_and_store(location['city'], country=location['country'])
        time.sleep(2)  # Be respectful to the API
    
    # Summary
    print("\n" + "=" * 70)
    print("COLLECTION COMPLETE")
    print("=" * 70)
    print(f"Total records: {collector.get_weather_count()}")
    
    print("\nAll cities being tracked:")
    for city, country in collector.get_cities_tracked():
        print(f"  • {city}, {country}")


# ===== MAIN PROGRAM =====

if __name__ == "__main__":
    import sys
    
    print("\n" + "=" * 70)
    print("WEATHER DATA COLLECTOR")
    print("=" * 70)
    
    print("\nWhat would you like to do?")
    print("1. Test location handling (shows ambiguity issues)")
    print("2. Collect data for multiple European cities")
    print("3. Collect for a single city")
    
    choice = input("\nEnter choice (1-3): ").strip()
    
    if choice == '1':
        test_location_handling()
    elif choice == '2':
        collect_multiple_cities()
    elif choice == '3':
        collector = WeatherCollector()
        city = input("Enter city name: ").strip()
        country = input("Enter country (or press Enter to skip): ").strip()
        
        if country:
            collector.collect_and_store(city, country=country)
        else:
            print("⚠️  Warning: Collecting without country may be ambiguous!")
            collector.collect_and_store(city)
        
        # Show what was collected
        print("\nAll collected data:")
        for row in collector.get_all_weather_data()[:5]:
            city, country, date, temp, condition, timestamp = row
            print(f"  {city}, {country}: {temp}°C - {condition}")
    else:
        print("Invalid choice. Running default test...")
        test_location_handling()
    
    print("\n" + "=" * 70)
    print("DONE!")
    print("=" * 70)
