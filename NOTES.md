# Week 4 - Day 1: APIs and Data Fetching

### APIs
- **API**: Application Programming Interface - a way for programs to talk to each other
- **REST API**: Most common type, uses HTTP requests (GET, POST, PUT, DELETE)
- **JSON**: JavaScript Object Notation - format for data exchange

### HTTP Status Codes
- 200: Success
- 404: Not found
- 500: Server error
- Timeout: Request took too long

### Python Requests Library
```python
import requests

# Basic GET request
response = requests.get(url)

# Check status
if response.status_code == 200:
    data = response.json()  # Parse JSON

# With parameters
response = requests.get(url, params={'key': 'value'})

# With timeout
response = requests.get(url, timeout=10)

### ETL Pipeline  
1. Extract: Fetch data from source (API)  
2. Transform: Clean and structure the data  
3. Load: Save to database

### Key Concepts  
- Always handle errors (try/except)  
- Check status codes  
- Be respectful to APIs (don’t spam requests)  
- Parse JSON responses carefully