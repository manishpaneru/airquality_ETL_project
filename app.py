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

# Section 6: I implemented this detailed alert system with multiple trigger levels
st.header("6. Air Quality Alerts")

# I defined these PM2.5 trigger levels based on standard air quality guidelines
def get_air_quality_status(pm25_value):
    if pm25_value <= 12:
        return "Good", "Air quality is satisfactory, and air pollution poses little or no risk.", "✅"
    elif pm25_value <= 35.4:
        return "Moderate", "Air quality is acceptable; however, some pollutants may cause moderate health concerns for a very small number of people.", "⚠️"
    elif pm25_value <= 55.4:
        return "Unhealthy for Sensitive Groups", "Members of sensitive groups may experience health effects, but the general public is less likely to be affected.", "⚠️"
    elif pm25_value <= 150.4:
        return "Unhealthy", "Everyone may begin to experience health effects; members of sensitive groups may experience more serious health effects.", "🚨"
    elif pm25_value <= 250.4:
        return "Very Unhealthy", "Health warnings of emergency conditions. The entire population is more likely to be affected.", "🚨"
    else:
        return "Hazardous", "Health alert: everyone may experience more serious health effects.", "☠️"

# I get the current PM2.5 value for the selected location
current_location_data = df[df['location'] == selected_country]['pm25_value'].mean()
status, description, icon = get_air_quality_status(current_location_data)

# I create an expander to show the general PM2.5 trigger levels
with st.expander("ℹ️ PM2.5 Trigger Levels Information", expanded=True):
    st.markdown("""
    | Level | PM2.5 Range (µg/m³) | Health Implications |
    |-------|---------------------|-------------------|
    | Good | 0 - 12 | Air quality is satisfactory |
    | Moderate | 12.1 - 35.4 | Acceptable air quality |
    | Unhealthy for Sensitive Groups | 35.5 - 55.4 | May affect sensitive individuals |
    | Unhealthy | 55.5 - 150.4 | Everyone may experience effects |
    | Very Unhealthy | 150.5 - 250.4 | Emergency health effects |
    | Hazardous | > 250.4 | Serious health alert |
    """)

# I display the current alert status for the selected location
st.subheader(f"Current Alert Status for {selected_country}")
alert_color = "green" if status == "Good" else "orange" if status in ["Moderate", "Unhealthy for Sensitive Groups"] else "red"
st.markdown(f"<div style='padding: 20px; border-radius: 10px; background-color: {alert_color}; color: white;'>"
           f"<h3 style='margin:0'>{icon} Current Status: {status}</h3>"
           f"<p style='margin:10px 0 0 0'>PM2.5 Level: {current_location_data:.1f} µg/m³</p>"
           f"<p style='margin:10px 0 0 0'>{description}</p>"
           "</div>", unsafe_allow_html=True)

# I show critical alerts for all locations
st.subheader("Critical Alerts Across All Locations")
critical_locations = df[df['pm25_value'] > 55.4][['location', 'pm25_value', 'datetime_utc']].drop_duplicates()

if not critical_locations.empty:
    for _, row in critical_locations.iterrows():
        status, description, icon = get_air_quality_status(row['pm25_value'])
        st.warning(
            f"{icon} Location: {row['location']}\n"
            f"Status: {status}\n"
            f"PM2.5 Level: {row['pm25_value']:.1f} µg/m³\n"
            f"Time: {row['datetime_utc']}\n"
            f"Advisory: {description}"
        )
else:
    st.success("✅ No critical PM2.5 levels detected in any location") 