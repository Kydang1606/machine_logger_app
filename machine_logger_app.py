import streamlit as st 
import pandas as pd
import plotly.express as px
import os
from datetime import datetime, timedelta
from openpyxl import load_workbook, Workbook

FILE_PATH = "machine_log.xlsx"
SHEET_NAME = "Logs"

st.set_page_config(page_title="Machine Logger", layout="wide")

st.title("🛠️ Machine Work Logger")

# --- Load existing logs ---
@st.cache_data
def load_logs():
    if os.path.exists(FILE_PATH):
        try:
            df = pd.read_excel(FILE_PATH, sheet_name=SHEET_NAME, parse_dates=["Date"])
            return df
        except Exception as e:
            st.warning(f"Could not load existing log: {e}")
            return pd.DataFrame()
    else:
        return pd.DataFrame()

df_logs = load_logs()

# --- Input form ---
st.subheader("➕ Nhập thông tin công việc")

with st.form("log_form", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        date = st.date_input("📅 Ngày", value=datetime.today())
        start_time = st.time_input("🕑 Thời gian bắt đầu", value=datetime.strptime("08:00", "%H:%M").time())
    with col2:
        end_time = st.time_input("🕕 Thời gian kết thúc", value=datetime.strptime("12:00", "%H:%M").time())
        machine = st.text_input("🏭 Máy", placeholder="Tên máy")
    with col3:
        project_code = st.text_input("📁 Mã dự án", placeholder="VD: D001")
        material = st.text_input("🧱 Loại vật liệu", placeholder="VD: CFRP, GRP,...")
    
    executor = st.text_input("👷 Người thực hiện", placeholder="Họ và tên")
    description = st.text_area("📋 Mô tả công việc", height=100)

    submitted = st.form_submit_button("📤 Ghi vào log")

    if submitted:
        try:
            # Tính tổng thời gian
            start_dt = datetime.combine(date, start_time)
            end_dt = datetime.combine(date, end_time)
            if end_dt < start_dt:
                end_dt += timedelta(days=1)
            total_minutes = (end_dt - start_dt).seconds // 60
            total_hours = round(total_minutes / 60, 2)

            # Tạo record mới
            new_row = pd.DataFrame([{
                "Date": date,
                "Executor": executor,
                "Start": start_time.strftime("%H:%M"),
                "End": end_time.strftime("%H:%M"),
                "Total (min)": total_minutes,
                "Total (hr)": total_hours,
                "Machine": machine,
                "Project Code": project_code,
                "Material": material,
                "Description": description
            }])

            # Ghi vào file Excel
            if os.path.exists(FILE_PATH):
                existing = pd.read_excel(FILE_PATH, sheet_name=SHEET_NAME)
                updated_df = pd.concat([existing, new_row], ignore_index=True)
            else:
                updated_df = new_row

            with pd.ExcelWriter(FILE_PATH, engine="openpyxl", mode="w") as writer:
                updated_df.to_excel(writer, index=False, sheet_name=SHEET_NAME)

            st.success("✅ Ghi log thành công!")
            st.experimental_rerun()

        except Exception as e:
            st.error(f"❌ Lỗi khi ghi log: {e}")

# --- Hiển thị log ---
st.divider()
st.subheader("📊 Tổng hợp thời gian theo máy")

if not df_logs.empty:
    df_logs["Total (hr)"] = pd.to_numeric(df_logs["Total (hr)"], errors="coerce")
    summary = df_logs.groupby("Machine")["Total (hr)"].sum().reset_index().sort_values("Total (hr)", ascending=False)
    st.dataframe(summary, use_container_width=True)
else:
    st.info("Chưa có dữ liệu log nào.")
