"""
Properties View — CRUD interface with search, filter, and data tables.
"""

import streamlit as st
import pandas as pd


def render_properties(api_request, user_role):
    st.markdown('<div class="page-title">Properties</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Manage your real estate portfolio</div>', unsafe_allow_html=True)

    # ---- Tabs ----
    if user_role in ("admin", "manager"):
        tab_list = ["All Properties", "Add Property", "Edit Property"]
        if user_role == "admin":
            tab_list.append("Delete Property")
        tabs = st.tabs(tab_list)
    else:
        tabs = st.tabs(["All Properties"])

    # ---- Tab: View Properties ----
    with tabs[0]:
        # Filters
        f1, f2, f3 = st.columns(3)
        with f1:
            search = st.text_input("Search by name", placeholder="Property name...", key="prop_search")
        with f2:
            status_filter = st.selectbox("Occupancy Status", ["All", "Occupied", "Vacant"], key="prop_status")
        with f3:
            city_filter = st.text_input("Filter by city", placeholder="City...", key="prop_city")

        params = {}
        if search:
            params["search"] = search
        if status_filter != "All":
            params["status"] = status_filter.lower()
        if city_filter:
            params["city"] = city_filter

        result = api_request("get", "/properties", params=params)

        if result and "properties" in result:
            properties = result["properties"]
            if properties:
                st.markdown(f"**{len(properties)} properties found**")

                df = pd.DataFrame(properties)
                display_df = df[["id", "property_name", "city", "address", "occupancy_status", "monthly_revenue"]].copy()
                display_df.columns = ["ID", "Name", "City", "Address", "Status", "Revenue (₹)"]
                display_df["Revenue (₹)"] = display_df["Revenue (₹)"].apply(lambda x: f"₹{x:,.0f}")

                st.dataframe(display_df, use_container_width=True, hide_index=True)

                # Summary
                s1, s2, s3 = st.columns(3)
                total_rev = sum(p["monthly_revenue"] for p in properties)
                occ_count = sum(1 for p in properties if p["occupancy_status"] == "occupied")
                with s1:
                    st.metric("Properties", len(properties))
                with s2:
                    st.metric("Occupied", f"{occ_count} / {len(properties)}")
                with s3:
                    st.metric("Total Revenue", f"₹{total_rev:,.0f}")
            else:
                st.info("No properties match your filters.")
        else:
            st.error("Failed to load properties.")

    # ---- Tab: Add Property ----
    if user_role in ("admin", "manager"):
        with tabs[1]:
            st.markdown('<div class="section-header">Add New Property</div>', unsafe_allow_html=True)

            with st.form("add_property", clear_on_submit=True):
                c1, c2 = st.columns(2)
                with c1:
                    name = st.text_input("Property Name *", placeholder="Skyline Tower B")
                    city = st.text_input("City *", placeholder="Mumbai")
                with c2:
                    occ = st.selectbox("Status", ["vacant", "occupied"])
                    rev = st.number_input("Monthly Revenue (₹)", min_value=0.0, step=5000.0, format="%.2f")
                address = st.text_area("Address *", placeholder="Full property address...")

                if st.form_submit_button("Add Property", type="primary", use_container_width=True):
                    if not name or not city or not address:
                        st.error("Fill all required fields.")
                    else:
                        res = api_request("post", "/properties", {
                            "property_name": name, "city": city, "address": address,
                            "occupancy_status": occ, "monthly_revenue": rev,
                        })
                        if res and "property" in res:
                            st.success(f"Property '{name}' created.")
                        elif res and "error" in res:
                            st.error(res["error"])

        # ---- Tab: Edit Property ----
        with tabs[2]:
            st.markdown('<div class="section-header">Edit Property</div>', unsafe_allow_html=True)

            edit_id = st.number_input("Property ID", min_value=1, step=1, key="edit_pid")
            if st.button("Load", key="load_prop"):
                res = api_request("get", f"/properties/{int(edit_id)}")
                if res and "property" in res:
                    st.session_state.edit_property = res["property"]
                elif res and "error" in res:
                    st.error(res["error"])

            if "edit_property" in st.session_state:
                p = st.session_state.edit_property
                with st.form("edit_property"):
                    c1, c2 = st.columns(2)
                    with c1:
                        e_name = st.text_input("Name", value=p.get("property_name", ""))
                        e_city = st.text_input("City", value=p.get("city", ""))
                    with c2:
                        e_occ = st.selectbox("Status", ["vacant", "occupied"],
                                             index=1 if p.get("occupancy_status") == "occupied" else 0)
                        e_rev = st.number_input("Revenue (₹)", value=float(p.get("monthly_revenue", 0)),
                                                step=5000.0, format="%.2f")
                    e_addr = st.text_area("Address", value=p.get("address", ""))

                    if st.form_submit_button("Save Changes", type="primary", use_container_width=True):
                        res = api_request("put", f"/properties/{p['id']}", {
                            "property_name": e_name, "city": e_city, "address": e_addr,
                            "occupancy_status": e_occ, "monthly_revenue": e_rev,
                        })
                        if res and "property" in res:
                            st.success("Property updated.")
                            del st.session_state.edit_property
                        elif res and "error" in res:
                            st.error(res["error"])

        # ---- Tab: Delete Property (Admin only) ----
        if user_role == "admin":
            with tabs[3]:
                st.markdown('<div class="section-header">Delete Property</div>', unsafe_allow_html=True)
                st.warning("Deleting a property removes all associated maintenance requests.")

                with st.form("delete_property"):
                    del_id = st.number_input("Property ID", min_value=1, step=1, key="del_pid")
                    confirm = st.checkbox("I confirm this deletion")
                    if st.form_submit_button("Delete Property", type="primary"):
                        if not confirm:
                            st.warning("Please confirm.")
                        else:
                            res = api_request("delete", f"/properties/{int(del_id)}")
                            if res and "message" in res:
                                st.success(res["message"])
                            elif res and "error" in res:
                                st.error(res["error"])
