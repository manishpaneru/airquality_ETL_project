# 🌍 Air Quality Live Analysis Project

## Author
**Manish Paneru**  
*Data Analyst*

## 🎯 Project Overview
This project implements a real-time air quality monitoring and analysis system using the OpenAQ API. It follows a modern ETL (Extract, Transform, Load) architecture and presents the data through an interactive dashboard built with Streamlit.

## 🛠️ Technical Skills & Tools Used
- **Python Programming**
  - Data manipulation with Pandas
  - Data visualization with Plotly
  - API integration with Requests
  - Database management with SQLite
- **ETL Pipeline Development**
  - Data extraction from OpenAQ API
  - Data transformation and cleaning
  - Data loading into SQLite database
- **Data Visualization**
  - Interactive charts with Plotly
  - Geospatial visualization
  - Real-time data updates
- **Web Application Development**
  - Streamlit for dashboard creation
  - Interactive user interface
  - Responsive design

## 🏗️ Project Architecture
The project is structured in three main components:

1. **Data Extraction (`openaq_etl.py`)**
   - Connects to OpenAQ API
   - Fetches real-time air quality data
   - Handles API authentication and rate limiting

2. **Data Processing**
   - Cleans and transforms raw data
   - Filters for PM2.5 measurements
   - Handles missing values and data validation
   - Standardizes data format

3. **Visualization Dashboard (`app.py`)**
   - Interactive data exploration
   - Multiple visualization types:
     - Bar charts for top polluted locations
     - Geographic distribution map
     - Real-time gauges and alerts
     - Ranked tables with color coding

## 📊 Key Features
1. **Real-time Air Quality Monitoring**
   - Live data updates from OpenAQ
   - PM2.5 concentration tracking
   - Geographic distribution analysis

2. **Interactive Visualizations**
   - Top polluted locations bar chart
   - Geographic heat map
   - Air quality rankings
   - Summary statistics
   - Location-specific gauge charts
   - Critical alerts system

3. **Data Analysis Capabilities**
   - Location-based filtering
   - Threshold-based alerts
   - Trend analysis
   - Comparative analysis

## 💡 Business Value & Applications
This project provides value in several scenarios:

1. **Environmental Monitoring**
   - Track air quality trends
   - Identify pollution hotspots
   - Monitor environmental compliance

2. **Public Health**
   - Assess health risks
   - Plan public health interventions
   - Issue timely warnings

3. **Urban Planning**
   - Inform policy decisions
   - Plan green spaces
   - Optimize traffic management

4. **Research & Analysis**
   - Study pollution patterns
   - Analyze seasonal variations
   - Assess intervention effectiveness

## 🚀 Getting Started

### Prerequisites
```bash
Python 3.8+
pip (Python package manager)
```

### Installation
1. Clone the repository
```bash
git clone [repository-url]
cd air-quality-analysis
```

2. Install required packages
```bash
pip install -r requirements.txt
```

3. Run the ETL process
```bash
python openaq_etl.py
```

4. Launch the dashboard
```bash
streamlit run app.py
```

## 🔄 Project Workflow
1. **Data Collection**
   - Regular API calls to OpenAQ
   - Data validation and error handling
   - Raw data storage

2. **Data Processing**
   - Cleaning and standardization
   - Feature extraction
   - Quality checks

3. **Data Visualization**
   - Interactive dashboard
   - Real-time updates
   - User-friendly interface

## 📈 Future Enhancements
- Integration with additional data sources
- Machine learning for prediction
- Mobile app development
- Advanced analytics features
- Historical data analysis
- Automated reporting system

## 🤝 Contributing
Feel free to fork this project and submit pull requests. For major changes, please open an issue first to discuss the proposed changes.

## 📝 License
This project is licensed under the MIT License - see the LICENSE file for details.

---
*Created with ❤️ by Manish Paneru* 