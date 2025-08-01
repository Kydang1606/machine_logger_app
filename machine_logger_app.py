import streamlit as st
import pandas as pd
import plotly.express as px
import os
from datetime import datetime
from openpyxl import load_workbook, Workbook

# ================================================
# 🛠️ CẤU HÌNH BAN ĐẦU
# ================================================
st.set_page_config(page_title="Machine Log App", layout="centered")
DATA_PATH = "data/Logs.xlsx"
SHEET_NAME = "Logs"

# ================================================
# 🧠 HÀM TẠO FILE EXCEL VÀ SHEET "Logs" NẾU CHƯA TỒN TẠI
# ================================================
def ensure_log_file():
    if not os.path.exists("data"):
        os.makedirs("data")

    if not os.path.exists(DATA_PATH):
        wb = Workbook()
        ws = wb.active
        ws.title = SHEET_NAME
        ws.append(["Date", "Project", "Machine", "Hours", "Employee", "Note"])
        wb.save(DATA_PATH)
    else:
        wb = load_workbook(DATA_PATH)
        if SHEET_NAME not in wb.sheetnames:
            ws = wb.create_sheet(SHEET_NAME)
            ws.append(["Date", "Project", "Machine", "Hours", "Employee", "Note"])
            wb.save(DATA_PATH)

# ================================================
# ✅ GHI DỮ LIỆU VÀO FILE EXCEL
# ================================================
def log_to_excel(date, project, machine, hours, employee, note):
    df_new = pd.DataFrame([{
        "Date": date,
        "Project": project,
        "Machine": machine,
        "Hours": hours,
        "Employee": employee,
        "Note": note
    }])

    # Ghi vào sheet Logs
    with pd.ExcelWriter(DATA_PATH, engine="openpyxl", mode="a", if_sheet_exists="overlay") as writer:
        reader = pd.read_excel(DATA_PATH, sheet_name=SHEET_NAME)
        df_all = pd.concat([reader, df_new], ignore_index=True)
        df_all.to_excel(writer, sheet_name=SHEET_NAME, index=False)

# ================================================
# 🚀 ỨNG DỤNG CHÍNH
# ================================================
def main():
    st.title("📝 Machine Log Entry")
    ensure_log_file()

    with st.form("log_form", clear_on_submit=True):
        date = st.date_input("📅 Date", value=datetime.today())
        project = st.text_input("📁 Project")
        machine = st.text_input("🛠️ Machine")
        hours = st.number_input("⏱️ Hours", min_value=0.0, step=0.5)
        employee = st.text_input("👤 Employee")
        note = st.text_area("📝 Note (optional)")

        submitted = st.form_submit_button("✅ Submit Entry")
        if submitted:
            log_to_excel(date, project, machine, hours, employee, note)
            st.success("✅ Entry logged successfully!")

    st.markdown("---")

    # ========================================
    # 📊 HIỂN THỊ VÀ LỌC DỮ LIỆU
    # ========================================
    st.header("📋 Logs Viewer")

    try:
        df_logs = pd.read_excel(DATA_PATH, sheet_name=SHEET_NAME)
        if df_logs.empty:
            st.info("Chưa có dữ liệu nào.")
            return

        # Lọc theo Project hoặc Machine
        filter_col = st.selectbox("🔍 Filter by", ["Project", "Machine"])
        options = df_logs[filter_col].dropna().unique()
        selected = st.multiselect(f"Select {filter_col}(s)", options, default=options)

        filtered_df = df_logs[df_logs[filter_col].isin(selected)]
        st.dataframe(filtered_df, use_container_width=True)

        # ========================================
        # 📈 VẼ BIỂU ĐỒ
        # ========================================
        st.subheader("📊 Total Hours Chart")
        chart_data = (
            filtered_df.groupby(filter_col)["Hours"]
            .sum()
            .reset_index()
            .sort_values("Hours", ascending=False)
        )

        fig = px.bar(
            chart_data,
            x=filter_col,
            y="Hours",
            title=f"Total Hours by {filter_col}",
            text_auto=".2s",
            color=filter_col,
            height=400
        )
        st.plotly_chart(fig, use_container_width=True)

    except Exception as e:
        st.error(f"⚠️ Error reading logs: {e}")

# ================================================
# 🔁 CHẠY APP
# ================================================
if __name__ == "__main__":
    main()
