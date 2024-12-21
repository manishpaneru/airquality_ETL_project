import streamlit as st
import pandas as pd
import sqlite3
import plotly.express as px
import plotly.graph_objects as go
import numpy as np

# I configured the page layout to be wide and added a globe icon to match our air quality theme
st.set_page_config(
    page_title="Air Quality Live Analysis",
    page_icon="🌍",
    layout="wide"
)

# I added a title and my name as the creator to establish ownership and professionalism
st.title("🌍 Air Quality Live Analysis")
st.markdown("Created by Manish Paneru")
st.markdown("---")

# I created this function to efficiently load and cache our data from SQLite
# This way, we don't have to reload the data every time the user interacts with the app
@st.cache_data
def load_data():
    conn = sqlite3.connect('air.db')
    df = pd.read_sql_query("SELECT * FROM quality", conn)
    conn.close()
    return df

# Load the data once when the app starts
df = load_data()

# I added these filters in the sidebar to make the app interactive and user-friendly
st.sidebar.header("Filters")
countries = sorted(df['location'].unique())
selected_country = st.sidebar.selectbox("Select Location", countries)

# Section 1: I created this bar chart to visualize the most polluted locations
st.header("1. Top Polluted Locations")
top_n = st.slider("Select number of locations to show", 5, 20, 10)

# I calculated average PM2.5 values for each location to show overall pollution levels
avg_pm25 = df.groupby('location')['pm25_value'].mean().sort_values(ascending=False).head(top_n)

# I used color coding to make it easy to identify dangerous pollution levels:
# Green for safe, Yellow for moderate, Red for dangerous
colors = ['green' if x < 50 else 'yellow' if x < 100 else 'red' for x in avg_pm25.values]

fig_bar = px.bar(
    x=avg_pm25.index,
    y=avg_pm25.values,
    title=f"Top {top_n} Locations by PM2.5 Levels",
    labels={'x': 'Location', 'y': 'Average PM2.5 (µg/m³)'}
)
fig_bar.update_traces(marker_color=colors)
st.plotly_chart(fig_bar, use_container_width=True)

# Section 2: I implemented this interactive map to show the geographic distribution of pollution
st.header("2. PM2.5 Distribution Map")
pm25_threshold = st.slider("PM2.5 Threshold (µg/m³)", 0, 200, 50)

# I filtered the data based on user-selected threshold for better visualization
map_data = df[df['pm25_value'] >= pm25_threshold].copy()

# I used the same color scheme as the bar chart for consistency
map_data['color'] = map_data['pm25_value'].apply(
    lambda x: 'green' if x < 50 else 'yellow' if x < 100 else 'red'
)

# I chose a clean map style and added hover data for better user interaction
fig_map = px.scatter_mapbox(
    map_data,
    lat='latitude',
    lon='longitude',
    color='pm25_value',
    size=np.ones(len(map_data)) * 10,
    hover_data=['location', 'pm25_value'],
    color_continuous_scale=['green', 'yellow', 'red'],
    zoom=1,
    title='PM2.5 Distribution Map',
    mapbox_style='carto-positron'
)

fig_map.update_layout(
    margin={"r":0,"t":30,"l":0,"b":0},
    height=600
)

st.plotly_chart(fig_map, use_container_width=True)

# Section 3: I created this ranked table with gradient colors to show detailed measurements
st.header("3. Air Quality Rankings")
st.dataframe(
    df[['location', 'pm25_value', 'datetime_utc']]
    .sort_values('pm25_value', ascending=False)
    .style.background_gradient(subset=['pm25_value'], cmap='RdYlGn_r'),
    height=400
)

# Section 4: I added these summary statistics to give users a quick overview
st.header("4. Summary Statistics")
col1, col2, col3 = st.columns(3)

with col1:
    st.metric("Maximum PM2.5", f"{df['pm25_value'].max():.2f} µg/m³")
with col2:
    st.metric("Minimum PM2.5", f"{df['pm25_value'].min():.2f} µg/m³")
with col3:
    st.metric("Average PM2.5", f"{df['pm25_value'].mean():.2f} µg/m³")

# Section 5: I designed this gauge chart to show real-time PM2.5 levels for selected locations
st.header("5. PM2.5 Gauge for Selected Location")
selected_location_data = df[df['location'] == selected_country]['pm25_value'].mean()

fig_gauge = go.Figure(go.Indicator(
    mode = "gauge+number",
    value = selected_location_data,
    domain = {'x': [0, 1], 'y': [0, 1]},
    title = {'text': f"PM2.5 Level in {selected_country}"},
    gauge = {
        'axis': {'range': [None, 200]},
        'steps': [
            {'range': [0, 50], 'color': "lightgreen"},
            {'range': [50, 100], 'color': "yellow"},
            {'range': [100, 200], 'color': "red"}
        ],
        'threshold': {
            'line': {'color': "red", 'width': 4},
            'thickness': 0.75,
            'value': 100
        }
    }
))
st.plotly_chart(fig_gauge, use_container_width=True)

# Section 6: I implemented this alert system to highlight dangerous pollution levels
st.header("6. Air Quality Alerts")
critical_locations = df[df['pm25_value'] > 100][['location', 'pm25_value', 'datetime_utc']].drop_duplicates()

if not critical_locations.empty:
    st.error("⚠️ Critical PM2.5 Levels Detected!")
    for _, row in critical_locations.iterrows():
        st.warning(
            f"Location: {row['location']}\n"
            f"PM2.5 Level: {row['pm25_value']:.2f} µg/m³\n"
            f"Time: {row['datetime_utc']}"
        )
else:
    st.success("✅ No critical PM2.5 levels detected in any location") 