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

---

# Week 4 - Day 2: Data Transformation & ETL Pipeline

### What is ETL?
- **Extract**: Get data from source (API, database, file)
- **Transform**: Clean, validate, enrich the data
- **Load**: Save to destination (database, file, data warehouse)

### Data Quality Checks
- Validation (is data reasonable?)
- Completeness (any missing fields?)
- Consistency (proper formats?)
- Duplicates (already exists?)
- Outliers (unusual values?)

### Transformation Techniques
1. **Cleaning**
   - Trim whitespace
   - Standardize case
   - Round numbers
   - Format dates

2. **Validation**
   - Range checks (temp between -90 and 60)
   - Required fields present
   - Type checking

3. **Enrichment**
   - Calculate derived fields
   - Add categories
   - Compute aggregates

### Best Practices
- Always validate before loading
- Log everything
- Handle errors gracefully
- Check for duplicates
- Generate quality reports
- Track statistics

### What I Built
- Data validation functions
- Data cleaning pipeline
- Quality reporting system
- Complete ETL pipeline
- Batch processing capability

## Key Takeaways
(Write your own thoughts)
