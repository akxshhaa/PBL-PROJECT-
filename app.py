import streamlit as st
import preprocessor
import helper
import matplotlib.pyplot as plt
import seaborn as sns
import pandas as pd

st.sidebar.title("whatsapp chat analyser")
uploaded_file = st.sidebar.file_uploader("Choose a file")

if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    data = bytes_data.decode("utf-8")
    st.text(data)
    df = preprocessor.preprocess(data)


    if 'date' not in df.columns or not pd.api.types.is_datetime64_any_dtype(df['date']):
        df['date'] = pd.to_datetime(df.get('date', df.iloc[:, 0]), errors='coerce')
    if 'year' not in df.columns:
        df['year'] = df['date'].dt.year
    if 'month_num' not in df.columns:
        df['month_num'] = df['date'].dt.month
    if 'month' not in df.columns:
        df['month'] = df['date'].dt.month_name()
    if 'only_date' not in df.columns:
        df['only_date'] = df['date'].dt.date
    if 'day_name' not in df.columns:
        df['day_name'] = df['date'].dt.day_name()

    st.dataframe(df)
    user_list = df['user'].unique().tolist()
    if 'group_notification' in user_list:
        user_list.remove('group_notification')
    user_list.sort()
    user_list.insert(0, "Overall")

    selected_user = st.sidebar.selectbox("Show analysis for", user_list)

    if st.sidebar.button("Show Analysis"):

        # Top Stats
        num_messages, words, num_media_messages, num_links = helper.fetch_stats(selected_user, df)
        st.title("Top Statistics")
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.header("Total Messages")
            st.title(num_messages)
        with col2:
            st.header("Total Words")
            st.title(words)
        with col3:
            st.header("Media Shared")
            st.title(num_media_messages)
        with col4:
            st.header("Links Shared")
            st.title(num_links)

        # Monthly Timeline
        st.title("Monthly Timeline")
        timeline = helper.monthly_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(timeline['time'], timeline['message'], color='green', marker='o')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # Daily Timeline
        st.title("Daily Timeline")
        daily_timeline = helper.daily_timeline(selected_user, df)
        fig, ax = plt.subplots()
        ax.plot(daily_timeline['only_date'], daily_timeline['message'], color='black', marker='o')
        plt.xticks(rotation='vertical')
        st.pyplot(fig)

        # Activity Map
        st.title('Activity Map')
        col1, col2 = st.columns(2)

        with col1:
            st.header("Most busy day")
            try:
                busy_day = helper.week_activity_map(selected_user, df)
            except Exception:
                busy_day = df['day_name'].value_counts()
            order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
            busy_day = busy_day.reindex(order).fillna(0)
            fig, ax = plt.subplots()
            ax.bar(busy_day.index, busy_day.values, color='purple')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)

        with col2:
            st.header("Most busy month")
            busy_month = helper.month_activity_map(selected_user, df)
            fig, ax = plt.subplots()
            ax.bar(busy_month.index, busy_month.values, color='orange')
            plt.xticks(rotation='vertical')
            st.pyplot(fig)


        st.title("Weekly Activity Map (Heatmap)")
        if 'date' not in df.columns or not pd.api.types.is_datetime64_any_dtype(df['date']):
            df['date'] = pd.to_datetime(df.get('date', df.iloc[:, 0]), errors='coerce')
        if 'hour' not in df.columns:
            df['hour'] = df['date'].dt.hour

        def _make_period(h):
            try:
                h = int(h)
                return f"{h}-{(h+1)%24}"
            except Exception:
                return "Unknown"

        if 'period' not in df.columns:
            df['period'] = df['hour'].apply(_make_period)

        try:
            user_heatmap = helper.activity_heatmap(selected_user, df)
            if user_heatmap is None:
                raise ValueError("helper returned None")
        except Exception:
            user_heatmap = df.pivot_table(index='day_name', columns='period',
                                          values='message', aggfunc='count').fillna(0)

        weekday_order = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
        if isinstance(user_heatmap, pd.DataFrame):
            common_days = [d for d in weekday_order if d in user_heatmap.index]
            if common_days:
                user_heatmap = user_heatmap.reindex(common_days).fillna(0)

        fig, ax = plt.subplots()
        sns.heatmap(user_heatmap, ax=ax)
        plt.xticks(rotation='vertical')
        st.pyplot(fig)


        st.title('Most Common Words')
        try:
            most_common_df = helper.most_common_words(selected_user, df)
        except FileNotFoundError:
            import re
            words_list = []
            for message in df['message']:
                words_list.extend(re.findall(r'\b\w+\b', str(message).lower()))
            from collections import Counter
            most_common_df = pd.DataFrame(Counter(words_list).most_common(20))

        fig, ax = plt.subplots()
        ax.barh(most_common_df[0], most_common_df[1])
        plt.xticks(rotation='vertical')
        st.pyplot(fig)


