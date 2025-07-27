import streamlit as st
import pandas as pd
import altair as alt
import requests
import time

API_BASE_URL = "http://localhost:8000"

def count_come_in_per_day(customers):
    try:
        df = pd.DataFrame(customers)
    except Exception as e:
        print("Lỗi tạo DataFrame:", e)
        return pd.DataFrame(columns=["Date", "Come in"])

    if df.empty or "come_in" not in df.columns:
        return pd.DataFrame(columns=["Date", "Come in"])

    # Chuyển datetime và đếm
    df["Date"] = pd.to_datetime(df["come_in"], errors="coerce").dt.date
    result = df.groupby("Date").size().reset_index(name="Come in")

    # Bổ sung các ngày bị thiếu
    if not result.empty:
        today = pd.Timestamp.today().normalize()
        all_dates = pd.date_range(result["Date"].min(), today)
        result = result.set_index("Date").reindex(all_dates, fill_value=0)
        result.index.name = "Date"
        result = result.reset_index()
        result.columns = ["Date", "Come in"]
        
    return result

def count_total_age_groups(customers):
    try:
        df = pd.DataFrame(customers)
    except Exception as e:
        print("Lỗi tạo DataFrame:", e)
        return pd.DataFrame(columns=["Age Group", "Count"])
    
    if df.empty or "age_group" not in df.columns:
        return pd.DataFrame(columns=["Age Group", "Count"])

    df["Age Group"] = df["age_group"]
    age_order = ["Children", "Teen", "Adult", "Elderly"]
    counts = df["Age Group"].value_counts().reindex(age_order, fill_value=0)

    return pd.DataFrame({"Age Group": counts.index, "Count": counts.values})

def count_age_group_per_day(customers):
    try:
        df = pd.DataFrame(customers)
    except Exception as e:
        print("Lỗi tạo DataFrame:", e)
        return pd.DataFrame(columns=["Date", "Children", "Teen", "Adult", "Elderly"])
    
    if df.empty or not {"come_in", "age_group"}.issubset(df.columns):
        return pd.DataFrame(columns=["Date", "Children", "Teen", "Adult", "Elderly"])

    # Tạo result
    df["Date"] = pd.to_datetime(df["come_in"], errors="coerce").dt.date
    df["Age Group"] = df["age_group"]

    grouped = df.groupby(["Date", "Age Group"]).size().unstack(fill_value=0)
    for col in ["Children", "Teen", "Adult", "Elderly"]:
        if col not in grouped.columns:
            grouped[col] = 0
    grouped = grouped[["Children", "Teen", "Adult", "Elderly"]].reset_index()
    
    # Bổ sung các ngày bị thiếu (đảm bảo đến hôm qua)
    if not grouped.empty:
        today = pd.Timestamp.today().normalize()
        yesterday = today - pd.Timedelta(days=1)
        all_dates = pd.date_range(grouped["Date"].min(), yesterday)
        grouped = grouped.set_index("Date").reindex(all_dates, fill_value=0)
        grouped.index.name = "Date"
        grouped = grouped.reset_index()
        grouped["Date"] = pd.to_datetime(grouped["Date"])
        grouped = grouped[grouped["Date"] <= yesterday].sort_values("Date").tail(10)
        grouped = grouped[["Date", "Children", "Teen", "Adult", "Elderly"]]
        
    return grouped

def get_sound_history():
    """Lấy tất cả lịch sử sử dụng âm thanh"""
    try:
        response = requests.get(f"{API_BASE_URL}/get-sound-history")
        if response.status_code == 200:
            return response.json().get("history", [])
        else:
            st.error(f"Lỗi lấy lịch sử: {response.text}")
            return []
    except Exception as e:
        st.error(f"Lỗi kết nối API: {e}")
        return []

def display_sound_history():
    """Hiển thị lịch sử sử dụng âm thanh"""
    st.header("📋 Audio Usage Statistics")

    # Tạo tabs để phân chia hiển thị
    tab1, tab2, tab3 = st.tabs(["📊 All History", "👤 Filter by User", "🎵 Filter by Sound Clip"])

    with tab1:
        history_data = get_sound_history()
        if history_data:
            # Tạo DataFrame
            df = pd.DataFrame(history_data)
            
            # Hiển thị thống kê tổng quan
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Usage", len(history_data))
            with col2:
                unique_users = df['user_name'].nunique()
                st.metric("Number of Users", unique_users)
            with col3:
                if len(history_data) > 0:
                    most_used = df['sound_name'].value_counts().index[0]
                    st.metric("Most Used Sound", most_used)

            # Hiển thị bảng lịch sử với sorting options
            st.write("**Historical Details:**")
            
            # Thêm options để sort
            col_sort, col_order = st.columns([2, 1])
            with col_sort:
                sort_column = st.selectbox(
                    "Sort by:",
                    ["Default", "User", "Sound Clip", "Timestamp"],
                    key="sort_column_all"
                )
            with col_order:
                sort_ascending = st.selectbox(
                    "Order:",
                    ["Ascending", "Descending"],
                    key="sort_order_all"
                ) == "Ascending"

            # Chuẩn bị DataFrame để hiển thị
            display_df = df[['user_name', 'sound_name', 'timestamp']].copy()
            display_df.columns = ['User', 'Sound Clip', 'Timestamp']

            # Thực hiện sort trên toàn bộ dữ liệu trước khi phân trang
            if sort_column != "Default":
                if sort_column == "Timestamp":
                    # Convert timestamp to datetime for proper sorting
                    display_df['Timestamp'] = pd.to_datetime(display_df['Timestamp'])

                display_df = display_df.sort_values(
                    by=sort_column, 
                    ascending=sort_ascending
                )
            
            # Reset index sau khi sort
            display_df.reset_index(drop=True, inplace=True)
            display_df.index = display_df.index + 1
            display_df.index.name = 'STT'
            
            # Hiển thị với pagination
            items_per_page = 10
            total_items = len(display_df)
            total_pages = (total_items - 1) // items_per_page + 1
            
            if total_pages > 1:
                page = st.selectbox("Choose page:", range(1, total_pages + 1), key="history_page")
                start_idx = (page - 1) * items_per_page
                end_idx = start_idx + items_per_page
                
                # Hiển thị với index bắt đầu từ số thứ tự thực tế
                page_df = display_df.iloc[start_idx:end_idx].copy()
                
                # Adjust index to show correct row numbers for current page
                page_df.index = range(start_idx + 1, min(end_idx + 1, total_items + 1))
                page_df.index.name = 'STT'
                
                st.dataframe(page_df, use_container_width=True)
                st.write(f"Showing {start_idx + 1}-{min(end_idx, total_items)} of {total_items} records")
            else:
                st.dataframe(display_df, use_container_width=True)
        else:
            st.info("No usage history available.")

    with tab2:
        # Lấy danh sách tất cả user để filter
        all_history = get_sound_history()
        if all_history:
            all_users = list(set([record['user_name'] for record in all_history]))
            selected_user = st.selectbox("Choose user:", ["All"] + sorted(all_users), key="user_filter")

            if selected_user != "All":
                user_history = [record for record in all_history if record['user_name'] == selected_user]
                if user_history:
                    df_user = pd.DataFrame(user_history)
                    
                    # Thêm sorting cho tab user
                    col_sort_user, col_order_user = st.columns([2, 1])
                    with col_sort_user:
                        sort_column_user = st.selectbox(
                            "Sort by:",
                            ["Default", "Sound Clip", "Timestamp"],
                            key="sort_column_user"
                        )
                    with col_order_user:
                        sort_ascending_user = st.selectbox(
                            "Order:",
                            ["Ascending", "Descending"],
                            key="sort_order_user"
                        ) == "Ascending"

                    display_df_user = df_user[['sound_name', 'timestamp']].copy()
                    display_df_user.columns = ['Sound Clip', 'Timestamp']

                    # Sort if needed
                    if sort_column_user != "Default":
                        if sort_column_user == "Timestamp":
                            display_df_user['Timestamp'] = pd.to_datetime(display_df_user['Timestamp'])

                        display_df_user = display_df_user.sort_values(
                            by=sort_column_user, 
                            ascending=sort_ascending_user
                        )
                    
                    # Thêm cột STT bắt đầu từ 1
                    display_df_user.reset_index(drop=True, inplace=True)
                    display_df_user.index = display_df_user.index + 1
                    display_df_user.index.name = 'STT'

                    st.write(f"**History of {selected_user}:**")
                    st.dataframe(display_df_user, use_container_width=True)

                    # Statistics for this user
                    st.write("**Statistics:**")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Total Usage", len(user_history))
                    with col2:
                        if len(user_history) > 0:
                            most_used_by_user = df_user['sound_name'].value_counts().index[0]
                            st.metric("Most Used Sound", most_used_by_user)
                else:
                    st.info(f"User {selected_user} has no usage history.")
            else:
                st.info("Please select a specific user to view history.")
        else:
            st.info("No history data available to filter.")

    with tab3:
        # Lọc theo bản ghi âm
        all_history = get_sound_history()
        if all_history:
            all_sounds = list(set([record['sound_name'] for record in all_history]))
            selected_sound = st.selectbox("Select Sound:", ["All"] + sorted(all_sounds), key="sound_filter")

            if selected_sound != "All":
                sound_history = [record for record in all_history if record['sound_name'] == selected_sound]
                if sound_history:
                    df_sound = pd.DataFrame(sound_history)
                    
                    # Thêm sorting cho tab sound
                    col_sort_sound, col_order_sound = st.columns([2, 1])
                    with col_sort_sound:
                        sort_column_sound = st.selectbox(
                            "Sort by:",
                            ["Default", "User", "Timestamp"],
                            key="sort_column_sound"
                        )
                    with col_order_sound:
                        sort_ascending_sound = st.selectbox(
                            "Order:",
                            ["Ascending", "Descending"],
                            key="sort_order_sound"
                        ) == "Ascending"

                    display_df_sound = df_sound[['user_name', 'timestamp']].copy()
                    display_df_sound.columns = ['User', 'Timestamp']

                    # Sort if needed
                    if sort_column_sound != "Default":
                        if sort_column_sound == "Timestamp":
                            display_df_sound['Timestamp'] = pd.to_datetime(display_df_sound['Timestamp'])

                        display_df_sound = display_df_sound.sort_values(
                            by=sort_column_sound, 
                            ascending=sort_ascending_sound
                        )
                    
                    # Thêm cột STT bắt đầu từ 1
                    display_df_sound.reset_index(drop=True, inplace=True)
                    display_df_sound.index = display_df_sound.index + 1
                    display_df_sound.index.name = 'STT'

                    st.write(f"**History of Sound: {selected_sound}**")
                    st.dataframe(display_df_sound, use_container_width=True)

                    # Statistics for this sound
                    st.write("**Statistics:**")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Total Plays", len(sound_history))
                    with col2:
                        unique_users_for_sound = df_sound['user_name'].nunique()
                        st.metric("Total Users", unique_users_for_sound)
                    with col3:
                        if len(sound_history) > 0:
                            most_active_user = df_sound['user_name'].value_counts().index[0]
                            st.metric("Most Active User", most_active_user)

                    # User statistics chart
                    st.write("**User Statistics:**")
                    user_counts = df_sound['user_name'].value_counts()
                    st.bar_chart(user_counts)
                else:
                    st.info(f"Sound {selected_sound} has not been used.")
            else:
                st.info("Please select a specific sound to view statistics.")
        else:
            st.info("No history data available to filter.")

def display_charts():
    st.header("📈 Biểu Đồ Mẫu")

    tab1, tab2, tab3 = st.tabs(["📈 Customer per day", "🥧 Age group overview", "📊 Customer age group"])

    # TAB 1: Realtime fetch mỗi 5s
    with tab1:
        if "last_fetch_tab1" not in st.session_state:
            st.session_state.last_fetch_tab1 = 0
        if time.time() - st.session_state.last_fetch_tab1 > 20 or "dataCos_tab1" not in st.session_state:
            res = requests.get("http://localhost:8000/get-info-customers")
            if res.status_code == 200:
                st.session_state.dataCos_tab1 = res.json().get("customers", [])
            else:
                st.session_state.dataCos_tab1 = []
            st.session_state.last_fetch_tab1 = time.time()
            st.rerun()
        df1 = count_come_in_per_day(st.session_state.get("dataCos_tab1", []))
        if not df1.empty:
            df1["Date"] = pd.to_datetime(df1["Date"])

            # Tạo vùng tương tác: kéo chọn, zoom, pan
            zoom = alt.selection_interval(bind='scales')  # Zoom cả chiều ngang và dọc

            # Biểu đồ đường
            line = alt.Chart(df1).mark_line(color="steelblue").encode(
                x=alt.X("Date:T"),
                y=alt.Y("Come in:Q"),
                tooltip=["Date:T", "Come in"]
            )

            # Các điểm đỏ
            points = alt.Chart(df1).mark_point(filled=True, color="red", size=60).encode(
                x="Date:T",
                y="Come in:Q",
                tooltip=["Date:T", "Come in"]
            )

            # Gộp biểu đồ và thêm vùng tương tác
            chart = alt.layer(line, points).add_params(zoom).properties(
                width=700,
                height=400
            )

            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("No customer data available to display")

    with tab2:
        now = time.strftime("%H:%M")
        if "last_fetch_tab2" not in st.session_state:
            st.session_state.last_fetch_tab2 = ""
        if "dataCos_tab2" not in st.session_state:
            st.session_state.dataCos_tab2 = []

        # Tự động fetch lúc 23:00
        if now == "23:00" and st.session_state.last_fetch_tab2 != time.strftime("%d/%m/%Y"):
            res_pie = requests.get("http://localhost:8000/get-info-customers")
            if res_pie.status_code == 200:
                st.session_state.dataCos_tab2 = res_pie.json().get("customers", [])
                st.session_state.last_fetch_tab2 = time.strftime("%d/%m/%Y")

        # Nếu chưa có thì lấy từ tab1 (cache lại)
        data_tab2 = st.session_state.get("dataCos_tab2", [])
        if not data_tab2 and "dataCos_tab1" in st.session_state:
            data_tab2 = st.session_state["dataCos_tab1"]

        df2 = count_total_age_groups(data_tab2)
        
        if not df2.empty and df2["Count"].sum() > 0:
            total = df2["Count"].sum()
            df2["Percent"] = (df2["Count"] / total * 100).round(2)

            age_order = ["Children", "Teen", "Adult", "Elderly"]
            color_scale = alt.Scale(domain=age_order,
                                    range=["#1f77b4", "#2ca02c", "#f1c40f", "#d62728"])

            base = alt.Chart(df2).encode(
                theta=alt.Theta("Count:Q"),
                color=alt.Color("Age Group:N", 
                               scale=color_scale)
            )

            pie = base.mark_arc(innerRadius=50, outerRadius=130).encode(
                tooltip=["Age Group:N", "Count:Q", alt.Tooltip("Percent:Q", format=".2f", title="Percent (%)")]
            )

            chart = pie.properties(
                width=500,
                height=400,
                title="Proportion of total population by age group"
            )

            st.altair_chart(chart, use_container_width=True)
        else:
            st.info("No age group data available to display")

   
    # TAB 3: Chỉ fetch lại lúc 23:00 hoặc khi bấm nút
    with tab3:
        now = time.strftime("%H:%M")
        if "last_fetch_tab3" not in st.session_state:
            st.session_state.last_fetch_tab3 = ""
        if "dataCos_tab3" not in st.session_state:
            st.session_state.dataCos_tab3 = []
        # Tự động cập nhật lúc 23:00
        if now == "23:00" and st.session_state.last_fetch_tab3 != time.strftime("%d/%m/%Y"):
            res3 = requests.get("http://localhost:8000/get-info-customers")
            if res3.status_code == 200:
                st.session_state.dataCos_tab3 = res3.json().get("customers", [])
                st.session_state.last_fetch_tab3 = time.strftime("%d/%m/%Y")
        # Nếu chưa có dữ liệu tab3, lấy từ tab1 (lần fetch đầu tiên)
        data_tab3 = st.session_state.get("dataCos_tab3", [])
        if not data_tab3 and "dataCos_tab1" in st.session_state:
            data_tab3 = st.session_state["dataCos_tab1"]
        df3 = count_age_group_per_day(data_tab3)
        # st.write(df2)
        if not df3.empty:
            # Chỉ lấy 10 ngày gần nhất để vẽ biểu đồ (nếu chưa lấy ở hàm xử lý)
            df_melted = df3.melt(id_vars="Date", value_vars=["Children", "Teen", "Adult", "Elderly"],
                                var_name="Age Group", value_name="Count")

            age_order = ["Children", "Teen", "Adult", "Elderly"]
            color_scale = alt.Scale(domain=age_order,
                                    range=["#1f77b4", "#2ca02c", "#f1c40f", "#d62728"])  # bạn có thể tùy chỉnh màu

            chart = alt.Chart(df_melted).mark_bar().encode(
                x=alt.X("Date:T", 
                        title="Date",
                        axis=alt.Axis(
                            format="%b %d",  # Chỉ hiển thị tháng và ngày
                            labelAngle=0,  # Nghiêng nhãn để dễ đọc
                            tickCount=10     # Số lượng tick cố định
                        )),
                y=alt.Y("Count:Q", stack="zero", title="Come in"),
                color=alt.Color("Age Group:N",
                                scale=color_scale,
                                legend=alt.Legend(orient="bottom", title=None)),
                tooltip=["Date:T", "Age Group:N", "Count:Q"]
            ).properties(
                width=700,
                height=400,
            )

            st.altair_chart(chart, use_container_width=True)           

        else:
            st.info("No customer data available to display")

# Hiển thị thống kê âm thanh
display_sound_history()
    
st.divider()

# Hiển thị biểu đồ mẫu (tùy chọn)
display_charts()
