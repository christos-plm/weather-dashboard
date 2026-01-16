# app.py - Weather Dashboard Web Application
from flask import Flask, render_template, jsonify, request, redirect, url_for
import sqlite3
import pandas as pd
from datetime import datetime
from weather_collector import WeatherCollector
from data_transformer import WeatherDataTransformer
from etl_pipeline import WeatherETLPipeline
import time

# Create Flask app
app = Flask(__name__)

# ===== HELPER FUNCTIONS =====

def get_db_connection():
    """Create database connection"""
    conn = sqlite3.connect('weather.db')
    conn.row_factory = sqlite3.Row  # Return rows as dictionaries
    return conn

def load_weather_data():
    """Load all weather data"""
    conn = get_db_connection()
    df = pd.read_sql_query("SELECT * FROM weather_data ORDER BY timestamp DESC", conn)
    conn.close()
    
    if not df.empty:
        df['date'] = pd.to_datetime(df['date'])
        df['timestamp'] = pd.to_datetime(df['timestamp'])
        df['location'] = df['city'] + ', ' + df['country']
    
    return df

# ===== ROUTES =====

@app.route('/')
def home():
    """Home page - Dashboard overview"""
    df = load_weather_data()
    
    if df.empty:
        return """
        <h1>Weather Dashboard</h1>
        <p>No data available. Run etl_pipeline.py to collect weather data.</p>
        """
    
    # Get statistics
    total_records = len(df)
    cities_count = df['location'].nunique()
    latest_update = df['timestamp'].max().strftime('%Y-%m-%d %H:%M:%S')
    
    # Get latest data for each city
    latest_by_city = df.sort_values('timestamp').groupby('location').last()
    
    # Create HTML
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Weather Dashboard</title>
        <meta http-equiv="refresh" content="300">  <!-- Auto-refresh every 5 minutes -->
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            h1 {{
                color: #2c3e50;
                border-bottom: 3px solid #3498db;
                padding-bottom: 10px;
            }}
            .stats {{
                display: flex;
                justify-content: space-around;
                margin: 20px 0;
            }}
            .stat-box {{
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                text-align: center;
                flex: 1;
                margin: 0 10px;
            }}
            .stat-number {{
                font-size: 36px;
                font-weight: bold;
                color: #3498db;
            }}
            .stat-label {{
                color: #7f8c8d;
                margin-top: 5px;
            }}
            .weather-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin-top: 30px;
            }}
            .weather-card {{
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }}
            .city-name {{
                font-size: 20px;
                font-weight: bold;
                color: #2c3e50;
                margin-bottom: 10px;
            }}
            .temperature {{
                font-size: 48px;
                font-weight: bold;
                color: #e74c3c;
                margin: 10px 0;
            }}
            .condition {{
                color: #7f8c8d;
                font-style: italic;
            }}
            .details {{
                margin-top: 15px;
                font-size: 14px;
                color: #34495e;
            }}
            .details div {{
                margin: 5px 0;
            }}
            nav {{
                background: #34495e;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 20px;
            }}
            nav a {{
                color: white;
                text-decoration: none;
                margin: 0 15px;
                font-weight: bold;
            }}
            nav a:hover {{
                color: #3498db;
            }}
        </style>
    </head>
    <body>
        <nav>
            <a href="/">Home</a>
            <a href="/data">Data Table</a>
            <a href="/visualizations">Visualizations</a>
            <a href="/manage">Manage Cities</a>
            <a href="/stats">Statistics</a>
            <a href="/about">About</a>
        </nav>
        
        <h1>🌤️ Weather Dashboard</h1>
        
        <div class="stats">
            <div class="stat-box">
                <div class="stat-number">{total_records}</div>
                <div class="stat-label">Total Records</div>
            </div>
            <div class="stat-box">
                <div class="stat-number">{cities_count}</div>
                <div class="stat-label">Cities Tracked</div>
            </div>
            <div class="stat-box">
                <div class="stat-label">Last Updated</div>
                <div style="font-size: 16px; color: #2c3e50; margin-top: 5px;">{latest_update}</div>
                <div style="color: #7f8c8d";><small>🕐 Auto-refreshes every 5 minutes</small></div>
            </div>
        </div>
        
        <h2>Current Weather</h2>
        <div class="weather-grid">
    """
    
    # Add weather cards for each city
    for location, row in latest_by_city.iterrows():
        html += f"""
            <div class="weather-card">
                <div class="city-name">{location}</div>
                <div class="temperature">{row['temp_c']:.1f}°C</div>
                <div class="condition">{row['condition']}</div>
                <div class="details">
                    <div>💧 Humidity: {row['humidity']}%</div>
                    <div>💨 Wind: {row['wind_speed_kmph']:.1f} km/h</div>
                    <div>🌡️ Feels like: {row['feels_like_c']:.1f}°C</div>
                    <div>📊 Pressure: {row['pressure_mb']:.0f} mb</div>
                </div>
            </div>
        """
    
    html += """
        </div>
    </body>
    </html>
    """
    
    return html


@app.route('/data')
def data_table():
    """Data table page - Show all weather records"""
    df = load_weather_data()
    
    if df.empty:
        return "<h1>No data available</h1>"
    
    # Create HTML table
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Weather Data Table</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 1400px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            h1 {
                color: #2c3e50;
            }
            nav {
                background: #34495e;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 20px;
            }
            nav a {
                color: white;
                text-decoration: none;
                margin: 0 15px;
                font-weight: bold;
            }
            nav a:hover {
                color: #3498db;
            }
            table {
                width: 100%;
                background: white;
                border-collapse: collapse;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                border-radius: 8px;
                overflow: hidden;
            }
            th {
                background: #34495e;
                color: white;
                padding: 12px;
                text-align: left;
            }
            td {
                padding: 10px;
                border-bottom: 1px solid #ecf0f1;
            }
            tr:hover {
                background: #f8f9fa;
            }
        </style>
    </head>
    <body>
        <nav>
            <a href="/">Home</a>
            <a href="/data">Data Table</a>
            <a href="/visualizations">Visualizations</a>
            <a href="/manage">Manage Cities</a>
            <a href="/stats">Statistics</a>
            <a href="/about">About</a>
        </nav>
        
        <h1>📊 Weather Data Table</h1>
        <p>Total records: """ + str(len(df)) + """</p>
        
        <table>
            <thead>
                <tr>
                    <th>City</th>
                    <th>Country</th>
                    <th>Date</th>
                    <th>Temp (°C)</th>
                    <th>Feels Like</th>
                    <th>Condition</th>
                    <th>Humidity</th>
                    <th>Wind (km/h)</th>
                </tr>
            </thead>
            <tbody>
    """
    
    # Add data rows
    for _, row in df.head(50).iterrows():  # Limit to 50 most recent
        html += f"""
                <tr>
                    <td>{row['city']}</td>
                    <td>{row['country']}</td>
                    <td>{row['date'].strftime('%Y-%m-%d')}</td>
                    <td>{row['temp_c']:.1f}°C</td>
                    <td>{row['feels_like_c']:.1f}°C</td>
                    <td>{row['condition']}</td>
                    <td>{row['humidity']}%</td>
                    <td>{row['wind_speed_kmph']:.1f}</td>
                </tr>
        """
    
    html += """
            </tbody>
        </table>
    </body>
    </html>
    """
    
    return html


@app.route('/about')
def about():
    """About page"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>About - Weather Dashboard</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 800px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            h1 {
                color: #2c3e50;
            }
            nav {
                background: #34495e;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 20px;
            }
            nav a {
                color: white;
                text-decoration: none;
                margin: 0 15px;
                font-weight: bold;
            }
            nav a:hover {
                color: #3498db;
            }
            .content {
                background: white;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                line-height: 1.6;
            }
            .tech-stack {
                background: #ecf0f1;
                padding: 15px;
                border-radius: 5px;
                margin: 20px 0;
            }
            .tech-stack ul {
                margin: 10px 0;
            }
        </style>
    </head>
    <body>
        <nav>
            <a href="/">Home</a>
            <a href="/data">Data Table</a>
            <a href="/visualizations">Visualizations</a>
            <a href="/manage">Manage Cities</a>
            <a href="/stats">Statistics</a>
            <a href="/about">About</a>
        </nav>
        
        <div class="content">
            <h1>ℹ️ About This Project</h1>
            
            <h2>Weather Analytics Dashboard</h2>
            <p>
                This is a full-stack data application that demonstrates:
            </p>
            <ul>
                <li><strong>Data Engineering:</strong> Fetching data from APIs, ETL pipelines</li>
                <li><strong>Data Analysis:</strong> Processing and analyzing weather data</li>
                <li><strong>Data Visualization:</strong> Creating interactive charts</li>
                <li><strong>Web Development:</strong> Building a web application</li>
            </ul>
            
            <div class="tech-stack">
                <h3>🛠️ Technology Stack</h3>
                <ul>
                    <li><strong>Backend:</strong> Python, Flask</li>
                    <li><strong>Data Processing:</strong> Pandas, NumPy</li>
                    <li><strong>Database:</strong> SQLite</li>
                    <li><strong>Visualization:</strong> Plotly</li>
                    <li><strong>API:</strong> wttr.in weather API</li>
                </ul>
            </div>
            
            <h2>Features</h2>
            <ul>
                <li>Real-time weather data collection</li>
                <li>Data validation and quality checks</li>
                <li>Multiple city tracking</li>
                <li>Interactive visualizations</li>
                <li>Web-based dashboard</li>
            </ul>
            
            <h2>Built By</h2>
            <p>
                This project was built for demonstration purposes.
            </p>
            
            <p style="text-align: center; margin-top: 40px; color: #7f8c8d;">
                <em>Weather Dashboard © 2026</em>
            </p>
        </div>
    </body>
    </html>
    """
    
    return html


@app.route('/api/weather')
def api_weather():
    """API endpoint - Return weather data as JSON"""
    df = load_weather_data()
    
    if df.empty:
        return jsonify({'error': 'No data available'})
    
    # Convert to JSON
    data = df.to_dict('records')
    
    # Convert timestamps to strings
    for record in data:
        record['date'] = str(record['date'])
        record['timestamp'] = str(record['timestamp'])
    
    return jsonify(data)
    
@app.route('/visualizations')
def visualizations():
    """Visualizations page - Embed Plotly charts"""
    import plotly.express as px
    import plotly.graph_objects as go
    from plotly.subplots import make_subplots
    
    df = load_weather_data()
    
    if df.empty:
        return "<h1>No data available for visualizations</h1>"
    
    # Get latest data for each city
    latest = df.sort_values('timestamp').groupby('location').last().reset_index()
    latest = latest.sort_values('temp_c', ascending=True)
    
    # Chart 1: Temperature Bar Chart
    fig1 = px.bar(
        latest,
        x='temp_c',
        y='location',
        orientation='h',
        title='Current Temperature by City',
        labels={'temp_c': 'Temperature (°C)', 'location': 'City'},
        color='temp_c',
        color_continuous_scale='RdYlBu_r',
        height=400
    )
    fig1_html = fig1.to_html(full_html=False, include_plotlyjs='cdn')
    
    # Chart 2: Temperature Trends
    fig2 = px.line(
        df,
        x='timestamp',
        y='temp_c',
        color='location',
        title='Temperature Trends Over Time',
        labels={'temp_c': 'Temperature (°C)', 'timestamp': 'Date & Time'},
        markers=True,
        height=400
    )
    fig2_html = fig2.to_html(full_html=False, include_plotlyjs='cdn')
    
    # Chart 3: Humidity vs Temperature
    fig3 = px.scatter(
        df,
        x='temp_c',
        y='humidity',
        color='location',
        size='wind_speed_kmph',
        hover_data=['condition'],
        title='Humidity vs Temperature',
        labels={'temp_c': 'Temperature (°C)', 'humidity': 'Humidity (%)'},
        height=400
    )
    fig3_html = fig3.to_html(full_html=False, include_plotlyjs='cdn')
    
    # Chart 4: Multi-metric comparison
    fig4 = make_subplots(
        rows=1, cols=3,
        subplot_titles=('Temperature', 'Humidity', 'Wind Speed')
    )
    
    fig4.add_trace(
        go.Bar(x=latest['location'], y=latest['temp_c'], name='Temp', marker_color='indianred'),
        row=1, col=1
    )
    fig4.add_trace(
        go.Bar(x=latest['location'], y=latest['humidity'], name='Humidity', marker_color='lightblue'),
        row=1, col=2
    )
    fig4.add_trace(
        go.Bar(x=latest['location'], y=latest['wind_speed_kmph'], name='Wind', marker_color='lightgreen'),
        row=1, col=3
    )
    
    fig4.update_xaxes(tickangle=45)
    fig4.update_layout(height=400, showlegend=False, title_text="Multi-Metric Comparison")
    fig4_html = fig4.to_html(full_html=False, include_plotlyjs='cdn')
    
    # Create HTML page with all charts
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Visualizations - Weather Dashboard</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 1400px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            h1 {{
                color: #2c3e50;
            }}
            nav {{
                background: #34495e;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 20px;
            }}
            nav a {{
                color: white;
                text-decoration: none;
                margin: 0 15px;
                font-weight: bold;
            }}
            nav a:hover {{
                color: #3498db;
            }}
            .chart-container {{
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                margin-bottom: 30px;
            }}
        </style>
    </head>
    <body>
        <nav>
            <a href="/">Home</a>
            <a href="/data">Data Table</a>
            <a href="/visualizations">Visualizations</a>
            <a href="/manage">Manage Cities</a>
            <a href="/stats">Statistics</a>
            <a href="/about">About</a>
        </nav>
        
        <h1>📊 Weather Data Visualizations</h1>
        <p>Interactive charts - hover over data points for details!</p>
        
        <div class="chart-container">
            {fig1_html}
        </div>
        
        <div class="chart-container">
            {fig2_html}
        </div>
        
        <div class="chart-container">
            {fig3_html}
        </div>
        
        <div class="chart-container">
            {fig4_html}
        </div>
    </body>
    </html>
    """
    
    return html
    
@app.route('/manage')
def manage_cities():
    """City management page - add cities and refresh data"""
    df = load_weather_data()
    
    # Get URL parameters for messages
    success = request.args.get('success')
    error = request.args.get('error')
    city_param = request.args.get('city', '')
    country_param = request.args.get('country', '')
    
    # Get list of cities currently tracked
    if not df.empty:
        # Group by actual city returned from API, but keep original request
        cities = df.groupby(['city', 'country']).agg({
            'timestamp': 'max',
            'temp_c': 'last',
            'latitude': 'first',
            'longitude': 'first',
            'id': 'count'
        }).reset_index()
        cities.columns = ['city', 'country', 'last_update', 'last_temp', 'latitude', 'longitude', 'record_count']
        cities['last_update'] = pd.to_datetime(cities['last_update'])
        cities = cities.sort_values('city')
    else:
        cities = pd.DataFrame()
    
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Manage Cities - Weather Dashboard</title>
        <style>
            body {
                font-family: Arial, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }
            h1, h2 {
                color: #2c3e50;
            }
            nav {
                background: #34495e;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 20px;
            }
            nav a {
                color: white;
                text-decoration: none;
                margin: 0 15px;
                font-weight: bold;
            }
            nav a:hover {
                color: #3498db;
            }
            .section {
                background: white;
                padding: 25px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                margin-bottom: 20px;
            }
            .form-group {
                margin-bottom: 15px;
            }
            label {
                display: block;
                margin-bottom: 5px;
                font-weight: bold;
                color: #34495e;
            }
            input[type="text"] {
                width: 300px;
                padding: 10px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                font-size: 14px;
            }
            input[type="text"]:focus {
                outline: none;
                border-color: #3498db;
            }
            button {
                background: #3498db;
                color: white;
                border: none;
                padding: 12px 25px;
                border-radius: 5px;
                font-size: 16px;
                cursor: pointer;
                font-weight: bold;
            }
            button:hover {
                background: #2980b9;
            }
            .refresh-btn {
                background: #27ae60;
            }
            .refresh-btn:hover {
                background: #229954;
            }
            .delete-btn {
                background: #e74c3c;
            }
            .delete-btn:hover {
                background: #c0392b;
            }
            .refresh-all-btn {
                background: #e67e22;
            }
            .refresh-all-btn:hover {
                background: #d35400;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin-top: 15px;
            }
            th {
                background: #34495e;
                color: white;
                padding: 12px;
                text-align: left;
            }
            td {
                padding: 10px;
                border-bottom: 1px solid #ecf0f1;
            }
            tr:hover {
                background: #f8f9fa;
            }
            .success-message {
                background: #d4edda;
                color: #155724;
                padding: 15px;
                border-radius: 5px;
                margin-bottom: 20px;
                border: 1px solid #c3e6cb;
            }
            .error-message {
                background: #f8d7da;
                color: #721c24;
                padding: 15px;
                border-radius: 5px;
                margin-bottom: 20px;
                border: 1px solid #f5c6cb;
            }
            .info-box {
                background: #d1ecf1;
                color: #0c5460;
                padding: 15px;
                border-radius: 5px;
                margin-bottom: 20px;
                border: 1px solid #bee5eb;
            }
            .city-actions {
                display: flex;
                gap: 10px;
            }
            .small-btn {
                padding: 6px 12px;
                font-size: 14px;
            }
            .location-info {
                color: #7f8c8d;
                font-size: 12px;
                margin-top: 3px;
            }
            .close-btn {
                float: right;
                cursor: pointer;
                font-size: 20px;
                font-weight: bold;
                color: #155724;
            }
            .close-btn:hover {
                color: #0d3d1a;
            }
        </style>
        <script>
            function closeMessage(id) {
                document.getElementById(id).style.display = 'none';
            }
            
            function confirmDelete(city, country) {
                return confirm(`Are you sure you want to stop tracking ${city}, ${country}?\\n\\nThis will delete all historical data for this city.`);
            }
        </script>
    </head>
    <body>
        <nav>
            <a href="/">Home</a>
            <a href="/data">Data Table</a>
            <a href="/visualizations">Visualizations</a>
            <a href="/manage">Manage Cities</a>
            <a href="/stats">Statistics</a>
            <a href="/about">About</a>
        </nav>
        
        <h1>🏙️ Manage Cities</h1>
    """
    
    # Show success message
    if success == 'added':
        html += f"""
        <div class="success-message" id="success-msg">
            <span class="close-btn" onclick="closeMessage('success-msg')">&times;</span>
            <strong>✓ Success!</strong> Weather data for <strong>{city_param}, {country_param}</strong> has been added.
            <br><small>Check the city list below to see the actual location data was collected for.</small>
        </div>
        """
    elif success == 'refreshed':
        html += f"""
        <div class="success-message" id="success-msg">
            <span class="close-btn" onclick="closeMessage('success-msg')">&times;</span>
            <strong>✓ Success!</strong> Weather data has been refreshed for <strong>{city_param}, {country_param}</strong>.
        </div>
        """
    elif success == 'refreshed_all':
        html += """
        <div class="success-message" id="success-msg">
            <span class="close-btn" onclick="closeMessage('success-msg')">&times;</span>
            <strong>✓ Success!</strong> All cities have been refreshed with the latest weather data.
        </div>
        """
    elif success == 'deleted':
        html += f"""
        <div class="success-message" id="success-msg">
            <span class="close-btn" onclick="closeMessage('success-msg')">&times;</span>
            <strong>✓ Deleted!</strong> Stopped tracking <strong>{city_param}, {country_param}</strong> and removed all historical data.
        </div>
        """
    
    # Show error message
    if error == 'missing':
        html += """
        <div class="error-message" id="error-msg">
            <span class="close-btn" onclick="closeMessage('error-msg')">&times;</span>
            <strong>✗ Error!</strong> City and country are required.
        </div>
        """
    elif error == 'failed':
        html += """
        <div class="error-message" id="error-msg">
            <span class="close-btn" onclick="closeMessage('error-msg')">&times;</span>
            <strong>✗ Error!</strong> Failed to fetch weather data. Please try again.
        </div>
        """
    
    html += """
        <div class="info-box">
            💡 <strong>Note:</strong> The API may return data for a nearby location instead of the exact city you requested. 
            For example, "Athens, Greece" might return "Kipseli" (a neighborhood in Athens). The coordinates shown 
            will help you verify the actual location.
        </div>
        
        <div class="section">
            <h2>Add New City</h2>
            <form action="/add_city" method="POST">
                <div class="form-group">
                    <label for="city">City Name:</label>
                    <input type="text" id="city" name="city" placeholder="e.g., Athens" required>
                </div>
                <div class="form-group">
                    <label for="country">Country:</label>
                    <input type="text" id="country" name="country" placeholder="e.g., Greece" required>
                </div>
                <button type="submit">Add City & Fetch Data</button>
            </form>
        </div>
        
        <div class="section">
            <h2>Currently Tracked Cities</h2>
    """
    
    if not cities.empty:
        html += f"""
            <p>Tracking {len(cities)} cities</p>
            <form action="/refresh_all" method="POST" style="margin-bottom: 15px;">
                <button type="submit" class="refresh-all-btn">🔄 Refresh All Cities</button>
            </form>
            
            <table>
                <thead>
                    <tr>
                        <th>Location</th>
                        <th>Coordinates</th>
                        <th>Records</th>
                        <th>Last Temp</th>
                        <th>Last Update</th>
                        <th>Actions</th>
                    </tr>
                </thead>
                <tbody>
        """
        
        for _, row in cities.iterrows():
            city = row['city']
            country = row['country']
            last_update = row['last_update'].strftime('%Y-%m-%d %H:%M')
            
            # Calculate time since last update
            age = datetime.now() - row['last_update']
            age_str = f"{age.seconds // 3600}h {(age.seconds % 3600) // 60}m ago"
            if age.days > 0:
                age_str = f"{age.days}d {age_str}"
            
            # Display location with coordinates
            location_display = f"<strong>{city}</strong>, {country}"
            coord_display = f"{row['latitude']}, {row['longitude']}"
            
            html += f"""
                <tr>
                    <td>
                        {location_display}
                        <div class="location-info">📍 Actual API location</div>
                    </td>
                    <td>
                        <small>{coord_display}</small>
                    </td>
                    <td>{row['record_count']}</td>
                    <td>{row['last_temp']:.1f}°C</td>
                    <td>{last_update}<br><small style="color: #7f8c8d;">{age_str}</small></td>
                    <td>
                        <div class="city-actions">
                            <form action="/refresh_city" method="POST" style="margin: 0;">
                                <input type="hidden" name="city" value="{city}">
                                <input type="hidden" name="country" value="{country}">
                                <button type="submit" class="refresh-btn small-btn">🔄 Refresh</button>
                            </form>
                            <form action="/delete_city" method="POST" style="margin: 0;" 
                                  onsubmit="return confirmDelete('{city}', '{country}')">
                                <input type="hidden" name="city" value="{city}">
                                <input type="hidden" name="country" value="{country}">
                                <button type="submit" class="delete-btn small-btn">🗑️ Delete</button>
                            </form>
                        </div>
                    </td>
                </tr>
            """
        
        html += """
                </tbody>
            </table>
        """
    else:
        html += "<p>No cities tracked yet. Add one above!</p>"
    
    html += """
        </div>
    </body>
    </html>
    """
    
    return html

@app.route('/add_city', methods=['POST'])
def add_city():
    """Handle adding a new city"""
    city = request.form.get('city', '').strip()
    country = request.form.get('country', '').strip()
    
    if not city or not country:
        return redirect(url_for('manage_cities') + '?error=missing')
    
    # Run ETL for this city
    pipeline = WeatherETLPipeline()
    success = pipeline.run_etl(city, country=country)
    
    if success:
        # Redirect with success message
        return redirect(url_for('manage_cities') + f'?success=added&city={city}&country={country}')
    else:
        return redirect(url_for('manage_cities') + '?error=failed')
        
@app.route('/delete_city', methods=['POST'])
def delete_city():
    """Delete all data for a specific city"""
    city = request.form.get('city', '').strip()
    country = request.form.get('country', '').strip()
    
    if not city or not country:
        return redirect(url_for('manage_cities') + '?error=missing')
    
    try:
        # Delete all records for this city from database
        conn = sqlite3.connect('weather.db')
        cursor = conn.cursor()
        
        cursor.execute("""
            DELETE FROM weather_data 
            WHERE city = ? AND country = ?
        """, (city, country))
        
        deleted_count = cursor.rowcount
        conn.commit()
        conn.close()
        
        if deleted_count > 0:
            return redirect(url_for('manage_cities') + f'?success=deleted&city={city}&country={country}')
        else:
            return redirect(url_for('manage_cities') + '?error=notfound')
            
    except Exception as e:
        print(f"Error deleting city: {e}")
        return redirect(url_for('manage_cities') + '?error=failed')

@app.route('/refresh_city', methods=['POST'])
def refresh_city():
    """Refresh data for a specific city"""
    city = request.form.get('city', '').strip()
    country = request.form.get('country', '').strip()
    
    if not city or not country:
        return redirect(url_for('manage_cities') + '?error=missing')
    
    # Run ETL for this city
    pipeline = WeatherETLPipeline()
    success = pipeline.run_etl(city, country=country)
    
    if success:
        return redirect(url_for('manage_cities') + f'?success=refreshed&city={city}&country={country}')
    else:
        return redirect(url_for('manage_cities') + '?error=failed')

@app.route('/refresh_all', methods=['POST'])
def refresh_all():
    """Refresh data for all tracked cities"""
    df = load_weather_data()
    
    if df.empty:
        return redirect(url_for('manage_cities'))
    
    # Get unique cities
    cities = df[['city', 'country']].drop_duplicates().to_dict('records')
    
    # Run ETL for each city
    pipeline = WeatherETLPipeline()
    
    for location in cities:
        pipeline.run_etl(location['city'], country=location['country'])
        time.sleep(2)  # Be nice to the API
    
    # Redirect with success message
    return redirect(url_for('manage_cities') + '?success=refreshed_all')

@app.route('/stats')
def statistics():
    """Statistics and analytics page"""
    df = load_weather_data()
    
    if df.empty:
        return "<h1>No data available</h1>"
    
    # Calculate statistics
    total_records = len(df)
    cities_count = df['location'].nunique()
    date_range = f"{df['date'].min().strftime('%Y-%m-%d')} to {df['date'].max().strftime('%Y-%m-%d')}"
    
    # Temperature stats
    avg_temp = df['temp_c'].mean()
    min_temp = df['temp_c'].min()
    max_temp = df['temp_c'].max()
    
    # Find hottest and coldest cities
    latest = df.sort_values('timestamp').groupby('location').last()
    hottest_city = latest['temp_c'].idxmax()
    hottest_temp = latest['temp_c'].max()
    coldest_city = latest['temp_c'].idxmin()
    coldest_temp = latest['temp_c'].min()
    
    # City statistics
    city_stats = df.groupby('location').agg({
        'temp_c': ['mean', 'min', 'max', 'std'],
        'humidity': 'mean',
        'wind_speed_kmph': 'mean',
        'id': 'count'
    }).round(2)
    city_stats.columns = ['Avg Temp', 'Min Temp', 'Max Temp', 'Temp Std', 'Avg Humidity', 'Avg Wind', 'Records']
    city_stats = city_stats.sort_values('Avg Temp', ascending=False)
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Statistics - Weather Dashboard</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                max-width: 1200px;
                margin: 0 auto;
                padding: 20px;
                background-color: #f5f5f5;
            }}
            h1, h2 {{
                color: #2c3e50;
            }}
            nav {{
                background: #34495e;
                padding: 15px;
                border-radius: 8px;
                margin-bottom: 20px;
            }}
            nav a {{
                color: white;
                text-decoration: none;
                margin: 0 15px;
                font-weight: bold;
            }}
            nav a:hover {{
                color: #3498db;
            }}
            .stats-grid {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
                gap: 20px;
                margin: 20px 0;
            }}
            .stat-card {{
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                text-align: center;
            }}
            .stat-value {{
                font-size: 36px;
                font-weight: bold;
                color: #3498db;
                margin: 10px 0;
            }}
            .stat-label {{
                color: #7f8c8d;
                font-size: 14px;
            }}
            .section {{
                background: white;
                padding: 25px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
                margin: 20px 0;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 15px;
            }}
            th {{
                background: #34495e;
                color: white;
                padding: 12px;
                text-align: left;
            }}
            td {{
                padding: 10px;
                border-bottom: 1px solid #ecf0f1;
            }}
            tr:hover {{
                background: #f8f9fa;
            }}
            .hot {{
                color: #e74c3c;
                font-weight: bold;
            }}
            .cold {{
                color: #3498db;
                font-weight: bold;
            }}
        </style>
    </head>
    <body>
        <nav>
            <a href="/">Home</a>
            <a href="/data">Data Table</a>
            <a href="/visualizations">Visualizations</a>
            <a href="/manage">Manage Cities</a>
            <a href="/stats">Statistics</a>
            <a href="/about">About</a>
        </nav>
        
        <h1>📈 Weather Statistics</h1>
        
        <div class="stats-grid">
            <div class="stat-card">
                <div class="stat-label">Total Records</div>
                <div class="stat-value">{total_records}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Cities Tracked</div>
                <div class="stat-value">{cities_count}</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Average Temperature</div>
                <div class="stat-value">{avg_temp:.1f}°C</div>
            </div>
            <div class="stat-card">
                <div class="stat-label">Temperature Range</div>
                <div class="stat-value">{min_temp:.1f}° - {max_temp:.1f}°</div>
            </div>
        </div>
        
        <div class="section">
            <h2>🔥 Hottest & 🥶 Coldest</h2>
            <p><span class="hot">🔥 Hottest:</span> {hottest_city} at {hottest_temp:.1f}°C</p>
            <p><span class="cold">🥶 Coldest:</span> {coldest_city} at {coldest_temp:.1f}°C</p>
        </div>
        
        <div class="section">
            <h2>City Statistics Summary</h2>
            <table>
                <thead>
                    <tr>
                        <th>City</th>
                        <th>Avg Temp (°C)</th>
                        <th>Min Temp (°C)</th>
                        <th>Max Temp (°C)</th>
                        <th>Temp Variation</th>
                        <th>Avg Humidity (%)</th>
                        <th>Avg Wind (km/h)</th>
                        <th>Records</th>
                    </tr>
                </thead>
                <tbody>
    """
    
    for city, row in city_stats.iterrows():
        html += f"""
                <tr>
                    <td><strong>{city}</strong></td>
                    <td>{row['Avg Temp']:.1f}</td>
                    <td>{row['Min Temp']:.1f}</td>
                    <td>{row['Max Temp']:.1f}</td>
                    <td>{row['Temp Std']:.1f}</td>
                    <td>{row['Avg Humidity']:.1f}</td>
                    <td>{row['Avg Wind']:.1f}</td>
                    <td>{int(row['Records'])}</td>
                </tr>
        """
    
    html += f"""
                </tbody>
            </table>
        </div>
        
        <div class="section">
            <h2>📅 Data Collection Period</h2>
            <p>{date_range}</p>
        </div>
    </body>
    </html>
    """
    
    return html

@app.route('/loading')
def loading():
    """Loading page shown during data fetch"""
    html = """
    <!DOCTYPE html>
    <html>
    <head>
        <title>Loading...</title>
        <meta http-equiv="refresh" content="5;url=/">
        <style>
            body {
                font-family: Arial, sans-serif;
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                margin: 0;
            }
            .loader-container {
                text-align: center;
                color: white;
            }
            .spinner {
                border: 8px solid #f3f3f3;
                border-top: 8px solid #3498db;
                border-radius: 50%;
                width: 60px;
                height: 60px;
                animation: spin 1s linear infinite;
                margin: 0 auto 20px;
            }
            @keyframes spin {
                0% { transform: rotate(0deg); }
                100% { transform: rotate(360deg); }
            }
            h1 {
                font-size: 32px;
                margin-bottom: 10px;
            }
            p {
                font-size: 18px;
                opacity: 0.9;
            }
        </style>
    </head>
    <body>
        <div class="loader-container">
            <div class="spinner"></div>
            <h1>🌤️ Fetching Weather Data...</h1>
            <p>This may take a few moments</p>
            <p><small>You'll be redirected automatically</small></p>
        </div>
    </body>
    </html>
    """
    return html


# ===== RUN THE APP =====

if __name__ == '__main__':
    print("\n" + "=" * 70)
    print("STARTING WEATHER DASHBOARD WEB APPLICATION")
    print("=" * 70)
    print("\n🌐 Server starting...")
    print("📍 Open your browser and go to: http://127.0.0.1:5000")
    print("\n💡 Press CTRL+C to stop the server\n")
    print("=" * 70 + "\n")
    
    app.run(debug=True, port=5000)

