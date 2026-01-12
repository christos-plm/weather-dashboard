# weather_collector.py - Collecting and storing weather data
import requests
import sqlite3
from datetime import datetime
import time

class WeatherCollector:
    """Collects weather data from API and stores in database"""
    
    def __init__(self, db_name='weather.db'):
        self.db_name = db_name
        self.base_url = "https://wttr.in"
        self._init_database()
    
    def _init_database(self):
        """Create weather data table"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS weather_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                city TEXT NOT NULL,
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
                UNIQUE(city, date, timestamp)
            )
        ''')
        
        conn.commit()
        conn.close()
        print("✓ Database initialized")
    
    def fetch_weather(self, city):
        """Fetch current weather data for a city"""
        url = f"{self.base_url}/{city}?format=j1"
        
        try:
            print(f"Fetching weather data for {city}...")
            response = requests.get(url, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                return data
            else:
                print(f"❌ Error: Status code {response.status_code}")
                return None
                
        except requests.exceptions.Timeout:
            print("❌ Request timed out")
            return None
        except requests.exceptions.ConnectionError:
            print("❌ Connection error")
            return None
        except Exception as e:
            print(f"❌ Error: {e}")
            return None
    
    def parse_weather_data(self, data, city):
        """Extract relevant information from API response"""
        try:
            current = data['current_condition'][0]
            
            weather_record = {
                'city': city,
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
        """Save weather data to database"""
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO weather_data 
                (city, date, temp_c, feels_like_c, condition, humidity, 
                 wind_speed_kmph, pressure_mb, visibility_km, uv_index, timestamp)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                weather_record['city'],
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
            print(f"✓ Weather data saved for {weather_record['city']}")
            return True
            
        except sqlite3.IntegrityError:
            print(f"⚠️  Data already exists for {weather_record['city']} at this time")
            return False
        except Exception as e:
            print(f"❌ Error saving data: {e}")
            return False
        finally:
            conn.close()
    
    def collect_and_store(self, city):
        """Complete pipeline: fetch, parse, and store weather data"""
        print("\n" + "=" * 70)
        print(f"COLLECTING WEATHER DATA FOR {city.upper()}")
        print("=" * 70)
        
        # Step 1: Fetch
        data = self.fetch_weather(city)
        if not data:
            return False
        
        # Step 2: Parse
        weather_record = self.parse_weather_data(data, city)
        if not weather_record:
            return False
        
        # Step 3: Store
        success = self.save_weather_data(weather_record)
        
        # Step 4: Display
        if success:
            print("\nCollected data:")
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
        
        cursor.execute("SELECT * FROM weather_data ORDER BY timestamp DESC")
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


# ===== TEST THE COLLECTOR =====

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("WEATHER DATA COLLECTOR - TEST")
    print("=" * 70)
    
    # Create collector
    collector = WeatherCollector()
    
    # Collect data for multiple cities
    cities = ['Athens', 'London', 'Paris', 'NewYork', 'Tokyo']
    
    for city in cities:
        collector.collect_and_store(city)
        time.sleep(2)  # Be nice to the API - wait 2 seconds between requests
    
    # Show summary
    print("\n" + "=" * 70)
    print("COLLECTION SUMMARY")
    print("=" * 70)
    print(f"Total weather records collected: {collector.get_weather_count()}")
    
    # Show all collected data
    print("\nAll collected weather data:")
    print("-" * 70)
    
    data = collector.get_all_weather_data()
    for row in data[:10]:  # Show first 10
        print(f"  {row[1]} on {row[2]}: {row[3]}°C - {row[5]}")
    
    print("\n" + "=" * 70)
    print("TEST COMPLETE!")
    print("=" * 70)

