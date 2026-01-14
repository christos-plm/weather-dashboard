# explore_api.py - Template for exploring any API
import requests
import json

def explore_api(url):
    """Explore an API's response structure"""
    print("=" * 70)
    print(f"EXPLORING API: {url}")
    print("=" * 70)
    
    # Fetch data
    try:
        response = requests.get(url, timeout=10)
        
        if response.status_code != 200:
            print(f"Error: Status {response.status_code}")
            return
        
        data = response.json()
        
        # Show full response (first 2000 chars)
        print("\n1. RAW RESPONSE (preview):")
        print("-" * 70)
        json_str = json.dumps(data, indent=2)
        print(json_str[:2000])
        if len(json_str) > 2000:
            print("\n... (truncated)")
        
        # Show structure
        print("\n2. STRUCTURE ANALYSIS:")
        print("-" * 70)
        print(f"Type: {type(data)}")
        
        if isinstance(data, dict):
            print(f"Keys: {list(data.keys())}")
            print("\nExploring each key:")
            for key in list(data.keys())[:5]:  # First 5 keys
                print(f"\n  {key}:")
                print(f"    Type: {type(data[key])}")
                if isinstance(data[key], list) and len(data[key]) > 0:
                    print(f"    Length: {len(data[key])}")
                    print(f"    First item type: {type(data[key][0])}")
                elif isinstance(data[key], dict):
                    print(f"    Keys: {list(data[key].keys())[:5]}")
        
        elif isinstance(data, list):
            print(f"List length: {len(data)}")
            if len(data) > 0:
                print(f"First item type: {type(data[0])}")
                if isinstance(data[0], dict):
                    print(f"First item keys: {list(data[0].keys())}")
        
        # Save to file
        filename = 'api_response_sample.json'
        with open(filename, 'w') as f:
            json.dump(data, f, indent=2)
        print(f"\n3. Full response saved to: {filename}")
        
        return data
        
    except Exception as e:
        print(f"Error: {e}")
        return None


# Test with different APIs
if __name__ == "__main__":
    
    # Example 1: Weather API
    print("\n\nEXAMPLE 1: Weather API")
    explore_api("https://wttr.in/Athens?format=j1")
    
    print("\n\n")
    input("Press Enter to try another API...")
    
    # Example 2: Simple test API
    print("\n\nEXAMPLE 2: Test API (JSONPlaceholder)")
    explore_api("https://jsonplaceholder.typicode.com/users/1")
    
    print("\n\n")
    input("Press Enter to try another API...")
    
    # Example 3: GitHub API (public, no auth needed)
    print("\n\nEXAMPLE 3: GitHub API")
    explore_api("https://api.github.com/users/torvalds")
