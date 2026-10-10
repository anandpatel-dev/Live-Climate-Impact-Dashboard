# 🌍 Live Climate Impact Dashboard

A Python-based climate monitoring and visualization project that brings together weather conditions, air quality data, and historical weather records for Indian cities.

The project uses Python for data collection and processing, SQLite for data storage, and Streamlit for interactive data visualization.

🌍 Live Demo

🚀[🚀 Open Live Climate Impact Dashboard](https://live-climate-impact-dashboard-ruxmeigczzusoeyq2ck9qf.streamlit.app/)

Explore live weather conditions, air quality metrics, historical climate data, and interactive visualizations across cities.

## 📌 Project Overview

The Live Climate Impact Dashboard aims to make climate-related data easier to explore through interactive charts, weather summaries, and air quality indicators.

It combines API-based weather and air quality data with historical weather records to help users understand environmental conditions and trends.

## ✨ Key Features

- **Weather Monitoring:** Fetch current weather conditions and forecast data.
- **Air Quality Monitoring:** Retrieve air quality indicators from an external API.
- **Historical Weather Analysis:** Work with historical weather records for trend analysis.
- **Interactive Dashboard:** Explore climate data using a Streamlit interface.
- **Data Processing:** Clean and prepare collected data using Python and Pandas.
- **Database Storage:** Store weather and air quality data in SQLite.
- **Visual Analytics:** Present climate information through charts and summaries.

## 🛠️ Technologies Used

- Python
- Streamlit
- Pandas
- SQLite
- Open-Meteo APIs
- Plotly (if used by the current dashboard)

## 📂 Project Structure

    text
Live_Climate_Impact_Dashboard/
├── app.py
├── assets/
├── data/
├── src/
│   ├── clean_and_store.py
│   ├── fetch_air_quality.py
│   ├── fetch_historical_weather.py
│   ├── fetch_weather.py
│   ├── store_air_quality.py
│   └── store_historical_weather.py
└── .gitignore


## ⚙️ Getting Started

### 1. Clone the repository

   bash
git clone https://github.com/anandpatel-dev/Live-Climate-Impact-Dashboard.git
cd Live-Climate-Impact-Dashboard


### 2. Create a virtual environment

    bash
python -m venv .venv


### 3. Activate the environment

**Windows — Command Prompt:**

  bash
.venv\Scripts\activate


**Windows — Git Bash:**

    bash
source .venv/Scripts/activate


### 4. Install dependencies

Install the packages required by the project. If a `requirements.txt` file is available, run:
  bash
pip install -r requirements.txt


Otherwise, install the required packages based on the imports used in the project files.

### 5. Run the dashboard

bash
python -m streamlit run app.py


Streamlit will provide a local URL in the terminal. Open that URL in your browser to access the dashboard.

## 📊 Data Sources

The project uses Open-Meteo APIs for weather forecasts and air quality information. Historical weather records are used for historical analysis.

## 🎯 Project Goals

- Practice real-world API data collection.
- Develop data cleaning and storage workflows.
- Build interactive climate visualizations.
- Strengthen Python and data analytics skills.
- Create a portfolio project demonstrating an end-to-end data workflow.

## 🚀 Future Improvements

- Automate scheduled data collection.
- Expand coverage to additional Indian cities.
- Improve historical trend analysis.
- Add clearer data freshness indicators.
- Enhance dashboard design and usability.

## 👨‍💻 Author

**Anand Patel**

GitHub: [anandpatel-dev](https://github.com/anandpatel-dev)



*This project is being developed as a hands-on data analytics portfolio project.*
