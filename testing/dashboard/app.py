import streamlit as st
import json
import os
import glob
import pandas as pd

st.set_page_config(page_title="Agentic QA Dashboard", layout="wide")
st.title("Agentic AI Testing & Evaluation Dashboard")

# Find latest report
reports = glob.glob("evaluation/reports/*_latest.json")
if not reports:
    st.warning("No evaluation reports found. Run the test suite first.")
else:
    latest_report_file = max(reports, key=os.path.getctime)
    with open(latest_report_file, 'r') as f:
        data = json.load(f)

    st.subheader(f"Latest Run: {data.get('name', 'Unknown')}")
    st.text(f"Timestamp: {data.get('test_run')}")
    
    col1, col2, col3, col4 = st.columns(4)
    total = data.get("total", 0)
    passed = data.get("passed", 0)
    failed = data.get("failed", 0)
    pass_rate = data.get("pass_rate", 0) * 100
    
    col1.metric("Total Tests", total)
    col2.metric("Passed", passed)
    col3.metric("Failed", failed)
    col4.metric("Pass Rate", f"{pass_rate:.1f}%")

    st.markdown("---")
    st.subheader("Test Results Breakdown")
    results = data.get("results", [])
    if results:
        df = pd.DataFrame(results)
        st.dataframe(df, use_container_width=True)

    st.markdown("---")
    st.subheader("Reproducibility Metadata")
    st.json(data.get("metadata", {}))

st.sidebar.title("Configuration")
st.sidebar.info("This dashboard passively reads `evaluation/reports/` for the latest evaluation outputs.")
