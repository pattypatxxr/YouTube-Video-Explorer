import matplotlib.ticker as ticker
import streamlit as st
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from googleapiclient.discovery import build

# Set Streamlit app configuration
st.set_page_config(page_title="YouTube Video Explorer", layout="centered")

# Title and description
st.title("📺 YouTube Video Explorer")
st.markdown("Search for YouTube videos and explore their metadata!")

# User input for API key (hidden as password)
api_key = st.text_input("🔑 Enter your YouTube Data API Key", type="password")

# Input for search query and number of results to retrieve
query = st.text_input("🔍 Search Query (e.g. 'education')")

# Slider for how many results to fetch (from 5 to 50 videos)
max_results = st.slider("Max Results", 5, 50, 10)

# Main logic: when the "Search" button is clicked and valid inputs are given
if st.button("Search") and api_key and query:
    try:
        # Initialize YouTube API client
        youtube = build("youtube", "v3", developerKey=api_key)

        # Search for videos based on the query
        request = youtube.search().list(
            q=query,
            part="snippet",
            type="video",
            maxResults=max_results
        )
        response = request.execute()

        # Extract video IDs from the search response
        video_ids = [item["id"]["videoId"] for item in response["items"]]
        # Use the video IDs to request detailed video statistics and metadata
        video_request = youtube.videos().list(
            part="statistics,snippet",
            id=",".join(video_ids)
        )
        video_response = video_request.execute()

        # Parse the response and collect data into a list of dictionaries
        videos = []
        for item in video_response["items"]:
            stats = item["statistics"]
            snippet = item["snippet"]
            videos.append({
                "video_id": item["id"],
                "title": snippet["title"],
                "channel": snippet["channelTitle"],
                "publish_time": snippet["publishedAt"],
                "views": int(stats.get("viewCount", 0)),
                "likes": int(stats.get("likeCount", 0)),
                "comments": int(stats.get("commentCount", 0))
            })

        # Create a pandas DataFrame from the list of video data
        df = pd.DataFrame(videos)

        # Convert views, likes, comments to numeric
        df['views'] = pd.to_numeric(df['views'], errors='coerce')
        df['likes'] = pd.to_numeric(df['likes'], errors='coerce')
        df['comments'] = pd.to_numeric(df['comments'], errors='coerce')

        # Convert publish timestamp into datetime format
        df['publish_time'] = pd.to_datetime(df['publish_time'])

        # Extract time-based features from publish time
        df['publish_hour'] = df['publish_time'].dt.hour
        df['publish_day'] = df['publish_time'].dt.day_name()
        df['publish_month'] = df['publish_time'].dt.month

        df[['views', 'likes', 'comments']].describe()

        # Convert publish_hour to numeric(for plotting)
        df['publish_hour'] = pd.to_numeric(df['publish_hour'], errors='coerce')

        # Drop rows with missing views or publish_hour
        df = df.dropna(subset=['publish_hour', 'views'])

        # Notify user of successful retrieval
        st.success(f"Retrieved {len(df)} videos!")
        st.write(df)

        # ===============================
        # Visualization Section
        # ===============================

        # === Scatter plot: Likes vs Views ===
        # Shows how the number of likes relates to number of views for each video.
        # Helpful to see if videos with more likes also get more views.
        st.subheader("📊 Likes vs Views")
        fig1, ax1 = plt.subplots(figsize=(10, 5))
        sns.scatterplot(data=df, x='likes', y='views', ax=ax1)
        ax1.set_title("Likes vs Views")
        st.pyplot(fig1)

        # === Box plot: Views by Day of the Week ===
        # This chart compares the distribution of view counts for each day of the week.
        # We can see which days tend to have higher or more consistent views.
        st.subheader("📅 Views by Publish Day")
        fig2, ax2 = plt.subplots(figsize=(10, 5))
        day_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        sns.boxplot(x='publish_day', y='views', data=df, order=day_order, ax=ax2)
        ax2.set_title("Views by Day of the Week")
        ax2.set_xticklabels(ax2.get_xticklabels(), rotation=45)
        st.pyplot(fig2)

        # === Line plot: Average Views by Hour ===
        # This graph shows the average number of views based on what hour a video was published.
        # Helps identify the best time of day to publish videos.
        st.subheader("⏰ Views by Publish Hour")
        hour_labels = [f"{h % 12 or 12}{'AM' if h < 12 else 'PM'}" for h in range(24)]
        hourly_views = df.groupby('publish_hour')['views'].agg(['mean']).reset_index()

        fig3, ax3 = plt.subplots(figsize=(10, 5))
        sns.lineplot(x='publish_hour', y='mean', data=hourly_views, label='Mean', ax=ax3, marker='o')

        ax3.set_title("Average Views by Publish Hour")
        ax3.set_xlabel("Publish Hour")
        ax3.set_ylabel("Views")
        ax3.set_xticks(range(24))
        ax3.set_xticklabels(hour_labels, rotation=45)
        ax3.legend()
        st.pyplot(fig3)


        # === Heatmap: Correlation of Engagement Metrics ===
        # This heatmap shows the correlation between views, likes, and comments.
        # Helps identify which metrics are strongly related (positive or negative).
        st.subheader("📊 Correlation Heatmap of Engagement Metrics")
        fig4, ax4 = plt.subplots(figsize=(8, 6))
        corr = df[['views', 'likes', 'comments']].corr()
        sns.heatmap(corr, annot=True, cmap='coolwarm', fmt='.2f', ax=ax4)
        st.pyplot(fig4)


    # Handle any exceptions during API request or plotting
    except Exception as e:
        st.error(f"Error: {e}")
