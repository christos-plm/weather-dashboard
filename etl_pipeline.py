# etl_pipeline.py - Complete ETL Pipeline with Transformation
import time
from datetime import datetime
from weather_collector import WeatherCollector
from data_transformer import WeatherDataTransformer

class WeatherETLPipeline:
    """
    Complete ETL Pipeline for weather data
    Extract → Transform → Load with quality checks
    """
    
    def __init__(self, db_name='weather.db'):
        self.collector = WeatherCollector(db_name)
        self.transformer = WeatherDataTransformer(db_name)
        self.stats = {
            'attempted': 0,
            'succeeded': 0,
            'failed': 0,
            'validation_errors': 0,
            'duplicates': 0
        }
    
    def extract_weather_data(self, city, country=None, lat=None, lon=None):
        """
        EXTRACT: Fetch data from API
        Returns: raw data or None
        """
        print(f"\n[EXTRACT] Fetching data for {city}...")
        data = self.collector.fetch_weather(city, country, lat, lon)
        
        if data:
            print(f"[EXTRACT] ✓ Data fetched successfully")
            return data
        else:
            print(f"[EXTRACT] ❌ Failed to fetch data")
            return None
    
    def transform_weather_data(self, data, city, country):
        """
        TRANSFORM: Parse, validate, clean, and enrich data
        Returns: (transformed_record, is_valid, issues)
        """
        print(f"[TRANSFORM] Processing data...")
        
        # Step 1: Parse the raw API response
        record = self.collector.parse_weather_data(data, city, country)
        
        if not record:
            print(f"[TRANSFORM] ❌ Failed to parse data")
            return None, False, ["Parse error"]
        
        # Step 2: Clean the data
        record = self.transformer.clean_weather_record(record)
        print(f"[TRANSFORM] ✓ Data cleaned")
        
        # Step 3: Validate the data
        is_valid, issues = self.transformer.validate_weather_record(record)
        
        if not is_valid:
            print(f"[TRANSFORM] ⚠️  Validation issues found:")
            for issue in issues:
                print(f"            - {issue}")
        else:
            print(f"[TRANSFORM] ✓ Data validated")
        
        # Step 4: Calculate derived fields
        record = self.transformer.calculate_derived_fields(record)
        print(f"[TRANSFORM] ✓ Derived fields calculated")
        
        # Step 5: Check for duplicates
        is_dup, dup_id = self.transformer.check_for_duplicate(record)
        if is_dup:
            print(f"[TRANSFORM] ⚠️  Duplicate detected (ID: {dup_id})")
            issues.append(f"Duplicate of record {dup_id}")
        
        return record, is_valid, issues
    
    def load_weather_data(self, record, is_valid, issues):
        """
        LOAD: Save data to database (only if valid)
        Returns: success boolean
        """
        print(f"[LOAD] Saving to database...")
        
        # Decide whether to load based on validation
        if not is_valid:
            print(f"[LOAD] ❌ Skipping invalid data")
            return False
        
        # Check if it's a duplicate
        if any('Duplicate' in issue for issue in issues):
            print(f"[LOAD] ⚠️  Skipping duplicate")
            return False
        
        # Save to database
        success = self.collector.save_weather_data(record)
        
        if success:
            print(f"[LOAD] ✓ Data saved successfully")
        else:
            print(f"[LOAD] ❌ Failed to save data")
        
        return success
    
    def run_etl(self, city, country=None, lat=None, lon=None):
        """
        Run complete ETL pipeline for one location
        """
        self.stats['attempted'] += 1
        
        print("\n" + "=" * 70)
        print(f"ETL PIPELINE: {city}" + (f", {country}" if country else ""))
        print("=" * 70)
        
        start_time = time.time()
        
        # EXTRACT
        data = self.extract_weather_data(city, country, lat, lon)
        if not data:
            self.stats['failed'] += 1
            return False
        
        # TRANSFORM
        record, is_valid, issues = self.transform_weather_data(data, city, country)
        if not record:
            self.stats['failed'] += 1
            return False
        
        if not is_valid:
            self.stats['validation_errors'] += 1
        
        if any('Duplicate' in issue for issue in issues):
            self.stats['duplicates'] += 1
        
        # LOAD
        success = self.load_weather_data(record, is_valid, issues)
        
        if success:
            self.stats['succeeded'] += 1
        
        elapsed = time.time() - start_time
        print(f"\n[COMPLETE] Pipeline finished in {elapsed:.2f} seconds")
        print("=" * 70)
        
        return success
    
    def run_batch_etl(self, locations, delay=2):
        """
        Run ETL for multiple locations
        locations: list of dicts with 'city' and 'country' keys
        delay: seconds to wait between requests
        """
        print("\n" + "=" * 70)
        print("BATCH ETL PIPELINE")
        print(f"Processing {len(locations)} locations")
        print("=" * 70)
        
        for i, loc in enumerate(locations, 1):
            print(f"\n[BATCH] Processing {i}/{len(locations)}")
            
            self.run_etl(
                loc['city'],
                loc.get('country'),
                loc.get('lat'),
                loc.get('lon')
            )
            
            # Wait between requests (be nice to the API)
            if i < len(locations):
                print(f"\n[BATCH] Waiting {delay} seconds...")
                time.sleep(delay)
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print pipeline execution summary"""
        print("\n" + "=" * 70)
        print("ETL PIPELINE SUMMARY")
        print("=" * 70)
        print(f"Total attempted: {self.stats['attempted']}")
        print(f"Succeeded: {self.stats['succeeded']}")
        print(f"Failed: {self.stats['failed']}")
        print(f"Validation errors: {self.stats['validation_errors']}")
        print(f"Duplicates skipped: {self.stats['duplicates']}")
        
        if self.stats['attempted'] > 0:
            success_rate = (self.stats['succeeded'] / self.stats['attempted']) * 100
            print(f"Success rate: {success_rate:.1f}%")
        
        print("=" * 70)
    
    def generate_data_quality_report(self):
        """Generate and display data quality report"""
        print(self.transformer.get_data_quality_report())
    
    def show_statistics(self):
        """Show summary statistics"""
        summary = self.transformer.get_summary_statistics()
        if summary is not None:
            print("\n" + "=" * 70)
            print("WEATHER STATISTICS BY CITY")
            print("=" * 70)
            print(summary)
        else:
            print("No data available for statistics")


# ===== MAIN PROGRAM =====

if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("WEATHER DATA ETL PIPELINE")
    print("=" * 70)
    
    # Create pipeline
    pipeline = WeatherETLPipeline()
    
    # Define locations to collect
    locations = [
        {'city': 'Athens', 'country': 'Greece'},
        {'city': 'London', 'country': 'UK'},
        {'city': 'Paris', 'country': 'France'},
        {'city': 'Berlin', 'country': 'Germany'},
        {'city': 'Rome', 'country': 'Italy'},
        {'city': 'Madrid', 'country': 'Spain'},
        {'city': 'Amsterdam', 'country': 'Netherlands'},
        {'city': 'Vienna', 'country': 'Austria'},
    ]
    
    # Run batch ETL
    pipeline.run_batch_etl(locations, delay=2)
    
    # Generate reports
    print("\n")
    pipeline.generate_data_quality_report()
    
    print("\n")
    pipeline.show_statistics()
    
    print("\n" + "=" * 70)
    print("ETL PIPELINE COMPLETE!")
    print("=" * 70)

