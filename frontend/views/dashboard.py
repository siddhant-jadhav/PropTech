"""
Dashboard View — KPI cards, charts, and executive summary.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def render_dashboard(api_request):
    st.markdown('<div class="page-title">Dashboard</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Portfolio overview and key performance indicators</div>', unsafe_allow_html=True)

    data = api_request("get", "/dashboard")
    if not data:
        st.error("Failed to load dashboard data.")
        return

    kpis = data.get("kpis", {})
    maintenance = data.get("maintenance", {})
    charts = data.get("charts", {})
    activity = data.get("recent_activity", [])

    # ---- KPI Row 1: Properties ----
    total = kpis.get("total_properties", 0)
    occupied = kpis.get("occupied_properties", 0)
    vacant = kpis.get("vacant_properties", 0)
    occ_rate = kpis.get("occupancy_rate", 0)

    st.markdown(f"""
    <div class="kpi-row">
        <div class="kpi-card accent-blue">
            <div class="kpi-label">Total Properties</div>
            <div class="kpi-value">{total}</div>
            <div class="kpi-trend neutral">Across all cities</div>
        </div>
        <div class="kpi-card accent-green">
            <div class="kpi-label">Occupied</div>
            <div class="kpi-value">{occupied}</div>
            <div class="kpi-trend up">↑ {occ_rate}% occupancy</div>
        </div>
        <div class="kpi-card accent-amber">
            <div class="kpi-label">Vacant</div>
            <div class="kpi-value">{vacant}</div>
            <div class="kpi-trend {'down' if vacant > 0 else 'up'}">{'Needs attention' if vacant > 0 else 'All occupied'}</div>
        </div>
        <div class="kpi-card accent-purple">
            <div class="kpi-label">Occupancy Rate</div>
            <div class="kpi-value">{occ_rate}%</div>
            <div class="kpi-trend {'up' if occ_rate >= 75 else 'down'}">{'Healthy' if occ_rate >= 75 else 'Below target'}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ---- KPI Row 2: Revenue ----
    revenue = kpis.get("total_monthly_revenue", 0)
    avg_rev = kpis.get("avg_revenue_per_property", 0)
    annual = kpis.get("annual_projected_revenue", 0)

    st.markdown(f"""
    <div class="kpi-row">
        <div class="kpi-card accent-teal">
            <div class="kpi-label">Monthly Revenue</div>
            <div class="kpi-value">₹{revenue:,.0f}</div>
            <div class="kpi-trend up">Total collection</div>
        </div>
        <div class="kpi-card accent-blue">
            <div class="kpi-label">Avg Revenue / Property</div>
            <div class="kpi-value">₹{avg_rev:,.0f}</div>
            <div class="kpi-trend neutral">Per unit average</div>
        </div>
        <div class="kpi-card accent-green">
            <div class="kpi-label">Annual Projected</div>
            <div class="kpi-value">₹{annual:,.0f}</div>
            <div class="kpi-trend up">12-month forecast</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ---- KPI Row 3: Maintenance ----
    st.markdown('<div class="section-header">Maintenance Overview</div>', unsafe_allow_html=True)

    m_total = maintenance.get("total", 0)
    m_pending = maintenance.get("pending", 0)
    m_progress = maintenance.get("in_progress", 0)
    m_done = maintenance.get("completed", 0)

    st.markdown(f"""
    <div class="kpi-row">
        <div class="kpi-card accent-blue">
            <div class="kpi-label">Total Requests</div>
            <div class="kpi-value">{m_total}</div>
        </div>
        <div class="kpi-card accent-amber">
            <div class="kpi-label">Pending</div>
            <div class="kpi-value">{m_pending}</div>
        </div>
        <div class="kpi-card accent-purple">
            <div class="kpi-label">In Progress</div>
            <div class="kpi-value">{m_progress}</div>
        </div>
        <div class="kpi-card accent-green">
            <div class="kpi-label">Completed</div>
            <div class="kpi-value">{m_done}</div>
        </div>
    </div>
    """, unsafe_allow_html=True)

    # ---- Charts ----
    st.markdown('<div class="section-header">Analytics</div>', unsafe_allow_html=True)
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        city_data = charts.get("city_distribution", [])
        if city_data:
            df = pd.DataFrame(city_data)
            fig = px.pie(
                df, values="count", names="city",
                title="Properties by City", hole=0.45,
                color_discrete_sequence=["#2563EB", "#16A34A", "#F59E0B", "#7C3AED", "#0D9488",
                                         "#DC2626", "#64748B", "#EC4899", "#8B5CF6", "#059669"],
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Inter", color="#0F172A", size=12),
                title_font=dict(size=15, color="#0F172A"),
                legend=dict(orientation="h", y=-0.15, font=dict(size=11)),
                height=380, margin=dict(t=40, b=60, l=20, r=20),
            )
            fig.update_traces(textposition="inside", textinfo="percent+label", textfont_size=11)
            st.plotly_chart(fig, use_container_width=True)

    with chart_col2:
        rev_data = charts.get("revenue_by_city", [])
        if rev_data:
            df = pd.DataFrame(rev_data)
            fig = px.bar(
                df, x="city", y="revenue", title="Revenue by City (₹)",
                color_discrete_sequence=["#2563EB"],
            )
            fig.update_layout(
                paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Inter", color="#0F172A", size=12),
                title_font=dict(size=15, color="#0F172A"),
                xaxis_title="", yaxis_title="Revenue (₹)",
                xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="#F1F5F9"),
                height=380, margin=dict(t=40, b=40, l=20, r=20),
                showlegend=False,
            )
            fig.update_traces(
                text=df["revenue"].apply(lambda x: f"₹{x / 1000:.0f}K"),
                textposition="outside", marker_line_width=0,
            )
            st.plotly_chart(fig, use_container_width=True)

    # ---- Recent Activity ----
    st.markdown('<div class="section-header">Recent Activity</div>', unsafe_allow_html=True)

    if activity:
        for log in activity[:8]:
            action = log.get("action", "")
            icon = "●"
            color = "#64748B"
            if "CREATE" in action:
                icon = "●"; color = "#16A34A"
            elif "UPDATE" in action:
                icon = "●"; color = "#F59E0B"
            elif "DELETE" in action:
                icon = "●"; color = "#DC2626"
            elif "LOGIN" in action:
                icon = "●"; color = "#2563EB"

            ts = log.get("timestamp", "")[:19].replace("T", " ") if log.get("timestamp") else ""
            st.markdown(
                f'<div style="padding: 8px 0; border-bottom: 1px solid #F1F5F9; font-size: 13px;">'
                f'<span style="color: {color}; margin-right: 8px;">{icon}</span>'
                f'<strong>{log.get("user_name", "System")}</strong> — {action} '
                f'<span style="color: #94A3B8; float: right;">{ts}</span></div>',
                unsafe_allow_html=True,
            )
    else:
        st.info("No recent activity.")
