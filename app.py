# app.py - Weather Dashboard Web Application
from flask import Flask, render_template, jsonify
import sqlite3
import pandas as pd
from datetime import datetime

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

