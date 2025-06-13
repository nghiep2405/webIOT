import streamlit as st
import pandas as pd
import numpy as np
import altair as alt

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