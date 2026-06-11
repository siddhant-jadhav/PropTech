"""
Monitoring View — System health dashboard.
Pulls all metrics from the backend /health endpoint (no local psutil).
"""

import streamlit as st
import plotly.graph_objects as go
import time


def render_monitoring(api_request):
    st.markdown('<div class="page-title">System Monitoring</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Infrastructure health and resource utilization</div>', unsafe_allow_html=True)

    # Controls
    c1, c2 = st.columns([1, 4])
    with c1:
        auto_refresh = st.checkbox("Auto-refresh", value=False)
    with c2:
        st.caption(f"Last checked: {time.strftime('%Y-%m-%d %H:%M:%S')}")

    health = api_request("get", "/health")
    if not health:
        st.error("Cannot reach the backend API.")
        return

    # ---- Service Status ----
    st.markdown('<div class="section-header">Service Status</div>', unsafe_allow_html=True)

    api_ok = health.get("status") == "running"
    db_ok = health.get("database") == "healthy"

    st.markdown(f"""
    <div class="status-row">
        <span class="status-dot {'green' if api_ok else 'red'}"></span>
        <span class="status-label">Flask API</span>
        <span class="status-detail">{'Running on port 5000' if api_ok else 'Down'}</span>
    </div>
    <div class="status-row">
        <span class="status-dot {'green' if db_ok else 'red'}"></span>
        <span class="status-label">MySQL Database</span>
        <span class="status-detail">{'Connected' if db_ok else health.get('database', 'Unknown')}</span>
    </div>
    <div class="status-row">
        <span class="status-dot green"></span>
        <span class="status-label">Streamlit Frontend</span>
        <span class="status-detail">Running on port 8501</span>
    </div>
    """, unsafe_allow_html=True)

    # ---- Resource Gauges ----
    st.markdown('<div class="section-header">Server Resources</div>', unsafe_allow_html=True)

    system = health.get("system", {})
    cpu = system.get("cpu_usage_percent", 0)
    ram = system.get("ram_usage_percent", 0)
    disk = system.get("disk_usage_percent", 0)

    g1, g2, g3 = st.columns(3)

    with g1:
        fig = _gauge("CPU Usage", cpu)
        st.plotly_chart(fig, use_container_width=True)

    with g2:
        fig = _gauge("RAM Usage", ram)
        st.plotly_chart(fig, use_container_width=True)

    with g3:
        fig = _gauge("Disk Usage", disk)
        st.plotly_chart(fig, use_container_width=True)

    # ---- Detailed Metrics ----
    st.markdown('<div class="section-header">Resource Details</div>', unsafe_allow_html=True)

    d1, d2 = st.columns(2)
    with d1:
        st.markdown("**Memory**")
        st.markdown(f"""
        | Metric | Value |
        |--------|-------|
        | Total | {system.get('ram_total_gb', 0)} GB |
        | Used | {system.get('ram_used_gb', 0)} GB |
        | Usage | {system.get('ram_usage_percent', 0)}% |
        """)

    with d2:
        st.markdown("**Disk**")
        st.markdown(f"""
        | Metric | Value |
        |--------|-------|
        | Total | {system.get('disk_total_gb', 0)} GB |
        | Used | {system.get('disk_used_gb', 0)} GB |
        | Usage | {system.get('disk_usage_percent', 0)}% |
        """)

    if auto_refresh:
        time.sleep(30)
        st.rerun()


def _gauge(title, value):
    """Create a clean resource gauge."""
    if value < 50:
        bar_color = "#16A34A"
    elif value < 80:
        bar_color = "#F59E0B"
    else:
        bar_color = "#DC2626"

    fig = go.Figure(go.Indicator(
        mode="gauge+number",
        value=value,
        title={"text": title, "font": {"size": 14, "family": "Inter", "color": "#0F172A"}},
        number={"suffix": "%", "font": {"size": 32, "color": "#0F172A"}},
        gauge={
            "axis": {"range": [0, 100], "tickwidth": 1, "tickcolor": "#E2E8F0"},
            "bar": {"color": bar_color, "thickness": 0.75},
            "bgcolor": "#F1F5F9",
            "borderwidth": 0,
            "steps": [
                {"range": [0, 50], "color": "#F0FDF4"},
                {"range": [50, 80], "color": "#FFFBEB"},
                {"range": [80, 100], "color": "#FEF2F2"},
            ],
        },
    ))
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)",
        height=250,
        margin=dict(t=50, b=0, l=25, r=25),
        font=dict(family="Inter"),
    )
    return fig
