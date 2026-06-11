"""
Users View — Admin-only user management module.
"""

import streamlit as st
import pandas as pd


def render_users(api_request):
    st.markdown('<div class="page-title">User Management</div>', unsafe_allow_html=True)
    st.markdown('<div class="page-subtitle">Manage platform users, roles, and access</div>', unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["All Users", "Add User", "Edit User", "Delete User"])

    # ---- Tab 1: View All Users ----
    with tab1:
        result = api_request("get", "/users")
        if result and "users" in result:
            users = result["users"]
            if users:
                df = pd.DataFrame(users)
                display_df = df[["id", "name", "email", "role", "status", "created_at"]].copy()
                display_df.columns = ["ID", "Name", "Email", "Role", "Status", "Created"]
                display_df["Role"] = display_df["Role"].str.title()
                display_df["Status"] = display_df["Status"].str.title()
                display_df["Created"] = display_df["Created"].apply(
                    lambda x: x[:19].replace("T", " ") if x else "—"
                )

                st.dataframe(display_df, use_container_width=True, hide_index=True)

                # Summary
                c1, c2, c3, c4 = st.columns(4)
                with c1:
                    st.metric("Total Users", len(users))
                with c2:
                    st.metric("Admins", sum(1 for u in users if u["role"] == "admin"))
                with c3:
                    st.metric("Managers", sum(1 for u in users if u["role"] == "manager"))
                with c4:
                    st.metric("Staff", sum(1 for u in users if u["role"] == "staff"))
            else:
                st.info("No users found.")
        else:
            st.error("Failed to load users.")

    # ---- Tab 2: Add User ----
    with tab2:
        st.markdown('<div class="section-header">Create New User</div>', unsafe_allow_html=True)

        with st.form("add_user", clear_on_submit=True):
            c1, c2 = st.columns(2)
            with c1:
                name = st.text_input("Full Name *", placeholder="Jane Doe")
                email = st.text_input("Email *", placeholder="jane@proptech.com")
            with c2:
                role = st.selectbox("Role *", ["staff", "manager", "admin"])
                status = st.selectbox("Status", ["active", "inactive"])
            password = st.text_input("Password *", type="password", placeholder="Minimum 6 characters")

            if st.form_submit_button("Create User", type="primary", use_container_width=True):
                if not name or not email or not password:
                    st.error("Name, email, and password are required.")
                elif len(password) < 6:
                    st.error("Password must be at least 6 characters.")
                else:
                    res = api_request("post", "/users", {
                        "name": name, "email": email, "password": password,
                        "role": role, "status": status,
                    })
                    if res and "user" in res:
                        st.success(f"User '{name}' created as {role}.")
                    elif res and "error" in res:
                        st.error(res["error"])

    # ---- Tab 3: Edit User ----
    with tab3:
        st.markdown('<div class="section-header">Edit User</div>', unsafe_allow_html=True)

        edit_id = st.number_input("User ID", min_value=1, step=1, key="edit_uid")
        if st.button("Load User", key="load_user"):
            # Fetch user list and find by ID
            res = api_request("get", "/users")
            if res and "users" in res:
                found = next((u for u in res["users"] if u["id"] == edit_id), None)
                if found:
                    st.session_state.edit_user = found
                else:
                    st.error("User not found.")

        if "edit_user" in st.session_state:
            u = st.session_state.edit_user
            with st.form("edit_user_form"):
                c1, c2 = st.columns(2)
                with c1:
                    e_name = st.text_input("Name", value=u.get("name", ""))
                    e_email = st.text_input("Email", value=u.get("email", ""))
                with c2:
                    roles = ["staff", "manager", "admin"]
                    e_role = st.selectbox("Role", roles, index=roles.index(u.get("role", "staff")))
                    statuses = ["active", "inactive"]
                    e_status = st.selectbox("Status", statuses, index=statuses.index(u.get("status", "active")))
                e_password = st.text_input("New Password (leave blank to keep current)", type="password")

                if st.form_submit_button("Save Changes", type="primary", use_container_width=True):
                    payload = {
                        "name": e_name, "email": e_email,
                        "role": e_role, "status": e_status,
                    }
                    if e_password:
                        payload["password"] = e_password

                    res = api_request("put", f"/users/{u['id']}", payload)
                    if res and "user" in res:
                        st.success("User updated.")
                        del st.session_state.edit_user
                    elif res and "error" in res:
                        st.error(res["error"])

    # ---- Tab 4: Delete User ----
    with tab4:
        st.markdown('<div class="section-header">Delete User</div>', unsafe_allow_html=True)
        st.warning("This action is irreversible. You cannot delete your own account.")

        with st.form("delete_user"):
            del_id = st.number_input("User ID", min_value=1, step=1, key="del_uid")
            confirm = st.checkbox("I confirm this deletion")
            if st.form_submit_button("Delete User", type="primary"):
                if not confirm:
                    st.warning("Please confirm.")
                else:
                    res = api_request("delete", f"/users/{int(del_id)}")
                    if res and "message" in res:
                        st.success(res["message"])
                    elif res and "error" in res:
                        st.error(res["error"])
