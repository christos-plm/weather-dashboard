# visualizer.py - Weather data visualization
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import pandas as pd
import sqlite3
from datetime import datetime

class WeatherVisualizer:
    """
    Creates visualizations for weather data analysis
    """
    
    def __init__(self, db_name='weather.db'):
        self.db_name = db_name
        self.df = self.load_data()
    
    def load_data(self):
        """Load weather data into pandas DataFrame"""
        conn = sqlite3.connect(self.db_name)
        
        query = "SELECT * FROM weather_data ORDER BY timestamp"
        df = pd.read_sql_query(query, conn)
        
        conn.close()
        
        if not df.empty:
            # Convert to datetime
            df['date'] = pd.to_datetime(df['date'])
            df['timestamp'] = pd.to_datetime(df['timestamp'])
            
            # Create city-country label for clearer display
            df['location'] = df['city'] + ', ' + df['country']
        
        return df
    
    def plot_temperature_by_city(self):
        """
        Bar chart: Current temperature by city
        """
        if self.df.empty:
            print("No data available for visualization")
            return
        
        # Get the latest reading for each city
        latest = self.df.sort_values('timestamp').groupby('location').last().reset_index()
        
        # Sort by temperature
        latest = latest.sort_values('temp_c', ascending=True)
        
        # Create bar chart
        fig = px.bar(
            latest,
            x='temp_c',
            y='location',
            orientation='h',
            title='Current Temperature by City',
            labels={'temp_c': 'Temperature (°C)', 'location': 'City'},
            color='temp_c',
            color_continuous_scale='RdYlBu_r',  # Red (hot) to Blue (cold)
            text='temp_c'
        )
        
        # Customize layout
        fig.update_traces(texttemplate='%{text:.1f}°C', textposition='outside')
        fig.update_layout(
            height=500,
            showlegend=False,
            xaxis_title="Temperature (°C)",
            yaxis_title="",
        )
        
        fig.show()
        print("✓ Temperature comparison chart created")
    
    def plot_temperature_trends(self):
        """
        Line chart: Temperature trends over time for each city
        """
        if self.df.empty:
            print("No data available for visualization")
            return
        
        fig = px.line(
            self.df,
            x='timestamp',
            y='temp_c',
            color='location',
            title='Temperature Trends Over Time',
            labels={
                'temp_c': 'Temperature (°C)',
                'timestamp': 'Date & Time',
                'location': 'City'
            },
            markers=True
        )
        
        fig.update_layout(
            height=500,
            hovermode='x unified',
            legend=dict(
                orientation="v",
                yanchor="top",
                y=1,
                xanchor="left",
                x=1.02
            )
        )
        
        fig.show()
        print("✓ Temperature trends chart created")
    
    def plot_humidity_vs_temperature(self):
        """
        Scatter plot: Relationship between humidity and temperature
        """
        if self.df.empty:
            print("No data available for visualization")
            return
        
        fig = px.scatter(
            self.df,
            x='temp_c',
            y='humidity',
            color='location',
            size='wind_speed_kmph',
            hover_data=['condition', 'feels_like_c'],
            title='Humidity vs Temperature (bubble size = wind speed)',
            labels={
                'temp_c': 'Temperature (°C)',
                'humidity': 'Humidity (%)',
                'location': 'City',
                'wind_speed_kmph': 'Wind Speed (km/h)'
            }
        )
        
        fig.update_layout(height=500)
        fig.show()
        print("✓ Humidity vs Temperature scatter plot created")
    
    def plot_weather_conditions_distribution(self):
        """
        Pie chart: Distribution of weather conditions
        """
        if self.df.empty:
            print("No data available for visualization")
            return
        
        # Count occurrences of each condition
        condition_counts = self.df['condition'].value_counts()
        
        fig = px.pie(
            values=condition_counts.values,
            names=condition_counts.index,
            title='Weather Conditions Distribution',
            hole=0.3  # Makes it a donut chart
        )
        
        fig.update_traces(textposition='inside', textinfo='percent+label')
        fig.update_layout(height=500)
        
        fig.show()
        print("✓ Weather conditions distribution chart created")
    
    def plot_comfort_analysis(self):
        """
        Multi-panel visualization: Temperature, humidity, and wind by city
        """
        if self.df.empty:
            print("No data available for visualization")
            return
        
        # Get latest data for each city
        latest = self.df.sort_values('timestamp').groupby('location').last().reset_index()
        latest = latest.sort_values('temp_c', ascending=False)
        
        # Create subplots
        fig = make_subplots(
            rows=2, cols=2,
            subplot_titles=(
                'Temperature by City',
                'Humidity by City',
                'Wind Speed by City',
                'Feels Like vs Actual Temperature'
            ),
            specs=[
                [{"type": "bar"}, {"type": "bar"}],
                [{"type": "bar"}, {"type": "scatter"}]
            ]
        )
        
        # Temperature bars
        fig.add_trace(
            go.Bar(
                x=latest['location'],
                y=latest['temp_c'],
                name='Temperature',
                marker_color='indianred'
            ),
            row=1, col=1
        )
        
        # Humidity bars
        fig.add_trace(
            go.Bar(
                x=latest['location'],
                y=latest['humidity'],
                name='Humidity',
                marker_color='lightblue'
            ),
            row=1, col=2
        )
        
        # Wind speed bars
        fig.add_trace(
            go.Bar(
                x=latest['location'],
                y=latest['wind_speed_kmph'],
                name='Wind Speed',
                marker_color='lightgreen'
            ),
            row=2, col=1
        )
        
        # Feels like scatter
        fig.add_trace(
            go.Scatter(
                x=latest['temp_c'],
                y=latest['feels_like_c'],
                mode='markers+text',
                text=latest['location'],
                textposition='top center',
                marker=dict(size=12, color='coral'),
                name='Feels Like'
            ),
            row=2, col=2
        )
        
        # Add diagonal line for reference (feels like = actual)
        temp_range = [latest['temp_c'].min(), latest['temp_c'].max()]
        fig.add_trace(
            go.Scatter(
                x=temp_range,
                y=temp_range,
                mode='lines',
                line=dict(dash='dash', color='gray'),
                name='Actual = Feels Like',
                showlegend=False
            ),
            row=2, col=2
        )
        
        # Update axes labels
        fig.update_xaxes(title_text="City", row=1, col=1, tickangle=45)
        fig.update_xaxes(title_text="City", row=1, col=2, tickangle=45)
        fig.update_xaxes(title_text="City", row=2, col=1, tickangle=45)
        fig.update_xaxes(title_text="Actual Temp (°C)", row=2, col=2)
        
        fig.update_yaxes(title_text="Temperature (°C)", row=1, col=1)
        fig.update_yaxes(title_text="Humidity (%)", row=1, col=2)
        fig.update_yaxes(title_text="Wind Speed (km/h)", row=2, col=1)
        fig.update_yaxes(title_text="Feels Like (°C)", row=2, col=2)
        
        fig.update_layout(
            height=800,
            title_text="Weather Comfort Analysis Dashboard",
            showlegend=False
        )
        
        fig.show()
        print("✓ Multi-panel comfort analysis dashboard created")
    
    def plot_city_comparison_radar(self):
        """
        Radar chart: Compare multiple metrics for cities
        """
        if self.df.empty:
            print("No data available for visualization")
            return
        
        # Get latest data for each city
        latest = self.df.sort_values('timestamp').groupby('location').last().reset_index()
        
        # Normalize values to 0-100 scale for fair comparison
        latest['temp_normalized'] = ((latest['temp_c'] - latest['temp_c'].min()) /
                                     (latest['temp_c'].max() - latest['temp_c'].min())) * 100
        latest['humidity_normalized'] = latest['humidity']  # Already 0-100
        latest['wind_normalized'] = ((latest['wind_speed_kmph'] - latest['wind_speed_kmph'].min()) /
                                     (latest['wind_speed_kmph'].max() - latest['wind_speed_kmph'].min())) * 100
        latest['pressure_normalized'] = ((latest['pressure_mb'] - latest['pressure_mb'].min()) /
                                        (latest['pressure_mb'].max() - latest['pressure_mb'].min())) * 100
        
        # Create radar chart
        fig = go.Figure()
        
        categories = ['Temperature', 'Humidity', 'Wind Speed', 'Pressure']
        
        # Add a trace for each city (limit to first 5 for readability)
        for idx, row in latest.head(5).iterrows():
            fig.add_trace(go.Scatterpolar(
                r=[
                    row['temp_normalized'],
                    row['humidity_normalized'],
                    row['wind_normalized'],
                    row['pressure_normalized']
                ],
                theta=categories,
                fill='toself',
                name=row['location']
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 100]
                )
            ),
            showlegend=True,
            title="City Weather Comparison (Normalized Values)",
            height=600
        )
        
        fig.show()
        print("✓ Radar comparison chart created")
    
    def generate_summary_statistics(self):
        """
        Display summary statistics table
        """
        if self.df.empty:
            print("No data available")
            return
        
        print("\n" + "=" * 70)
        print("WEATHER DATA SUMMARY STATISTICS")
        print("=" * 70)
        
        summary = self.df.groupby('location').agg({
            'temp_c': ['mean', 'min', 'max', 'std'],
            'humidity': 'mean',
            'wind_speed_kmph': 'mean',
            'pressure_mb': 'mean',
            'id': 'count'
        }).round(2)
        
        summary.columns = ['Avg Temp', 'Min Temp', 'Max Temp', 'Temp Std',
                          'Avg Humidity', 'Avg Wind', 'Avg Pressure', 'Records']
        
        print(summary)
        print("=" * 70)
    
    def plot_temperature_heatmap(self):
        """
        Heatmap: Temperature by city and time
        """
        if self.df.empty:
            print("No data available")
            return
        
        # Pivot data for heatmap
        df_pivot = self.df.pivot_table(
            values='temp_c',
            index='location',
            columns=self.df['timestamp'].dt.hour,
            aggfunc='mean'
        )
        
        fig = px.imshow(
            df_pivot,
            labels=dict(x="Hour of Day", y="City", color="Temperature (°C)"),
            title="Temperature Heatmap by City and Hour",
            color_continuous_scale='RdYlBu_r',
            aspect='auto'
        )
        
        fig.update_xaxes(side="bottom")
        fig.update_layout(height=500)
        
        fig.show()
        print("✓ Temperature heatmap created")
    
    def plot_wind_rose(self):
        """
        Box plot: Wind speed distribution by city
        """
        if self.df.empty:
            print("No data available")
            return
        
        fig = px.box(
            self.df,
            x='location',
            y='wind_speed_kmph',
            color='location',
            title='Wind Speed Distribution by City',
            labels={
                'wind_speed_kmph': 'Wind Speed (km/h)',
                'location': 'City'
            },
            points='all'  # Show all data points
        )
        
        fig.update_layout(
            height=500,
            showlegend=False,
            xaxis_tickangle=45
        )
        
        fig.show()
        print("✓ Wind speed box plot created")
    
    def plot_comfort_score(self):
        """
        Calculate and visualize comfort score
        Based on temperature, humidity, and wind
        """
        if self.df.empty:
            print("No data available")
            return
        
        # Calculate comfort score (0-100)
        # Ideal: 20-25°C, 40-60% humidity, low wind
        def calculate_comfort(row):
            temp_score = 100 - abs(row['temp_c'] - 22.5) * 4
            humidity_score = 100 - abs(row['humidity'] - 50) * 2
            wind_penalty = min(row['wind_speed_kmph'] * 2, 50)
            
            score = (temp_score * 0.5 + humidity_score * 0.3 - wind_penalty * 0.2)
            return max(0, min(100, score))  # Clamp between 0-100
        
        latest = self.df.sort_values('timestamp').groupby('location').last().reset_index()
        latest['comfort_score'] = latest.apply(calculate_comfort, axis=1)
        latest = latest.sort_values('comfort_score', ascending=True)
        
        # Create color scale
        colors = ['red' if x < 40 else 'orange' if x < 60 else 'yellow' if x < 80 else 'green'
                 for x in latest['comfort_score']]
        
        fig = go.Figure(go.Bar(
            x=latest['comfort_score'],
            y=latest['location'],
            orientation='h',
            marker=dict(color=colors),
            text=latest['comfort_score'].round(1),
            textposition='outside'
        ))
        
        fig.update_layout(
            title='Weather Comfort Score by City (0-100)',
            xaxis_title='Comfort Score',
            yaxis_title='',
            height=500,
            showlegend=False
        )
        
        fig.show()
        print("✓ Comfort score visualization created")

    
    def create_all_visualizations(self):
        """
        Generate all visualizations in sequence
        """
        print("\n" + "=" * 70)
        print("GENERATING ALL VISUALIZATIONS")
        print("=" * 70)
        
        print("\n1. Creating temperature comparison chart...")
        self.plot_temperature_by_city()
        
        print("\n2. Creating temperature trends chart...")
        self.plot_temperature_trends()
        
        print("\n3. Creating humidity vs temperature scatter plot...")
        self.plot_humidity_vs_temperature()
        
        print("\n4. Creating weather conditions distribution...")
        self.plot_weather_conditions_distribution()
        
        print("\n5. Creating comfort analysis dashboard...")
        self.plot_comfort_analysis()
        
        print("\n6. Creating city comparison radar chart...")
        self.plot_city_comparison_radar()
        
        print("\n7. Displaying summary statistics...")
        self.generate_summary_statistics()
        
        print("\n8. Creating temperature heatmap...")
        self.plot_temperature_heatmap()
        
        print("\n9. Creating wind speed distribution...")
        self.plot_wind_rose()
        
        print("\n10. Creating comfort score analysis...")
        self.plot_comfort_score()
        
        print("\n" + "=" * 70)
        print("ALL VISUALIZATIONS COMPLETE!")
        print("=" * 70)


# ===== MAIN PROGRAM =====

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("WEATHER DATA VISUALIZER")
    print("=" * 70)
    
    # Create visualizer
    viz = WeatherVisualizer()
    
    # Check if we have data
    if viz.df.empty:
        print("\n⚠️  No data found in database!")
        print("Run etl_pipeline.py first to collect weather data.")
    else:
        print(f"\n✓ Loaded {len(viz.df)} weather records")
        print(f"✓ Tracking {viz.df['location'].nunique()} cities")
        
        # Generate all visualizations
        viz.create_all_visualizations()
        
        print("\n💡 TIP: Charts open in your web browser")
        print("   You can interact with them - hover, zoom, pan!")
    
    print("\n" + "=" * 70)
    print("VISUALIZATION SESSION COMPLETE!")
    print("=" * 70)

