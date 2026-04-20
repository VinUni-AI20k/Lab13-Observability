import streamlit as st
import pandas as pd
import json
import os
import time
from pathlib import Path

# Cấu hình giao diện
st.set_page_config(page_title="Đà Nẵng Travel Agent Dashboard", layout="wide")
st.title("🏙️ Đà Nẵng Travel Agent - Real-time Observability")

LOG_FILE = Path("data/logs.jsonl")

def load_data():
    if not LOG_FILE.exists() or os.path.getsize(LOG_FILE) == 0:
        return pd.DataFrame()
    
    records = []
    with open(LOG_FILE, "r", encoding="utf-8") as f:
        for line in f:
            try:
                data = json.loads(line)
                # "Phẳng hóa" payload để lấy latency_ms, cost_usd, quality_score...
                if "payload" in data and isinstance(data["payload"], dict):
                    data.update(data["payload"])
                records.append(data)
            except: continue
    
    df = pd.DataFrame(records)
    if not df.empty:
        df['ts'] = pd.to_datetime(df['ts'])
        df = df.sort_values('ts') # Sắp xếp để biểu đồ không bị ngược
    return df

df = load_data()

if df.empty:
    st.warning("⚠️ Đang chờ dữ liệu log từ chatbot... Hãy chắc chắn file data/logs.jsonl không trống.")
else:
    # --- 6 PANELS THEO SPEC (LAYER-2) ---
    
    # Row 1: Metrics tổng quan
    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Traffic (Total Requests)", len(df))
    with c2:
        # Kiểm tra level để tính lỗi chính xác (level thường ghi chữ thường)
        err_count = len(df[df['level'].str.lower() == 'error'])
        err_rate = (err_count / len(df)) * 100
        st.metric("Error Rate", f"{err_rate:.1f}%", delta=f"{err_count} errors", delta_color="inverse")
    with c3:
        # Dùng cost_usd trực tiếp từ agent.py
        total_cost = df['cost_usd'].sum() if 'cost_usd' in df else 0
        st.metric("Total Cost", f"${total_cost:.4f}")

    # Row 2: Latency & Tokens
    c4, c5 = st.columns(2)
    with c4:
        st.subheader("Latency P50/P95/P99 (ms)")
        # Sử dụng latency_ms cho khớp với agent.py
        target_col = 'latency_ms' if 'latency_ms' in df else 'latency'
        if target_col in df:
            st.line_chart(df.set_index('ts')[target_col])
            st.caption("🔴 SLO Threshold: 5000ms")
    with c5:
        st.subheader("Tokens Usage (Input vs Output)")
        t_in = 'tokens_in'
        t_out = 'tokens_out'
        if t_in in df and t_out in df:
            st.area_chart(df.set_index('ts')[[t_in, t_out]])

    # Row 3: Quality Proxy
    st.subheader("Quality Proxy (Heuristic Score)")
    if 'quality_score' in df:
        st.bar_chart(df.set_index('ts')['quality_score'])
        st.caption("Score dựa trên: RAG matches, Answer length, và PII safety.")

    # --- BỔ SUNG: PII REDACTION EVIDENCE (Dành cho Member E báo cáo) ---
    with st.expander("🛡️ Xem Log Audit (Evidence PII Redaction)"):
        if 'event' in df:
            # Lọc các log có chứa [REDACTED]
            audit_df = df[df['event'].str.contains("REDACTED", na=False, case=False)]
            st.dataframe(audit_df[['ts', 'level', 'event']].tail(10), use_container_width=True)

# Sidebar UI
st.sidebar.header("Dashboard Settings")
st.sidebar.write(f"🔄 Auto-refreshing every 15s...")
if st.sidebar.button("Manual Refresh"):
    st.rerun()

# Logic refresh tự động
time.sleep(15)
st.rerun()