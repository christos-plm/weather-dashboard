# 🌤️ Weather Analytics Dashboard

A full-stack data application that collects, analyzes, and visualizes weather data from multiple cities worldwide.

![Dashboard Screenshot](screenshot.png)

## 🎯 Project Overview

This project demonstrates end-to-end data engineering and analysis skills:
- **Data Engineering**: API integration, ETL pipelines, data validation
- **Data Analysis**: Statistical analysis, trend detection, data quality checks
- **Data Visualization**: Interactive charts and dashboards
- **Web Development**: Full-featured web application with Flask

## ✨ Features

### Data Collection
- ✅ Fetch real-time weather data from API
- ✅ Support for multiple cities worldwide
- ✅ Add new cities through web interface
- ✅ Refresh data on demand

### Data Processing
- ✅ Complete ETL pipeline (Extract, Transform, Load)
- ✅ Data validation and quality checks
- ✅ Duplicate detection
- ✅ Derived field calculation
- ✅ Data cleaning and standardization

### Visualizations
- ✅ Temperature comparison bar charts
- ✅ Trend analysis line charts
- ✅ Humidity vs temperature scatter plots
- ✅ Multi-metric dashboards
- ✅ Interactive Plotly charts

### Web Dashboard
- ✅ Real-time weather overview
- ✅ City management interface
- ✅ Data table views
- ✅ Embedded visualizations
- ✅ Statistics and analytics
- ✅ RESTful API endpoint
- ✅ Auto-refresh capability

## 🛠️ Technology Stack

**Backend & Data Processing:**
- Python 3.9+
- Flask (Web Framework)
- Pandas (Data Analysis)
- SQLite (Database)
- Requests (API Integration)

**Visualization:**
- Plotly (Interactive Charts)

**Data Pipeline:**
- Custom ETL framework
- Data validation engine
- Quality monitoring

## 📊 Architecture

┌─────────────┐  
│   Weather   │  
│     API     │  
└──────┬──────┘  
│  
▼  
┌─────────────┐  
│     ETL     │  
│  Pipeline   │  
└──────┬──────┘  
│  
▼  
┌─────────────┐  
│   SQLite    │  
│  Database   │  
└──────┬──────┘  
│  
▼  
┌─────────────┐  
│   Pandas    │  
│  Analysis   │  
└──────┬──────┘  
│  
▼  
┌─────────────┐  
│    Flask    │  
│  Web App    │  
└─────────────┘  

## 🚀 Getting Started

### Prerequisites
```bash
Python 3.9 or higher
pip (Python package manager)
```

### Installation  
1. Clone the repository:  
```bash
git clone https://github.com/christos-plm/weather-dashboard.git  
cd weather-dashboard  
```
2. Install dependencies:  
```bash
pip install flask pandas plotly requests  
```
3. Collect initial weather data:  
```bash
python3 etl_pipeline.py 
``` 
4. Run the web application:  
```bash
python3 app.py  
```
5. Open your browser:  
http://127.0.0.1:5000  

## 📖 Usage
**Viewing the Dashboard**
### Navigate to http://127.0.0.1:5000 to see:
- Current weather for all tracked cities
- Temperature trends
- Statistics and analytics
### Adding New Cities
1. Go to “Manage Cities” page
2. Enter city name and country
3. Click “Add City & Fetch Data”
4. Data is automatically collected and stored
### Refreshing Data
- Single city: Click refresh button next to the city
- All cities: Click “Refresh All Cities” button
- Automatic: Home page auto-refreshes every 5 minutes
### Viewing Visualizations
### Navigate to the “Visualizations” page for:
- Interactive temperature charts
- Humidity analysis
- Wind speed comparisons
- Multi-metric dashboards
    
## 📁 Project Structure  
weather-dashboard/
├── app.py                    # Flask web application
├── weather_collector.py      # API data collection
├── data_transformer.py       # Data validation & cleaning
├── etl_pipeline.py          # Complete ETL pipeline
├── visualizer.py            # Plotly visualizations
├── weather.db               # SQLite database
├── README.md                # This file
└── LEARNING_NOTES.md        # Development notes

## 🔄 Data Pipeline Flow
1. Extract: Fetch data from wttr.in API
2. Transform:
    ∙ Parse JSON response
    ∙ Validate data ranges
    ∙ Clean and standardize
    ∙ Calculate derived fields
    ∙ Check for duplicates
3. Load: Save to SQLite database
4. Analyze: Process with Pandas
5. Visualize: Display with Plotly
6. Present: Serve via Flask web app
    
## 📈 Future Enhancements
∙ Historical data analysis
∙ Weather predictions
∙ Email alerts for extreme weather
∙ Mobile-responsive design
∙ User authentication
∙ Data export
∙ More visualization types
∙ API rate limiting
∙ Caching layer
∙ Deploy to cloud

## This project is open source and available for educational purposes.

## 🙏 Acknowledgments
Weather data provided by wttr.in
