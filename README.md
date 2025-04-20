# YouTube-Video-Explorer

A data science project that analyzes popular YouTube videos using the **YouTube Data API v3**.  
This interactive dashboard helps users explore trends in video popularity, such as engagement metrics and optimal upload times.

## 🎯 Project Goal

To identify what makes certain YouTube videos more popular than others by analyzing:
- Views
- Likes
- Comments
- Publish day and hour

## 🔍 Key Features

- ✅ Real-time data fetching based on keyword search (e.g., “gaming”, “education”)
- ✅ Interactive Streamlit dashboard
- ✅ Visualizations:
  - Scatter plot: Likes vs. Views
  - Box plot: Views by Publish Day
  - Line chart: Views by Publish Hour
  - Correlation heatmap: Views, Likes, Comments
  - Metadata Table with publish date/hour

## 🚀 How to Run the App

1. Clone this repository

2. Install dependencies
> pip install -r requirements.txt

3. Run the Streamlit app
> streamlit run app.py

4. Enter your YouTube Data API key when prompted in the dashboard.
