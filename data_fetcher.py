# data_fetcher.py - Fetching data from APIs
import requests
import json
from datetime import datetime

print("=" * 70)
print("APIs - FETCHING DATA FROM THE INTERNET")
print("=" * 70)

# ===== EXAMPLE 1: Simple API Request =====
print("\n1. MAKING A SIMPLE API REQUEST:")
print("-" * 70)

# This is a test API that returns dummy data
url = "https://jsonplaceholder.typicode.com/users/1"

print(f"Requesting data from: {url}")

# Make the request
response = requests.get(url)

print(f"Status code: {response.status_code}")  # 200 means success
print(f"Response type: {type(response.json())}")

# Parse JSON response
data = response.json()
print("\nData received:")
print(json.dumps(data, indent=2))  # Pretty print

# ===== EXAMPLE 2: Accessing Data from Response =====
print("\n2. EXTRACTING SPECIFIC INFORMATION:")
print("-" * 70)

print(f"User name: {data['name']}")
print(f"User email: {data['email']}")
print(f"City: {data['address']['city']}")

# ===== EXAMPLE 3: Getting Multiple Items =====
print("\n3. FETCHING MULTIPLE RECORDS:")
print("-" * 70)

url = "https://jsonplaceholder.typicode.com/posts"
response = requests.get(url)

posts = response.json()
print(f"Total posts received: {len(posts)}")

# Show first 3 posts
print("\nFirst 3 posts:")
for post in posts[:3]:
    print(f"  - {post['title'][:50]}...")  # Show first 50 chars of title

# ===== EXAMPLE 4: API with Parameters =====
print("\n4. USING QUERY PARAMETERS:")
print("-" * 70)

# Request only posts from a specific user
url = "https://jsonplaceholder.typicode.com/posts"
params = {
    'userId': 1
}

response = requests.get(url, params=params)
user_posts = response.json()

print(f"Posts by user 1: {len(user_posts)}")

# ===== EXAMPLE 5: Real Weather API =====
print("\n5. FETCHING REAL WEATHER DATA:")
print("-" * 70)

# Using wttr.in - a simple weather API (no API key needed!)
city = "Athens"
url = f"https://wttr.in/{city}?format=j1"

print(f"Getting weather for {city}...")

try:
    response = requests.get(url)
    
    if response.status_code == 200:
        weather_data = response.json()
        
        # Extract current conditions
        current = weather_data['current_condition'][0]
        
        print(f"\nCurrent weather in {city}:")
        print(f"  Temperature: {current['temp_C']}°C")
        print(f"  Feels like: {current['FeelsLikeC']}°C")
        print(f"  Condition: {current['weatherDesc'][0]['value']}")
        print(f"  Humidity: {current['humidity']}%")
        print(f"  Wind: {current['windspeedKmph']} km/h")
        
        # Show forecast for next 3 days
        print(f"\n3-Day Forecast for {city}:")
        for day in weather_data['weather'][:3]:
            date = day['date']
            max_temp = day['maxtempC']
            min_temp = day['mintempC']
            desc = day['hourly'][0]['weatherDesc'][0]['value']
            print(f"  {date}: {min_temp}°C - {max_temp}°C, {desc}")
    
    else:
        print(f"Error: Status code {response.status_code}")
        
except Exception as e:
    print(f"Error occurred: {e}")

# ===== EXAMPLE 6: Error Handling =====
print("\n6. HANDLING API ERRORS:")
print("-" * 70)

# Try to access a URL that doesn't exist
bad_url = "https://jsonplaceholder.typicode.com/invalid"

try:
    response = requests.get(bad_url, timeout=5)
    
    if response.status_code == 200:
        print("Success!")
    elif response.status_code == 404:
        print("❌ Error 404: Resource not found")
    else:
        print(f"❌ Error {response.status_code}")
        
except requests.exceptions.Timeout:
    print("❌ Request timed out")
except requests.exceptions.ConnectionError:
    print("❌ Connection error - check internet")
except Exception as e:
    print(f"❌ Unexpected error: {e}")

print("\n" + "=" * 70)
print("API EXAMPLES COMPLETE")
print("=" * 70)

