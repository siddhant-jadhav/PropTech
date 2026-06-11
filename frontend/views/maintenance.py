"""
Maintenance View — Workflow management with status tracking.
Workflow: Pending → Approved → Assigned → In Progress → Completed → Closed
"""

import streamlit as st
import pandas as pd


STATUS_ORDER = ["pending", "approved", "assigned", "in_progress", "completed", "closed", "rejected"]

TRANSITIONS = {
    "pending": ["approved", "rejected"],
    "approved": ["assigned", "rejected"],
    "assigned": ["in_progress", "rejected"],
    "in_progress": ["completed"],
    "completed": ["closed"],
    "rejected": ["pending"],
    "closed": [],
}

STATUS_LABELS = {
    "pending": "Pending",
    "approved": "Approved",
    "assigned": "Assigned",
    "in_progress": "In Progress",
    "completed": "Completed",
    "closed": "Closed",
    "rejected": "Rejected",
}


def _badge(status):
    label = STATUS_LABELS.get(status, status)
    return f'<span class="badge badge-{status}">{label}</span>'


def render_maintenance(api_request, user_role):
    st.markdown('<div class="page-title">Maintenance</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Track and manage maintenance requests across properties</div>', unsafe_allow_html=True)

    tab1, tab2, tab3 = st.tabs(["All Requests", "New Request", "Update Status"])

    # ---- Tab 1: All Requests ----
    with tab1:
        f1, f2 = st.columns(2)
        with f1:
            status_filter = st.selectbox("Status", ["All"] + [STATUS_LABELS[s] for s in STATUS_ORDER], key="mf_status")
        with f2:
            prop_filter = st.text_input("Property ID", key="mf_prop")

        params = {}
        if status_filter != "All":
            # Reverse lookup
            for k, v in STATUS_LABELS.items():
                if v == status_filter:
                    params["status"] = k
                    break
        if prop_filter:
            params["property_id"] = prop_filter

        result = api_request("get", "/maintenance", params=params)

        if result and "maintenance_requests" in result:
            reqs = result["maintenance_requests"]

            if reqs:
                # Summary counts
                counts = {}
                for r in reqs:
                    s = r["status"]
                    counts[s] = counts.get(s, 0) + 1

                cols = st.columns(min(len(counts), 6))
                for i, (s, c) in enumerate(counts.items()):
                    with cols[i % len(cols)]:
                        st.metric(STATUS_LABELS.get(s, s), c)

                st.markdown("---")

                # Request cards
                for req in reqs:
                    status = req["status"]
                    with st.expander(f"#{req['id']} — {req['title']}  |  {STATUS_LABELS.get(status, status)}  |  {req.get('property_name', '')}"):
                        c1, c2 = st.columns(2)
                        with c1:
                            st.markdown(f"**Property:** {req.get('property_name', 'N/A')}")
                            st.markdown(f"**Title:** {req['title']}")
                            st.markdown(f"**Description:** {req.get('description') or '—'}")
                        with c2:
                            st.markdown(f"**Status:** {_badge(status)}", unsafe_allow_html=True)
                            st.markdown(f"**Assigned To:** {req.get('assigned_to_name') or '—'}")
                            st.markdown(f"**Approved By:** {req.get('approved_by_name') or '—'}")
                            st.markdown(f"**Created:** {req.get('created_at', '—')[:19].replace('T', ' ')}")
            else:
                st.info("No maintenance requests found.")
        else:
            st.error("Failed to load maintenance requests.")

    # ---- Tab 2: New Request ----
    with tab2:
        st.markdown('<div class="section-header">Submit Maintenance Request</div>', unsafe_allow_html=True)

        props_result = api_request("get", "/properties")
        prop_map = {}
        if props_result and "properties" in props_result:
            for p in props_result["properties"]:
                prop_map[f"{p['property_name']} (#{p['id']})"] = p["id"]

        with st.form("new_maint", clear_on_submit=True):
            selected_prop = st.selectbox("Property *", list(prop_map.keys()) if prop_map else ["No properties"])
            title = st.text_input("Title *", placeholder="Short description of the issue")
            desc = st.text_area("Description", placeholder="Detailed information...")

            if st.form_submit_button("Submit Request", type="primary", use_container_width=True):
                if not title or not prop_map:
                    st.error("Title and property are required.")
                else:
                    res = api_request("post", "/maintenance", {
                        "property_id": prop_map.get(selected_prop),
                        "title": title,
                        "description": desc,
                    })
                    if res and "maintenance_request" in res:
                        st.success(f"Request '{title}' submitted.")
                    elif res and "error" in res:
                        st.error(res["error"])

    # ---- Tab 3: Update Status ----
    with tab3:
        st.markdown('<div class="section-header">Update Request Status</div>', unsafe_allow_html=True)

        st.markdown("""
        **Workflow:** `Pending` → `Approved` → `Assigned` → `In Progress` → `Completed` → `Closed`
        """)

        req_id = st.number_input("Request ID", min_value=1, step=1, key="upd_maint_id")

        if st.button("Load Request", key="load_maint"):
            res = api_request("get", f"/maintenance/{int(req_id)}")
            if res and "maintenance_request" in res:
                st.session_state.edit_maint = res["maintenance_request"]
            elif res and "error" in res:
                st.error(res["error"])

        if "edit_maint" in st.session_state:
            req = st.session_state.edit_maint
            cur = req["status"]

            st.markdown(f"**#{req['id']}** — {req['title']}")
            st.markdown(f"**Property:** {req.get('property_name', 'N/A')}")
            st.markdown(f"**Current Status:** {_badge(cur)}", unsafe_allow_html=True)

            valid = TRANSITIONS.get(cur, [])
            if not valid:
                st.success("No further transitions available.")
            else:
                with st.form("update_maint_status"):
                    new_status = st.selectbox("New Status", [STATUS_LABELS[s] for s in valid])

                    # Reverse lookup for actual enum
                    new_status_key = cur
                    for k, v in STATUS_LABELS.items():
                        if v == new_status:
                            new_status_key = k
                            break

                    assigned_to = None
                    if new_status_key == "assigned":
                        users_res = api_request("get", "/users")
                        if users_res and "users" in users_res:
                            user_map = {f"{u['name']} ({u['role']})": u["id"] for u in users_res["users"]}
                            sel_user = st.selectbox("Assign To *", list(user_map.keys()))
                            assigned_to = user_map.get(sel_user)

                    if st.form_submit_button("Update Status", type="primary", use_container_width=True):
                        payload = {"status": new_status_key}
                        if assigned_to:
                            payload["assigned_to"] = assigned_to

                        res = api_request("put", f"/maintenance/{req['id']}", payload)
                        if res and "maintenance_request" in res:
                            st.success(f"Status updated to '{new_status}'.")
                            st.session_state.edit_maint = res["maintenance_request"]
                            st.rerun()
                        elif res and "error" in res:
                            st.error(res["error"])
