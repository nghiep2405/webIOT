import streamlit as st
import pandas as pd
import numpy as np
import altair as alt
import requests

API_BASE_URL = "http://localhost:8000"

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
    st.header("📋 Thống Kê Sử Dụng Âm Thanh")
    
    # Tạo tabs để phân chia hiển thị
    tab1, tab2, tab3 = st.tabs(["📊 Tất Cả Lịch Sử", "👤 Lọc Theo Người Dùng", "🎵 Lọc Theo Bản Ghi Âm"])
    
    with tab1:
        history_data = get_sound_history()
        if history_data:
            # Tạo DataFrame
            df = pd.DataFrame(history_data)
            
            # Hiển thị thống kê tổng quan
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Tổng Lượt Sử Dụng", len(history_data))
            with col2:
                unique_users = df['user_name'].nunique()
                st.metric("Số Người Dùng", unique_users)
            with col3:
                if len(history_data) > 0:
                    most_used = df['sound_name'].value_counts().index[0]
                    st.metric("Âm Thanh Phổ Biến", most_used)
            
            # Hiển thị bảng lịch sử với sorting options
            st.write("**Chi Tiết Lịch Sử:**")
            
            # Thêm options để sort
            col_sort, col_order = st.columns([2, 1])
            with col_sort:
                sort_column = st.selectbox(
                    "Sắp xếp theo:",
                    ["Mặc định", "Tài Khoản", "Bản Ghi Âm", "Thời Gian"],
                    key="sort_column_all"
                )
            with col_order:
                sort_ascending = st.selectbox(
                    "Thứ tự:",
                    ["Tăng dần", "Giảm dần"],
                    key="sort_order_all"
                ) == "Tăng dần"
            
            # Chuẩn bị DataFrame để hiển thị
            display_df = df[['user_name', 'sound_name', 'timestamp']].copy()
            display_df.columns = ['Tài Khoản', 'Bản Ghi Âm', 'Thời Gian']
            
            # Thực hiện sort trên toàn bộ dữ liệu trước khi phân trang
            if sort_column != "Mặc định":
                if sort_column == "Thời Gian":
                    # Convert timestamp to datetime for proper sorting
                    display_df['Thời Gian'] = pd.to_datetime(display_df['Thời Gian'])
                
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
                page = st.selectbox("Chọn trang:", range(1, total_pages + 1), key="history_page")
                start_idx = (page - 1) * items_per_page
                end_idx = start_idx + items_per_page
                
                # Hiển thị với index bắt đầu từ số thứ tự thực tế
                page_df = display_df.iloc[start_idx:end_idx].copy()
                
                # Adjust index to show correct row numbers for current page
                page_df.index = range(start_idx + 1, min(end_idx + 1, total_items + 1))
                page_df.index.name = 'STT'
                
                st.dataframe(page_df, use_container_width=True)
                st.write(f"Hiển thị {start_idx + 1}-{min(end_idx, total_items)} của {total_items} bản ghi")
            else:
                st.dataframe(display_df, use_container_width=True)
        else:
            st.info("Chưa có lịch sử sử dụng nào.")
    
    with tab2:
        # Lấy danh sách tất cả user để filter
        all_history = get_sound_history()
        if all_history:
            all_users = list(set([record['user_name'] for record in all_history]))
            selected_user = st.selectbox("Chọn tài khoản:", ["Tất cả"] + sorted(all_users), key="user_filter")
            
            if selected_user != "Tất cả":
                user_history = [record for record in all_history if record['user_name'] == selected_user]
                if user_history:
                    df_user = pd.DataFrame(user_history)
                    
                    # Thêm sorting cho tab user
                    col_sort_user, col_order_user = st.columns([2, 1])
                    with col_sort_user:
                        sort_column_user = st.selectbox(
                            "Sắp xếp theo:",
                            ["Mặc định", "Bản Ghi Âm", "Thời Gian"],
                            key="sort_column_user"
                        )
                    with col_order_user:
                        sort_ascending_user = st.selectbox(
                            "Thứ tự:",
                            ["Tăng dần", "Giảm dần"],
                            key="sort_order_user"
                        ) == "Tăng dần"
                    
                    display_df_user = df_user[['sound_name', 'timestamp']].copy()
                    display_df_user.columns = ['Bản Ghi Âm', 'Thời Gian']
                    
                    # Sort if needed
                    if sort_column_user != "Mặc định":
                        if sort_column_user == "Thời Gian":
                            display_df_user['Thời Gian'] = pd.to_datetime(display_df_user['Thời Gian'])
                        
                        display_df_user = display_df_user.sort_values(
                            by=sort_column_user, 
                            ascending=sort_ascending_user
                        )
                    
                    # Thêm cột STT bắt đầu từ 1
                    display_df_user.reset_index(drop=True, inplace=True)
                    display_df_user.index = display_df_user.index + 1
                    display_df_user.index.name = 'STT'
                    
                    st.write(f"**Lịch sử của {selected_user}:**")
                    st.dataframe(display_df_user, use_container_width=True)
                    
                    # Thống kê cho user này
                    st.write("**Thống kê:**")
                    col1, col2 = st.columns(2)
                    with col1:
                        st.metric("Tổng lượt sử dụng", len(user_history))
                    with col2:
                        if len(user_history) > 0:
                            most_used_by_user = df_user['sound_name'].value_counts().index[0]
                            st.metric("Âm thanh hay dùng nhất", most_used_by_user)
                else:
                    st.info(f"Người dùng {selected_user} chưa có lịch sử sử dụng.")
            else:
                st.info("Vui lòng chọn một tài khoản cụ thể để xem lịch sử.")
        else:
            st.info("Chưa có dữ liệu lịch sử để lọc.")
    
    with tab3:
        # Lọc theo bản ghi âm
        all_history = get_sound_history()
        if all_history:
            all_sounds = list(set([record['sound_name'] for record in all_history]))
            selected_sound = st.selectbox("Chọn bản ghi âm:", ["Tất cả"] + sorted(all_sounds), key="sound_filter")
            
            if selected_sound != "Tất cả":
                sound_history = [record for record in all_history if record['sound_name'] == selected_sound]
                if sound_history:
                    df_sound = pd.DataFrame(sound_history)
                    
                    # Thêm sorting cho tab sound
                    col_sort_sound, col_order_sound = st.columns([2, 1])
                    with col_sort_sound:
                        sort_column_sound = st.selectbox(
                            "Sắp xếp theo:",
                            ["Mặc định", "Tài Khoản", "Thời Gian"],
                            key="sort_column_sound"
                        )
                    with col_order_sound:
                        sort_ascending_sound = st.selectbox(
                            "Thứ tự:",
                            ["Tăng dần", "Giảm dần"],
                            key="sort_order_sound"
                        ) == "Tăng dần"
                    
                    display_df_sound = df_sound[['user_name', 'timestamp']].copy()
                    display_df_sound.columns = ['Tài Khoản', 'Thời Gian']
                    
                    # Sort if needed
                    if sort_column_sound != "Mặc định":
                        if sort_column_sound == "Thời Gian":
                            display_df_sound['Thời Gian'] = pd.to_datetime(display_df_sound['Thời Gian'])
                        
                        display_df_sound = display_df_sound.sort_values(
                            by=sort_column_sound, 
                            ascending=sort_ascending_sound
                        )
                    
                    # Thêm cột STT bắt đầu từ 1
                    display_df_sound.reset_index(drop=True, inplace=True)
                    display_df_sound.index = display_df_sound.index + 1
                    display_df_sound.index.name = 'STT'
                    
                    st.write(f"**Lịch sử sử dụng bản ghi âm: {selected_sound}**")
                    st.dataframe(display_df_sound, use_container_width=True)
                    
                    # Thống kê cho bản ghi âm này
                    st.write("**Thống kê:**")
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.metric("Tổng lượt phát", len(sound_history))
                    with col2:
                        unique_users_for_sound = df_sound['user_name'].nunique()
                        st.metric("Số người đã sử dụng", unique_users_for_sound)
                    with col3:
                        if len(sound_history) > 0:
                            most_active_user = df_sound['user_name'].value_counts().index[0]
                            st.metric("Người dùng tích cực nhất", most_active_user)
                    
                    # Biểu đồ thống kê người dùng
                    st.write("**Thống kê theo người dùng:**")
                    user_counts = df_sound['user_name'].value_counts()
                    st.bar_chart(user_counts)
                else:
                    st.info(f"Bản ghi âm {selected_sound} chưa được sử dụng.")
            else:
                st.info("Vui lòng chọn một bản ghi âm cụ thể để xem thống kê.")
        else:
            st.info("Chưa có dữ liệu lịch sử để lọc.")
            
# Phần biểu đồ cũ (có thể giữ lại hoặc bỏ tùy ý)
def display_old_charts():
    st.header("📈 Biểu Đồ Mẫu")
    
    tab1, tab2 = st.tabs(["📈 Customer per day", "🗃 Customer age group"])
    
    chart_data = {
        "Ngày": pd.date_range(start="2025-06-01", periods=14, freq="D"),
        "Nhiệt độ (°C)": [15, 16, 14, 12, 11, 15, 17, 15, 16, 14, 11, 9, 15, 11]
    }
    
    tab1.line_chart(chart_data, x="Ngày")
    
    data = {
        "Ngày": pd.date_range(start="2025-06-01", periods=14, freq="D"),
        "A": np.random.randint(10, 50, size=14),
        "B": np.random.randint(20, 60, size=14),
        "C": np.random.randint(5, 30, size=14)
    }
    
    df = pd.DataFrame(data)
    
    tab2.bar_chart(data, x="Ngày", stack=False)

# Hiển thị thống kê âm thanh
display_sound_history()
    
st.divider()
    
# Hiển thị biểu đồ mẫu (tùy chọn)
display_old_charts()