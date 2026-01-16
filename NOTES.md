# APIs and Data Fetching

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

# Data Transformation & ETL Pipeline

### What is ETL
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

### Built
- Data validation functions
- Data cleaning pipeline
- Quality reporting system
- Complete ETL pipeline
- Batch processing capability

---

## Data Visualization

### Why Visualize
- Spot patterns instantly
- Compare values easily  
- Communicate insights
- Find outliers
- Tell data stories

### Types of Charts

**Bar Charts**
- Compare categories
- Show rankings
- Good for: comparing cities, categories

**Line Charts**
- Show trends over time
- Multiple lines = multiple series
- Good for: temperature trends, time series

**Scatter Plots**
- Show relationships between 2 variables
- Bubble size can show 3rd variable
- Good for: humidity vs temp, correlations

**Pie/Donut Charts**
- Show parts of a whole
- Good for: condition distribution, percentages

**Heatmaps**
- Show patterns in 2D data
- Color intensity = values
- Good for: time patterns, correlations

**Box Plots**
- Show distribution and outliers
- Good for: comparing ranges across categories

**Radar Charts**
- Compare multiple metrics at once
- Good for: multi-dimensional comparisons

### Plotly Features
- Interactive (hover, zoom, pan)
- Opens in browser
- Professional looking
- Easy to customize
- Can export as images

### Best Practices
- Choose the right chart type
- Label axes clearly
- Use appropriate colors
- Keep it simple
- Tell a story

### Built
- 10 different visualization types
- Interactive dashboards
- Custom comfort score metric
- Multi-panel layouts

---

## Flask Web Development

### What is Flask
- Python web framework
- Makes building web apps easy
- Routes map URLs to Python functions
- Returns HTML to the browser

### Key Concepts

**Routes**
```python
@app.route('/path')
def function_name():
    return "HTML content"

**Running the server**
'''python
app.run(debug=True, port=5000)

### Dynamic content  
- Load data from database  
- Generate HTML with Python  
- Insert data into pages  

### Embedding visualizations  
- Plotly’s to_html() method  
- Include charts in web pages  
- Interactive in the browser  

### What I Built  
- Complete web application  
- Multiple pages with navigation  
- Data table display  
- Embedded visualizations  
- API endpoint  
- Responsive styling  

### Web Development Basics  
- HTML structure  
- CSS styling  
- Navigation menu  
- Page layout  

### Next Steps  
- Add templates (cleaner HTML)  
- Add more features  
- Deploy online  

## Project Completion

### New Features Added
- City management interface
- Add new cities through web UI
- Refresh individual cities
- Refresh all cities at once
- Statistics page
- Auto-refresh on home page
- Loading states
- Better error handling

### Final Project Features
✅ Data collection from API
✅ Complete ETL pipeline
✅ Data validation & quality checks
✅ Data transformation
✅ Database storage
✅ Data analysis with Pandas
✅ Interactive visualizations
✅ Web application
✅ City management
✅ Statistics dashboard
✅ RESTful API
✅ Auto-refresh capability

### Skills Gained
- API integration
- ETL pipeline development
- Data validation
- Data transformation
- Flask web development
- Interactive visualizations
- Form handling
- Database operations
- Full-stack development

### Project Statistics
- Lines of code: ~1500+
- Files created: 7
- Technologies: 5+
- Features: 15+
- Days: 5
