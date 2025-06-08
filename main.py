import numpy as np
import streamlit as st
import pandas as pd
import requests
import dotenv
import os

#____________________________KEYS_____________________________________________________________________________
dotenv.load_dotenv()
api_key = os.getenv("TASTEDIVE_KEY")


#_______________________PAGE SETUP____________________________________________________________________________________________
st.set_page_config(page_title="TasteDive Explorer", layout="wide", page_icon="🎬")
st.title("TasteDive Explorer Page 🎶")
st.subheader("Discover similar music, books, shows, or movies!")

#_______________________SIDE BAR______________________________________________________________________________________________
st.sidebar.title("Find Similar Recommendations 😁")

content_type = st.sidebar.radio("Choose a category", options=["music", "movie", "show", "book", "author", "game"])

st.sidebar.divider()

query = st.sidebar.text_input("What do you want recommendations for?", placeholder="e.g., Bruno Mars, Stranger Things")

result_limit = st.sidebar.slider("Number of recommendations", 1, 10, 5)

show_urls = st.sidebar.checkbox("Show URLs in table")

map_button = st.sidebar.button("Generate Map Points")

st.sidebar.divider()

st.sidebar.info("This website is powered by TasteDive API")


#__________________________TABS______________________________________________________________________________________________
tab1, tab2, tab3, tab4 = st.tabs(["Results", "Table", "Bar Chart", "Map"])


def get_recommendations(q, content_type, limit, key):
    url = "https://tastedive.com/api/similar"
    params = {"q": q,"type": content_type, "limit": limit, "k": key, "info": 1}
    response = requests.get(url, params=params).json()
    return response


if query:
    data = get_recommendations(query, content_type, result_limit, api_key)

    if "similar" in data and data["similar"]["results"]:
        recs = data["similar"]["results"]
        df = pd.DataFrame(recs)
        df["name_length"] = df["name"].apply(len)

        #_______________________TABS____________________________________________________________________________
        with tab1:
            st.success(f"Found {len(recs)} recommendations for **{query}** in *{content_type}*.")
            for item in recs:
                st.markdown(f"### 🎬 {item['name']}")
                if item.get("wUrl"):
                    st.markdown(f"[More info →]({item['wUrl']})", unsafe_allow_html=True)
                if item.get("yUrl"):
                    st.video(item["yUrl"])
                st.divider()

        with tab2:
            st.subheader("Recommendation Table")
            if show_urls:
                st.dataframe(df[["name", "wUrl", "yUrl"]])
            else:
                st.dataframe(df[["name"]])

        with tab3:
            st.subheader("YouTube Link Availability")
            df["has_youtube"] = df["yUrl"].notna()
            yt_counts = df["has_youtube"].value_counts()
            yt_df = pd.DataFrame({
                "YouTube Link": ["Available", "Not Available"],
                "Count": [yt_counts.get(True, 0), yt_counts.get(False, 0)]
            })
            st.bar_chart(yt_df.set_index("YouTube Link"))

        with tab4:
            st.subheader("Simulated Map of Recommendations")
            if map_button:
                coords = pd.DataFrame({
                    "lat": np.random.uniform(25.5, 26.5, len(recs)),
                    "lon": np.random.uniform(-80.5, -79.5, len(recs))
                })
                st.map(coords)
            else:
                st.info("Click the 'Generate Map Points' button in the sidebar to display the map.")

    else:
        st.warning(f"No recommendations found for **{query}** in *{content_type}*.")
else:
    st.info("Please enter a search term in the sidebar to begin.")