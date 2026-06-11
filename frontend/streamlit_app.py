"""
PropTech Management System - Streamlit Frontend
Single-sidebar navigation with RBAC-based page visibility.
"""

import streamlit as st
import requests
import os

BACKEND_URL = os.getenv("BACKEND_URL", "http://localhost:5000")

# ---- Page Config ----
st.set_page_config(
    page_title="PropTech Management",
    page_icon="🏢",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ---- Professional CSS ----
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&display=swap');

    /* Reset and base */
    .stApp { background-color: #F8FAFC; font-family: 'Inter', sans-serif; }
    header[data-testid="stHeader"] { background: #F8FAFC; }
    .block-container { padding-top: 2rem; }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background: #FFFFFF;
        border-right: 1px solid #E2E8F0;
    }
    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] p { color: #0F172A; }
    [data-testid="stSidebar"] .stRadio label { color: #0F172A !important; }
    [data-testid="stSidebar"] .stRadio > div > label > div > p { color: #0F172A !important; }

    /* KPI Cards */
    .kpi-row { display: flex; gap: 16px; margin-bottom: 24px; flex-wrap: wrap; }
    .kpi-card {
        flex: 1;
        min-width: 180px;
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 20px 24px;
    }
    .kpi-card .kpi-label {
        font-size: 13px;
        font-weight: 500;
        color: #64748B;
        margin-bottom: 6px;
        text-transform: uppercase;
        letter-spacing: 0.5px;
    }
    .kpi-card .kpi-value {
        font-size: 28px;
        font-weight: 700;
        color: #0F172A;
        line-height: 1.2;
    }
    .kpi-card .kpi-trend {
        font-size: 12px;
        margin-top: 6px;
        font-weight: 500;
    }
    .kpi-card .kpi-trend.up { color: #16A34A; }
    .kpi-card .kpi-trend.down { color: #DC2626; }
    .kpi-card .kpi-trend.neutral { color: #64748B; }

    /* Accent bars */
    .kpi-card.accent-blue { border-top: 3px solid #2563EB; }
    .kpi-card.accent-green { border-top: 3px solid #16A34A; }
    .kpi-card.accent-amber { border-top: 3px solid #F59E0B; }
    .kpi-card.accent-red { border-top: 3px solid #DC2626; }
    .kpi-card.accent-purple { border-top: 3px solid #7C3AED; }
    .kpi-card.accent-teal { border-top: 3px solid #0D9488; }

    /* Section headers */
    .section-header {
        font-size: 18px;
        font-weight: 600;
        color: #0F172A;
        margin: 28px 0 16px 0;
        padding-bottom: 8px;
        border-bottom: 1px solid #E2E8F0;
    }

    /* Page title */
    .page-title {
        font-size: 24px;
        font-weight: 700;
        color: #0F172A;
        margin-bottom: 4px;
    }
    .page-subtitle {
        font-size: 14px;
        color: #64748B;
        margin-bottom: 24px;
    }

    /* Status badges */
    .badge {
        display: inline-block;
        padding: 3px 10px;
        border-radius: 6px;
        font-size: 12px;
        font-weight: 600;
        letter-spacing: 0.3px;
    }
    .badge-pending { background: #FEF3C7; color: #92400E; }
    .badge-approved { background: #DBEAFE; color: #1E40AF; }
    .badge-assigned { background: #E0E7FF; color: #3730A3; }
    .badge-in_progress { background: #FDE68A; color: #78350F; }
    .badge-completed { background: #D1FAE5; color: #065F46; }
    .badge-closed { background: #F1F5F9; color: #475569; }
    .badge-rejected { background: #FEE2E2; color: #991B1B; }
    .badge-occupied { background: #D1FAE5; color: #065F46; }
    .badge-vacant { background: #FEF3C7; color: #92400E; }
    .badge-active { background: #D1FAE5; color: #065F46; }
    .badge-inactive { background: #FEE2E2; color: #991B1B; }

    /* White card container */
    .card {
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 12px;
        padding: 24px;
        margin-bottom: 16px;
    }

    /* Service status indicator */
    .status-row {
        display: flex;
        align-items: center;
        gap: 10px;
        padding: 12px 16px;
        background: #FFFFFF;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        margin-bottom: 8px;
    }
    .status-dot {
        width: 10px;
        height: 10px;
        border-radius: 50%;
        display: inline-block;
    }
    .status-dot.green { background: #16A34A; }
    .status-dot.red { background: #DC2626; }
    .status-label { font-size: 14px; font-weight: 500; color: #0F172A; }
    .status-detail { font-size: 13px; color: #64748B; margin-left: auto; }

    /* Hide Streamlit default elements */
    #MainMenu { visibility: hidden; }
    footer { visibility: hidden; }

    /* Buttons */
    .stButton > button {
        border-radius: 8px;
        font-weight: 500;
        font-family: 'Inter', sans-serif;
    }

    /* Sidebar user card */
    .sidebar-user {
        padding: 12px 16px;
        background: #F8FAFC;
        border: 1px solid #E2E8F0;
        border-radius: 8px;
        margin-bottom: 12px;
    }
    .sidebar-user .user-name { font-weight: 600; color: #0F172A; font-size: 14px; }
    .sidebar-user .user-email { color: #64748B; font-size: 12px; }
    .sidebar-user .user-role {
        display: inline-block;
        padding: 2px 8px;
        border-radius: 4px;
        font-size: 11px;
        font-weight: 600;
        margin-top: 4px;
        background: #DBEAFE;
        color: #1E40AF;
    }

    /* Nav styling */
    .nav-item {
        padding: 8px 12px;
        border-radius: 8px;
        margin-bottom: 2px;
        cursor: pointer;
        color: #334155;
        font-size: 14px;
        font-weight: 500;
    }
    .nav-item:hover { background: #F1F5F9; }
    .nav-item.active { background: #EFF6FF; color: #2563EB; font-weight: 600; }

    /* Form styling */
    .stTextInput > div > div > input,
    .stTextArea > div > div > textarea,
    .stSelectbox > div > div {
        border-radius: 8px !important;
    }
</style>
""", unsafe_allow_html=True)


# ---- API Helper ----

def api_request(method, endpoint, data=None, params=None):
    """Make an authenticated API request to the Flask backend."""
    url = f"{BACKEND_URL}{endpoint}"
    headers = {}
    if "token" in st.session_state:
        headers["Authorization"] = f"Bearer {st.session_state.token}"

    try:
        if method == "get":
            resp = requests.get(url, headers=headers, params=params, timeout=10)
        elif method == "post":
            resp = requests.post(url, json=data, headers=headers, timeout=10)
        elif method == "put":
            resp = requests.put(url, json=data, headers=headers, timeout=10)
        elif method == "delete":
            resp = requests.delete(url, headers=headers, timeout=10)
        else:
            return None

        if resp.status_code == 401:
            st.session_state.clear()
            st.error("Session expired. Please login again.")
            st.rerun()
            return None

        return resp.json() if resp.status_code < 500 else None

    except requests.exceptions.ConnectionError:
        st.error("Cannot connect to the backend API.")
        return None
    except requests.exceptions.Timeout:
        st.error("Request timed out.")
        return None
    except Exception as e:
        st.error(f"API Error: {str(e)}")
        return None


# ---- RBAC Page Definitions ----

ROLE_PAGES = {
    "admin": ["Dashboard", "Properties", "Maintenance", "Users", "Reports", "Monitoring"],
    "manager": ["Dashboard", "Properties", "Maintenance", "Reports"],
    "staff": ["Dashboard", "Maintenance"],
}

PAGE_ICONS = {
    "Dashboard": "📊",
    "Properties": "🏠",
    "Maintenance": "🔧",
    "Users": "👥",
    "Reports": "📈",
    "Monitoring": "🖥",
}


# ---- Login Page ----

def login_page():
    """Professional login form."""
    col1, col2, col3 = st.columns([1, 1.2, 1])
    with col2:
        st.markdown("")
        st.markdown("")
        st.markdown("""
        <div style="text-align: center; margin-bottom: 32px;">
            <div style="font-size: 40px; margin-bottom: 8px;">🏢</div>
            <div style="font-size: 22px; font-weight: 700; color: #0F172A;">PropTech Management</div>
            <div style="font-size: 14px; color: #64748B; margin-top: 4px;">Sign in to your account</div>
        </div>
        """, unsafe_allow_html=True)

        with st.form("login_form"):
            email = st.text_input("Email", placeholder="admin@proptech.com")
            password = st.text_input("Password", type="password", placeholder="Enter password")
            submitted = st.form_submit_button("Sign In", use_container_width=True, type="primary")

            if submitted:
                if not email or not password:
                    st.error("Email and password are required.")
                else:
                    result = api_request("post", "/login", {"email": email, "password": password})
                    if result and "token" in result:
                        st.session_state.token = result["token"]
                        st.session_state.user = result["user"]
                        st.session_state.logged_in = True
                        st.rerun()
                    elif result and "error" in result:
                        st.error(result["error"])

        st.markdown("---")
        st.markdown("""
        <div style="text-align: center; color: #94A3B8; font-size: 12px; line-height: 1.8;">
            <strong>Demo Accounts</strong><br>
            admin@proptech.com · sarah@proptech.com · john@proptech.com<br>
            Password: Password@123
        </div>
        """, unsafe_allow_html=True)


# ---- Main Application ----

def main_app():
    """Main application with single sidebar navigation."""
    user = st.session_state.get("user", {})
    user_role = user.get("role", "staff")
    available_pages = ROLE_PAGES.get(user_role, ["Dashboard"])

    # ---- Sidebar ----
    with st.sidebar:
        # Logo
        st.markdown("""
        <div style="padding: 8px 0 16px 0; border-bottom: 1px solid #E2E8F0; margin-bottom: 16px;">
            <div style="font-size: 18px; font-weight: 700; color: #0F172A;">🏢 PropTech</div>
            <div style="font-size: 11px; color: #94A3B8;">Management System</div>
        </div>
        """, unsafe_allow_html=True)

        # User info card
        role_badge = user.get("role", "staff").title()
        st.markdown(f"""
        <div class="sidebar-user">
            <div class="user-name">{user.get('name', 'User')}</div>
            <div class="user-email">{user.get('email', '')}</div>
            <span class="user-role">{role_badge}</span>
        </div>
        """, unsafe_allow_html=True)

        # Navigation
        nav_options = [f"{PAGE_ICONS.get(p, '')}  {p}" for p in available_pages]
        selected = st.radio("Navigation", nav_options, label_visibility="collapsed")
        page_name = selected.split("  ", 1)[1] if "  " in selected else selected

        st.markdown("---")

        if st.button("Logout", use_container_width=True):
            st.session_state.clear()
            st.rerun()

        st.markdown("""
        <div style="position: fixed; bottom: 12px; font-size: 11px; color: #CBD5E1;">
            PropTech v2.0
        </div>
        """, unsafe_allow_html=True)

    # ---- Page Router ----
    if page_name == "Dashboard":
        from views.dashboard import render_dashboard
        render_dashboard(api_request)
    elif page_name == "Properties":
        from views.properties import render_properties
        render_properties(api_request, user_role)
    elif page_name == "Maintenance":
        from views.maintenance import render_maintenance
        render_maintenance(api_request, user_role)
    elif page_name == "Users":
        from views.users import render_users
        render_users(api_request)
    elif page_name == "Reports":
        from views.reports import render_reports
        render_reports(api_request)
    elif page_name == "Monitoring":
        from views.monitoring import render_monitoring
        render_monitoring(api_request)


# ---- Entry Point ----
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False

if st.session_state.logged_in:
    main_app()
else:
    login_page()
