import requests
import pandas as pd
import sqlite3
from datetime import datetime
import os

def fetch_air_quality_data():
    """
    I created this function to fetch real-time air quality data from the OpenAQ API.
    I'm using their v2 API endpoint with authentication to get the most recent measurements.
    """
    # I'm using my OpenAQ API key for authenticated access to their service
    API_URL = "https://api.openaq.org/v2/measurements"
    API_KEY = "3380c40ee807e917c4ecaad9219ca9c2c3b198ec5b5228eba1dce39960a3ab63"
    
    # I included the API key in the headers for authentication
    headers = {
        "X-API-Key": API_KEY
    }
    
    # I set these parameters to get today's data, limited to 1000 records for manageability
    params = {
        "limit": 1000,
        "page": 1,
        "date_from": (datetime.now()).strftime("%Y-%m-%d"),
        "order_by": "datetime"
    }
    
    try:
        # I make the API request here with proper error handling
        response = requests.get(API_URL, headers=headers, params=params)
        
        # I check if the request was successful before proceeding
        if response.status_code == 200:
            # I extract the results from the JSON response
            data = response.json()["results"]
            
            # I convert the data to a pandas DataFrame for easier manipulation
            air = pd.DataFrame(data)
            
            # I print these previews to help with debugging and verification
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
    I created this function to clean and transform the raw air quality data.
    I'm focusing on PM2.5 measurements and ensuring the data is in a consistent format.
    """
    try:
        # I work with a copy to preserve the original data
        cleaned_df = df.copy()
        
        # I remove columns we don't need for our analysis
        columns_to_drop = ['city', 'isAnalysis', 'isMobile', 'entity', 'sensorType']
        cleaned_df = cleaned_df.drop(columns=[col for col in columns_to_drop if col in cleaned_df.columns])
        
        # I filter for PM2.5 measurements since that's our focus
        cleaned_df = cleaned_df[cleaned_df['parameter'] == 'pm25']
        
        # I handle the nested coordinate data by extracting latitude and longitude
        if 'coordinates' in cleaned_df.columns:
            cleaned_df['latitude'] = cleaned_df['coordinates'].apply(lambda x: x.get('latitude') if isinstance(x, dict) else None)
            cleaned_df['longitude'] = cleaned_df['coordinates'].apply(lambda x: x.get('longitude') if isinstance(x, dict) else None)
            cleaned_df = cleaned_df.drop('coordinates', axis=1)
        
        # I convert the timestamps to a standardized format
        if 'date' in cleaned_df.columns:
            cleaned_df['datetime_utc'] = pd.to_datetime(cleaned_df['date'].apply(lambda x: x.get('utc') if isinstance(x, dict) else x))
            cleaned_df = cleaned_df.drop('date', axis=1)
        
        # I remove invalid measurements (negative values don't make sense for PM2.5)
        cleaned_df = cleaned_df[cleaned_df['value'] > 0]
        
        # I rename the value column to be more specific
        cleaned_df = cleaned_df.rename(columns={'value': 'pm25_value'})
        
        # I select and reorder columns to match our database schema
        cleaned_df = cleaned_df[['location', 'parameter', 'pm25_value', 'unit', 'latitude', 'longitude', 'datetime_utc']]
        
        # I print these previews to verify the transformation
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
    I created this function to store our cleaned data in a SQLite database.
    I'm using SQLite because it's lightweight and perfect for our needs.
    """
    try:
        # I specify the database path in the current directory
        db_path = 'air.db'
        
        # I remove any existing database to start fresh
        if os.path.exists(db_path):
            os.remove(db_path)
            print(f"Removed existing database at {db_path}")
        
        # I create a new connection to the database
        print(f"Creating new database at {db_path}")
        conn = sqlite3.connect(db_path)
        
        # I create the table with appropriate columns for our data
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
        
        # I load the data into our table, replacing any existing data
        df.to_sql('quality', conn, if_exists='replace', index=False)
        
        # I verify the data was loaded correctly
        row_count = conn.execute("SELECT COUNT(*) FROM quality").fetchone()[0]
        print(f"\nSuccessfully loaded {row_count} records into the quality table")
        
        # I show a preview of the loaded data for verification
        print("\nPreview of data in SQLite:")
        preview_df = pd.read_sql_query("SELECT * FROM quality LIMIT 5", conn)
        print(preview_df)
        
        # I make sure to close the connection properly
        conn.close()
        print(f"\nDatabase connection closed. Database saved at {db_path}")
        
    except Exception as e:
        print(f"An error occurred while loading to SQLite: {str(e)}")
        print(f"Error details: {str(e)}")
        # I ensure the connection is closed even if an error occurs
        if 'conn' in locals():
            conn.close()

if __name__ == "__main__":
    # I run the ETL process in sequence
    raw_data = fetch_air_quality_data()
    
    if raw_data is not None:
        cleaned_data = transform(raw_data)
        
        if cleaned_data is not None:
            load_to_sqlite(cleaned_data)