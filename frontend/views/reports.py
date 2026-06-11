"""
Reports View — Executive reporting with Plotly charts and CSV export.
"""

import streamlit as st
import plotly.express as px
import plotly.graph_objects as go
import pandas as pd


def render_reports(api_request):
    st.markdown('<div class="page-title">Reports</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Executive analytics — occupancy, revenue, and maintenance</div>', unsafe_allow_html=True)

    result = api_request("get", "/reports", params={"type": "all"})
    if not result:
        st.error("Failed to load reports.")
        return

    tab1, tab2, tab3 = st.tabs(["Occupancy Report", "Revenue Report", "Maintenance Report"])

    # ========================================
    # Occupancy Report
    # ========================================
    with tab1:
        occ = result.get("occupancy_report", {})

        # KPIs
        st.markdown(f"""
        <div class="kpi-row">
            <div class="kpi-card accent-blue">
                <div class="kpi-label">Total Properties</div>
                <div class="kpi-value">{occ.get('total_properties', 0)}</div>
            </div>
            <div class="kpi-card accent-green">
                <div class="kpi-label">Occupied</div>
                <div class="kpi-value">{occ.get('occupied', 0)}</div>
            </div>
            <div class="kpi-card accent-amber">
                <div class="kpi-label">Vacant</div>
                <div class="kpi-value">{occ.get('vacant', 0)}</div>
            </div>
            <div class="kpi-card accent-purple">
                <div class="kpi-label">Occupancy Rate</div>
                <div class="kpi-value">{occ.get('occupancy_rate', 0)}%</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        city = occ.get("city_breakdown", [])
        if city:
            df = pd.DataFrame(city)
            c1, c2 = st.columns(2)

            with c1:
                fig = px.bar(
                    df, x="city", y=["occupied", "vacant"],
                    title="Occupancy by City", barmode="group",
                    color_discrete_sequence=["#16A34A", "#F59E0B"],
                )
                _clean_layout(fig)
                st.plotly_chart(fig, use_container_width=True)

            with c2:
                fig = px.bar(
                    df, x="city", y="occupancy_rate", title="Occupancy Rate (%)",
                    color_discrete_sequence=["#2563EB"],
                )
                _clean_layout(fig)
                fig.update_traces(text=df["occupancy_rate"].apply(lambda x: f"{x}%"), textposition="outside")
                st.plotly_chart(fig, use_container_width=True)

            st.markdown('<div class="section-header">Data Table</div>', unsafe_allow_html=True)
            st.dataframe(df, use_container_width=True, hide_index=True)
            _download_csv(df, "occupancy_report.csv", "Download Occupancy CSV")

    # ========================================
    # Revenue Report
    # ========================================
    with tab2:
        rev = result.get("revenue_report", {})

        st.markdown(f"""
        <div class="kpi-row">
            <div class="kpi-card accent-teal">
                <div class="kpi-label">Monthly Revenue</div>
                <div class="kpi-value">₹{rev.get('total_monthly_revenue', 0):,.0f}</div>
            </div>
            <div class="kpi-card accent-green">
                <div class="kpi-label">Annual Projected</div>
                <div class="kpi-value">₹{rev.get('annual_projected_revenue', 0):,.0f}</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        city_rev = rev.get("city_breakdown", [])
        if city_rev:
            df = pd.DataFrame(city_rev)
            c1, c2 = st.columns(2)

            with c1:
                fig = px.bar(
                    df, x="city", y="total_revenue", title="Revenue by City (₹)",
                    color_discrete_sequence=["#2563EB"],
                )
                _clean_layout(fig)
                fig.update_traces(
                    text=df["total_revenue"].apply(lambda x: f"₹{x / 1000:.0f}K"),
                    textposition="outside",
                )
                st.plotly_chart(fig, use_container_width=True)

            with c2:
                fig = px.pie(
                    df, values="total_revenue", names="city",
                    title="Revenue Distribution", hole=0.4,
                    color_discrete_sequence=["#2563EB", "#16A34A", "#F59E0B", "#7C3AED",
                                             "#0D9488", "#DC2626", "#64748B", "#EC4899"],
                )
                _clean_layout(fig)
                st.plotly_chart(fig, use_container_width=True)

            _download_csv(df, "revenue_report.csv", "Download Revenue CSV")

        top = rev.get("top_properties", [])
        if top:
            st.markdown('<div class="section-header">Top Revenue Properties</div>', unsafe_allow_html=True)
            df_top = pd.DataFrame(top)[["property_name", "city", "monthly_revenue", "occupancy_status"]]
            df_top.columns = ["Property", "City", "Revenue (₹)", "Status"]
            df_top["Revenue (₹)"] = df_top["Revenue (₹)"].apply(lambda x: f"₹{x:,.0f}")
            st.dataframe(df_top, use_container_width=True, hide_index=True)

    # ========================================
    # Maintenance Report
    # ========================================
    with tab3:
        maint = result.get("maintenance_report", {})

        st.markdown(f"""
        <div class="kpi-row">
            <div class="kpi-card accent-blue">
                <div class="kpi-label">Total Requests</div>
                <div class="kpi-value">{maint.get('total_requests', 0)}</div>
            </div>
            <div class="kpi-card accent-amber">
                <div class="kpi-label">Pending</div>
                <div class="kpi-value">{maint.get('pending', 0)}</div>
            </div>
            <div class="kpi-card accent-green">
                <div class="kpi-label">Completed</div>
                <div class="kpi-value">{maint.get('completed', 0)}</div>
            </div>
            <div class="kpi-card accent-purple">
                <div class="kpi-label">Completion Rate</div>
                <div class="kpi-value">{maint.get('completion_rate', 0)}%</div>
            </div>
        </div>
        """, unsafe_allow_html=True)

        status = maint.get("status_breakdown", {})
        if status:
            c1, c2 = st.columns(2)

            with c1:
                df_s = pd.DataFrame(list(status.items()), columns=["Status", "Count"])
                colors = {
                    "pending": "#F59E0B", "approved": "#2563EB", "assigned": "#7C3AED",
                    "in_progress": "#EC4899", "completed": "#16A34A", "closed": "#64748B",
                    "rejected": "#DC2626",
                }
                fig = px.pie(
                    df_s, values="Count", names="Status",
                    title="Status Distribution", hole=0.4,
                    color="Status", color_discrete_map=colors,
                )
                _clean_layout(fig)
                st.plotly_chart(fig, use_container_width=True)

            with c2:
                comp = maint.get("completion_rate", 0)
                fig = go.Figure(go.Indicator(
                    mode="gauge+number", value=comp,
                    title={"text": "Completion Rate", "font": {"size": 15, "family": "Inter"}},
                    number={"suffix": "%", "font": {"size": 36}},
                    gauge={
                        "axis": {"range": [0, 100]},
                        "bar": {"color": "#16A34A"},
                        "steps": [
                            {"range": [0, 40], "color": "#FEE2E2"},
                            {"range": [40, 70], "color": "#FEF3C7"},
                            {"range": [70, 100], "color": "#D1FAE5"},
                        ],
                    },
                ))
                fig.update_layout(
                    paper_bgcolor="rgba(0,0,0,0)", font=dict(family="Inter"),
                    height=350, margin=dict(t=40, b=0),
                )
                st.plotly_chart(fig, use_container_width=True)

        prop_data = maint.get("property_breakdown", [])
        if prop_data:
            st.markdown('<div class="section-header">Requests by Property</div>', unsafe_allow_html=True)
            df_p = pd.DataFrame(prop_data)
            fig = px.bar(
                df_p, x="property_name", y="request_count",
                title="Maintenance Requests per Property",
                color_discrete_sequence=["#DC2626"],
            )
            _clean_layout(fig)
            st.plotly_chart(fig, use_container_width=True)
            _download_csv(df_p, "maintenance_report.csv", "Download Maintenance CSV")


def _clean_layout(fig):
    """Apply consistent chart styling."""
    fig.update_layout(
        paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Inter", color="#0F172A", size=12),
        title_font=dict(size=15, color="#0F172A"),
        xaxis=dict(showgrid=False), yaxis=dict(showgrid=True, gridcolor="#F1F5F9"),
        height=380, margin=dict(t=40, b=40, l=20, r=20),
        showlegend=True,
    )


def _download_csv(df, filename, label):
    """Render a CSV download button."""
    csv = df.to_csv(index=False)
    st.download_button(label, data=csv, file_name=filename, mime="text/csv", use_container_width=True)
