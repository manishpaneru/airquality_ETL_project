import requests
import pandas as pd
import sqlite3
from datetime import datetime
import os

def fetch_air_quality_data():
    """
    Fetch air quality data from OpenAQ API
    """
    # API endpoint and key for OpenAQ
    API_URL = "https://api.openaq.org/v2/measurements"
    API_KEY = "3380c40ee807e917c4ecaad9219ca9c2c3b198ec5b5228eba1dce39960a3ab63"
    
    # Request headers with API Key
    headers = {
        "X-API-Key": API_KEY
    }
    
    # Parameters for the API request
    params = {
        "limit": 1000,  # Number of records to fetch
        "page": 1,
        "date_from": (datetime.now()).strftime("%Y-%m-%d"),  # Get today's data
        "order_by": "datetime"
    }
    
    try:
        # Make the API request with headers
        response = requests.get(API_URL, headers=headers, params=params)
        
        # Check if request was successful
        if response.status_code == 200:
            # Extract data from the JSON response
            data = response.json()["results"]
            
            # Convert to DataFrame
            air = pd.DataFrame(data)
            
            print("\nDataFrame Preview before transformation:")
            print(air.head())
            print("\nColumns in the raw dataset:")
            print(air.columns.tolist())
            
            return air
            
        else:
            print(f"Failed to fetch data. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
    except Exception as e:
        print(f"An error occurred: {str(e)}")
        return None

def transform(df):
    """
    Clean and transform the air quality data
    """
    try:
        # Create a copy of the dataframe to avoid modifying the original
        cleaned_df = df.copy()
        
        # Drop unnecessary columns
        columns_to_drop = ['city', 'isAnalysis', 'isMobile', 'entity', 'sensorType']
        cleaned_df = cleaned_df.drop(columns=[col for col in columns_to_drop if col in cleaned_df.columns])
        
        # Filter for PM2.5 measurements only
        cleaned_df = cleaned_df[cleaned_df['parameter'] == 'pm25']
        
        # Handle nested data
        # Extract coordinates
        if 'coordinates' in cleaned_df.columns:
            cleaned_df['latitude'] = cleaned_df['coordinates'].apply(lambda x: x.get('latitude') if isinstance(x, dict) else None)
            cleaned_df['longitude'] = cleaned_df['coordinates'].apply(lambda x: x.get('longitude') if isinstance(x, dict) else None)
            cleaned_df = cleaned_df.drop('coordinates', axis=1)
        
        # Convert date to datetime if it exists
        if 'date' in cleaned_df.columns:
            cleaned_df['datetime_utc'] = pd.to_datetime(cleaned_df['date'].apply(lambda x: x.get('utc') if isinstance(x, dict) else x))
            cleaned_df = cleaned_df.drop('date', axis=1)
        
        # Remove invalid measurements
        cleaned_df = cleaned_df[cleaned_df['value'] > 0]
        
        # Rename value column
        cleaned_df = cleaned_df.rename(columns={'value': 'pm25_value'})
        
        # Select and reorder columns to match the database schema
        cleaned_df = cleaned_df[['location', 'parameter', 'pm25_value', 'unit', 'latitude', 'longitude', 'datetime_utc']]
        
        print("\nDataFrame Preview after transformation:")
        print(cleaned_df.head())
        print("\nColumns in the cleaned dataset:")
        print(cleaned_df.columns.tolist())
        
        return cleaned_df
        
    except Exception as e:
        print(f"An error occurred during transformation: {str(e)}")
        return None

def load_to_sqlite(df):
    """
    Load the transformed data into SQLite database
    """
    try:
        # Specify the database path
        db_path = 'air.db'
        
        # Remove existing database if it exists
        if os.path.exists(db_path):
            os.remove(db_path)
            print(f"Removed existing database at {db_path}")
        
        # Connect to SQLite database
        print(f"Creating new database at {db_path}")
        conn = sqlite3.connect(db_path)
        
        # Create the quality table
        conn.execute("""
            CREATE TABLE IF NOT EXISTS quality (
                location TEXT,
                parameter TEXT,
                pm25_value REAL,
                unit TEXT,
                latitude REAL,
                longitude REAL,
                datetime_utc TIMESTAMP
            )
        """)
        
        # Load the DataFrame into the quality table
        df.to_sql('quality', conn, if_exists='replace', index=False)
        
        # Get the number of rows in the table
        row_count = conn.execute("SELECT COUNT(*) FROM quality").fetchone()[0]
        print(f"\nSuccessfully loaded {row_count} records into the quality table")
        
        # Show a preview of the data in the table
        print("\nPreview of data in SQLite:")
        preview_df = pd.read_sql_query("SELECT * FROM quality LIMIT 5", conn)
        print(preview_df)
        
        # Close the connection
        conn.close()
        print(f"\nDatabase connection closed. Database saved at {db_path}")
        
    except Exception as e:
        print(f"An error occurred while loading to SQLite: {str(e)}")
        print(f"Error details: {str(e)}")
        # If connection exists, close it
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    # Extract
    raw_data = fetch_air_quality_data()
    
    # Transform
    if raw_data is not None:
        cleaned_data = transform(raw_data)
        
        # Load
        if cleaned_data is not None:
            load_to_sqlite(cleaned_data)