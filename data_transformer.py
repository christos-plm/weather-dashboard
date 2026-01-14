# data_transformer.py - Data transformation and quality checks
import pandas as pd
import sqlite3
from datetime import datetime, timedelta
import numpy as np

class WeatherDataTransformer:
    """
    Handles data transformation, validation, and quality checks
    for weather data
    """
    
    def __init__(self, db_name='weather.db'):
        self.db_name = db_name
    
    def validate_temperature(self, temp_c):
        """
        Validate temperature is within reasonable range
        Extreme recorded temps: -89°C to +57°C
        """
        if temp_c is None:
            return False, "Temperature is missing"
        
        if temp_c < -90 or temp_c > 60:
            return False, f"Temperature {temp_c}°C is outside reasonable range"
        
        return True, "Valid"
    
    def validate_humidity(self, humidity):
        """Validate humidity is between 0-100%"""
        if humidity is None:
            return False, "Humidity is missing"
        
        if humidity < 0 or humidity > 100:
            return False, f"Humidity {humidity}% is invalid"
        
        return True, "Valid"
    
    def validate_wind_speed(self, wind_kmph):
        """
        Validate wind speed is reasonable
        Strongest recorded: ~408 km/h (tropical cyclone)
        """
        if wind_kmph is None:
            return False, "Wind speed is missing"
        
        if wind_kmph < 0 or wind_kmph > 500:
            return False, f"Wind speed {wind_kmph} km/h seems invalid"
        
        return True, "Valid"
    
    def validate_weather_record(self, record):
        """
        Validate entire weather record
        Returns: (is_valid, list_of_issues)
        """
        issues = []
        
        # Check required fields exist
        required_fields = ['city', 'country', 'temp_c', 'humidity', 'condition']
        for field in required_fields:
            if field not in record or record[field] is None:
                issues.append(f"Missing required field: {field}")
        
        # If basic fields are missing, return early
        if issues:
            return False, issues
        
        # Validate temperature
        valid, msg = self.validate_temperature(record.get('temp_c'))
        if not valid:
            issues.append(msg)
        
        # Validate humidity
        valid, msg = self.validate_humidity(record.get('humidity'))
        if not valid:
            issues.append(msg)
        
        # Validate wind speed
        valid, msg = self.validate_wind_speed(record.get('wind_speed_kmph'))
        if not valid:
            issues.append(msg)
        
        # Check if feels_like is too different from actual temp
        if 'feels_like_c' in record and 'temp_c' in record:
            diff = abs(record['feels_like_c'] - record['temp_c'])
            if diff > 30:  # More than 30°C difference seems extreme
                issues.append(f"Feels like temperature differs by {diff}°C from actual")
        
        is_valid = len(issues) == 0
        return is_valid, issues
    
    def clean_weather_record(self, record):
        """
        Clean and standardize a weather record
        Returns cleaned record
        """
        cleaned = record.copy()
        
        # Standardize city and country names (title case)
        if 'city' in cleaned and cleaned['city']:
            cleaned['city'] = cleaned['city'].strip().title()
        
        if 'country' in cleaned and cleaned['country']:
            cleaned['country'] = cleaned['country'].strip()
        
        # Round numerical values to reasonable precision
        if 'temp_c' in cleaned and cleaned['temp_c'] is not None:
            cleaned['temp_c'] = round(float(cleaned['temp_c']), 1)
        
        if 'feels_like_c' in cleaned and cleaned['feels_like_c'] is not None:
            cleaned['feels_like_c'] = round(float(cleaned['feels_like_c']), 1)
        
        if 'wind_speed_kmph' in cleaned and cleaned['wind_speed_kmph'] is not None:
            cleaned['wind_speed_kmph'] = round(float(cleaned['wind_speed_kmph']), 1)
        
        # Ensure integers are actually integers
        if 'humidity' in cleaned and cleaned['humidity'] is not None:
            cleaned['humidity'] = int(cleaned['humidity'])
        
        if 'uv_index' in cleaned and cleaned['uv_index'] is not None:
            cleaned['uv_index'] = int(cleaned['uv_index'])
        
        # Standardize condition text
        if 'condition' in cleaned and cleaned['condition']:
            cleaned['condition'] = cleaned['condition'].strip().title()
        
        return cleaned
    
    def calculate_derived_fields(self, record):
        """
        Calculate additional fields from existing data
        """
        derived = record.copy()
        
        # Add heat index category
        if 'temp_c' in record:
            temp = record['temp_c']
            if temp >= 35:
                derived['heat_category'] = 'Extreme Heat'
            elif temp >= 30:
                derived['heat_category'] = 'Hot'
            elif temp >= 20:
                derived['heat_category'] = 'Warm'
            elif temp >= 10:
                derived['heat_category'] = 'Mild'
            elif temp >= 0:
                derived['heat_category'] = 'Cool'
            else:
                derived['heat_category'] = 'Cold'
        
        # Add comfort index (combines temp and humidity)
        if 'temp_c' in record and 'humidity' in record:
            temp = record['temp_c']
            humidity = record['humidity']
            
            # Simple comfort calculation
            if temp >= 20 and temp <= 26 and humidity >= 30 and humidity <= 60:
                derived['comfort_level'] = 'Comfortable'
            elif temp > 30 or humidity > 70:
                derived['comfort_level'] = 'Uncomfortable'
            elif temp < 10:
                derived['comfort_level'] = 'Cold'
            else:
                derived['comfort_level'] = 'Moderate'
        
        # Categorize wind
        if 'wind_speed_kmph' in record:
            wind = record['wind_speed_kmph']
            if wind < 12:
                derived['wind_category'] = 'Calm'
            elif wind < 30:
                derived['wind_category'] = 'Breezy'
            elif wind < 50:
                derived['wind_category'] = 'Windy'
            else:
                derived['wind_category'] = 'Very Windy'
        
        return derived
    
    def check_for_duplicate(self, record):
        """
        Check if this record already exists in database
        Returns: (is_duplicate, existing_id)
        """
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        
        # Check for exact match on city, country, and date
        cursor.execute("""
            SELECT id FROM weather_data 
            WHERE city = ? 
            AND country = ? 
            AND date = ?
            AND ABS(strftime('%s', timestamp) - strftime('%s', ?)) < 3600
        """, (
            record['city'],
            record['country'],
            record['date'],
            record['timestamp']
        ))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            return True, result[0]
        return False, None
    
    def load_data_to_pandas(self):
        """
        Load weather data into pandas DataFrame for analysis
        """
        conn = sqlite3.connect(self.db_name)
        
        query = """
            SELECT * FROM weather_data 
            ORDER BY timestamp DESC
        """
        
        df = pd.read_sql_query(query, conn)
        conn.close()
        
        # Convert date and timestamp to datetime
        if not df.empty:
            df['date'] = pd.to_datetime(df['date'])
            df['timestamp'] = pd.to_datetime(df['timestamp'])
        
        return df
    
    def get_data_quality_report(self):
        """
        Generate a data quality report
        """
        df = self.load_data_to_pandas()
        
        if df.empty:
            return "No data available for quality report"
        
        report = []
        report.append("=" * 70)
        report.append("DATA QUALITY REPORT")
        report.append("=" * 70)
        
        # Basic stats
        report.append(f"\nTotal records: {len(df)}")
        report.append(f"Date range: {df['date'].min()} to {df['date'].max()}")
        report.append(f"Cities tracked: {df['city'].nunique()}")
        report.append(f"Countries: {df['country'].nunique()}")
        
        # Missing values
        report.append("\nMissing Values:")
        missing = df.isnull().sum()
        missing = missing[missing > 0]
        if len(missing) == 0:
            report.append("  ✓ No missing values")
        else:
            for col, count in missing.items():
                pct = (count / len(df)) * 100
                report.append(f"  - {col}: {count} ({pct:.1f}%)")
        
        # Temperature stats
        report.append("\nTemperature Statistics:")
        report.append(f"  Mean: {df['temp_c'].mean():.1f}°C")
        report.append(f"  Min: {df['temp_c'].min():.1f}°C")
        report.append(f"  Max: {df['temp_c'].max():.1f}°C")
        report.append(f"  Std Dev: {df['temp_c'].std():.1f}°C")
        
        # Check for outliers (temperatures outside 3 std devs)
        mean_temp = df['temp_c'].mean()
        std_temp = df['temp_c'].std()
        outliers = df[(df['temp_c'] < mean_temp - 3*std_temp) |
                     (df['temp_c'] > mean_temp + 3*std_temp)]
        
        if len(outliers) > 0:
            report.append(f"\n⚠️  Temperature outliers detected: {len(outliers)}")
        else:
            report.append("\n✓ No temperature outliers")
        
        # Duplicate check
        duplicates = df.duplicated(subset=['city', 'country', 'date'], keep=False)
        dup_count = duplicates.sum()
        
        if dup_count > 0:
            report.append(f"\n⚠️  Potential duplicates: {dup_count} records")
        else:
            report.append("\n✓ No duplicates detected")
        
        # Data freshness
        latest = df['timestamp'].max()
        age = datetime.now() - latest
        report.append(f"\nData Freshness:")
        report.append(f"  Latest update: {latest}")
        report.append(f"  Age: {age}")
        
        if age > timedelta(hours=24):
            report.append("  ⚠️  Data is more than 24 hours old")
        else:
            report.append("  ✓ Data is fresh")
        
        report.append("\n" + "=" * 70)
        
        return "\n".join(report)
    
    def get_summary_statistics(self):
        """
        Get summary statistics by city
        """
        df = self.load_data_to_pandas()
        
        if df.empty:
            return None
        
        summary = df.groupby(['city', 'country']).agg({
            'temp_c': ['mean', 'min', 'max', 'std'],
            'humidity': 'mean',
            'wind_speed_kmph': 'mean',
            'id': 'count'
        }).round(2)
        
        summary.columns = ['Avg Temp', 'Min Temp', 'Max Temp', 'Temp StdDev',
                          'Avg Humidity', 'Avg Wind', 'Record Count']
        
        return summary


# ===== TEST THE TRANSFORMER =====

if __name__ == "__main__":
    print("=" * 70)
    print("WEATHER DATA TRANSFORMER - TESTING")
    print("=" * 70)
    
    transformer = WeatherDataTransformer()
    
    # Test 1: Validate good record
    print("\n1. TESTING VALIDATION - Good Record:")
    print("-" * 70)
    good_record = {
        'city': 'Athens',
        'country': 'Greece',
        'temp_c': 25.5,
        'feels_like_c': 27.0,
        'humidity': 65,
        'wind_speed_kmph': 15.0,
        'condition': 'Partly Cloudy'
    }
    
    valid, issues = transformer.validate_weather_record(good_record)
    print(f"Valid: {valid}")
    if issues:
        for issue in issues:
            print(f"  - {issue}")
    else:
        print("  ✓ No issues found")
    
    # Test 2: Validate bad record
    print("\n2. TESTING VALIDATION - Bad Record:")
    print("-" * 70)
    bad_record = {
        'city': 'Test City',
        'country': 'Test',
        'temp_c': 150,  # Invalid!
        'humidity': 200,  # Invalid!
        'wind_speed_kmph': -10  # Invalid!
    }
    
    valid, issues = transformer.validate_weather_record(bad_record)
    print(f"Valid: {valid}")
    if issues:
        print("Issues found:")
        for issue in issues:
            print(f"  - {issue}")
    
    # Test 3: Clean data
    print("\n3. TESTING DATA CLEANING:")
    print("-" * 70)
    dirty_record = {
        'city': '  athens  ',
        'country': 'GREECE',
        'temp_c': 25.567891,
        'humidity': 65.7,
        'condition': '  partly cloudy  '
    }
    
    print("Before cleaning:")
    print(f"  City: '{dirty_record['city']}'")
    print(f"  Temp: {dirty_record['temp_c']}")
    
    cleaned = transformer.clean_weather_record(dirty_record)
    print("\nAfter cleaning:")
    print(f"  City: '{cleaned['city']}'")
    print(f"  Temp: {cleaned['temp_c']}")
    print(f"  Condition: '{cleaned['condition']}'")
    
    # Test 4: Calculate derived fields
    print("\n4. TESTING DERIVED FIELDS:")
    print("-" * 70)
    record = {
        'temp_c': 32,
        'humidity': 75,
        'wind_speed_kmph': 25
    }
    
    derived = transformer.calculate_derived_fields(record)
    print(f"Temperature: {record['temp_c']}°C")
    print(f"Heat Category: {derived.get('heat_category')}")
    print(f"Comfort Level: {derived.get('comfort_level')}")
    print(f"Wind Category: {derived.get('wind_category')}")
    
    # Test 5: Data quality report
    print("\n5. DATA QUALITY REPORT:")
    print("-" * 70)
    report = transformer.get_data_quality_report()
    print(report)
    
    # Test 6: Summary statistics
    print("\n6. SUMMARY STATISTICS BY CITY:")
    print("-" * 70)
    summary = transformer.get_summary_statistics()
    if summary is not None:
        print(summary)
    else:
        print("No data available for statistics")
    
    print("\n" + "=" * 70)
    print("TESTING COMPLETE!")
    print("=" * 70)

