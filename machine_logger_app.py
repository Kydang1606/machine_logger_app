import streamlit as st
import pandas as pd
import plotly.express as px
from PIL import Image

# ================================================
# ✅ LOAD ALL SHEETS FROM EXCEL
# ================================================
def load_all_sheets(file):
    try:
        xls = pd.ExcelFile(file)
        sheet_data = {}
        for sheet_name in xls.sheet_names:
            df = pd.read_excel(xls, sheet_name=sheet_name, header=0)
            df.columns = df.columns.str.strip()
            df = df.loc[:, ~df.columns.str.contains("^Unnamed", na=False)]
            df["Machine Type"] = sheet_name  # Add sheet name as column
            sheet_data[sheet_name] = df
        return sheet_data
    except Exception as e:
        st.error(f"❌ Failed to read Excel file: {e}")
        return {}

# ================================================
# 📊 BAR CHART OF TOTAL HOURS BY MACHINE
# ================================================
def plot_bar(df, project_name, selected_machines):
    col_machine = "Machine/máy"
    col_hour = "Total Time (hr)"

    df_group = (
        df[df[col_machine].isin(selected_machines)]
        .groupby(col_machine)[col_hour]
        .sum()
        .reset_index()
    )

    fig = px.bar(
        df_group,
        x=col_machine,
        y=col_hour,
        text_auto=".2f",
        color=col_machine,
        title=f"📊 Total Processing Time by Machine - Project {project_name}",
        labels={col_hour: "Hours"}
    )
    st.plotly_chart(fig, use_container_width=True)

# ================================================
# 🌀 SUNBURST CHART FOR MACHINE & TASK
# ================================================
def plot_sunburst(df, selected_machines):
    col_machine = "Machine/máy"
    col_desc = "Mô tả/Description"
    col_hour = "Total Time (hr)"

    if any(col not in df.columns for col in [col_machine, col_desc, col_hour]):
        st.warning("⚠️ Required columns missing for sunburst chart.")
        return

    df_sun = df[df[col_machine].isin(selected_machines)]

    fig = px.sunburst(
        df_sun,
        path=[col_machine, col_desc],
        values=col_hour,
        title="🌀 Time Allocation by Machine and Task",
        labels={col_hour: "Hours"}
    )
    st.plotly_chart(fig, use_container_width=True)

# ================================================
# 🚀 MAIN APP
# ================================================
def main():
    st.set_page_config(page_title="⏱️ Machine Time Report Viewer", layout="wide")
    st.title("Machining Time Report")
        # 🚩 Logo và tiêu đề
    logo_path = "triac_logo.png"  # Đặt file logo cùng thư mục với app
    col1, col2 = st.columns([1, 8])
    with col1:
        st.image(Image.open(logo_path), width=100)
    with col2:
        st.title("🛠️ Machining Time Report")
        st.caption("By Machine Type and Project")

    uploaded_file = st.file_uploader("📤 Upload Excel File", type=["xlsx"])
    if not uploaded_file:
        return

    sheet_data = load_all_sheets(uploaded_file)
    if not sheet_data:
        return

    st.markdown("## 🔧 Filter Settings")

    # 👉 Merge all sheets
    full_df = pd.concat(sheet_data.values(), ignore_index=True)

    # Convert total minutes to hours
    col_min = "Tổng thời gian gia công/Total machining time (min)"
    if col_min in full_df.columns:
        full_df[col_min] = pd.to_numeric(full_df[col_min], errors="coerce")
        full_df["Total Time (hr)"] = full_df[col_min] / 60

    # Identify project column
    col_project = "Mã dự án/Project"
    if col_project not in full_df.columns:
        st.error("❌ Column 'Mã dự án/Project' not found.")
        st.write("Available columns:", full_df.columns.tolist())
        return

    # Select project
    projects = full_df[col_project].dropna().unique().tolist()
    selected_project = st.selectbox("📁 Select Project", projects)

    # Filter by selected project
    df_filtered = full_df[full_df[col_project] == selected_project]

    # Select machines
    machine_col = "Machine/máy"
    available_machines = df_filtered[machine_col].dropna().unique().tolist()
    selected_machines = st.multiselect("🛠️ Select Machine(s)", available_machines, default=available_machines)

    if not selected_machines:
        st.warning("⚠️ Please select at least one machine.")
        return

    df_selected = df_filtered[df_filtered[machine_col].isin(selected_machines)]

    # Show data
    st.markdown("### 📋 Filtered Data")
    st.dataframe(df_selected, use_container_width=True)

    # Charts
    st.markdown("## 📊 Visualization")
    plot_bar(df_selected, selected_project, selected_machines)
    st.markdown("---")
    plot_sunburst(df_selected, selected_machines)

# ================================================
# 🔁 RUN APP
# ================================================
if __name__ == "__main__":
    main()
