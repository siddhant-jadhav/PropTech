# 🏢 PropTech — Property Management System v2.0

Production-grade property management platform built with **Flask + Streamlit + MySQL + Docker**.

---

## Architecture

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│   Streamlit     │────▶│   Flask API     │────▶│   MySQL 8.0     │
│   Port: 8501    │     │   Port: 5000    │     │   Port: 3306    │
└─────────────────┘     └─────────────────┘     └─────────────────┘
```

## Project Structure

```
property_management_system/
├── backend/
│   ├── app.py
│   ├── config.py
│   ├── models.py
│   ├── database.py
│   ├── requirements.txt
│   ├── Dockerfile
│   └── routes/
│       ├── auth.py          # Login + User CRUD
│       ├── properties.py
│       ├── maintenance.py
│       ├── reports.py
│       └── dashboard.py
├── frontend/
│   ├── streamlit_app.py     # Main app + sidebar + RBAC
│   ├── requirements.txt
│   ├── Dockerfile
│   └── views/
│       ├── dashboard.py
│       ├── properties.py
│       ├── maintenance.py
│       ├── users.py         # Admin-only user management
│       ├── reports.py
│       └── monitoring.py
├── database/
│   └── init.sql
├── docker-compose.yml
├── .env
└── README.md
```

## Quick Start

```bash
cd property_management_system
docker-compose up --build
```

Wait ~30-60 seconds for MySQL initialization.

| Service  | URL                    |
|----------|------------------------|
| Frontend | http://localhost:8501   |
| API      | http://localhost:5001   |

### Stop

```bash
docker-compose down        # Keep data
docker-compose down -v     # Remove all data
```

## Login Credentials

| Role    | Email               | Password     |
|---------|---------------------|--------------|
| Admin   | admin@proptech.com  | Password@123 |
| Manager | sarah@proptech.com  | Password@123 |
| Staff   | john@proptech.com   | Password@123 |

## Role-Based Access Control

| Page        | Admin | Manager | Staff |
|-------------|:-----:|:-------:|:-----:|
| Dashboard   | ✅    | ✅      | ✅    |
| Properties  | ✅    | ✅      | ❌    |
| Maintenance | ✅    | ✅      | ✅    |
| Users       | ✅    | ❌      | ❌    |
| Reports     | ✅    | ✅      | ❌    |
| Monitoring  | ✅    | ❌      | ❌    |

## Maintenance Workflow

```
Staff creates request
        ↓
   [Pending]
        ↓
Manager approves
        ↓
   [Approved]
        ↓
Manager assigns to staff
        ↓
   [Assigned]
        ↓
Staff starts work
        ↓
  [In Progress]
        ↓
Staff completes
        ↓
  [Completed]
        ↓
Manager closes
        ↓
    [Closed]
```

At any stage, managers can **Reject** → returns to Pending.

## API Endpoints

| Method | Endpoint           | Auth | Roles          |
|--------|--------------------|------|----------------|
| POST   | /login             | No   | All            |
| GET    | /profile           | Yes  | All            |
| GET    | /users             | Yes  | Admin, Manager |
| POST   | /users             | Yes  | Admin          |
| PUT    | /users/\<id\>      | Yes  | Admin          |
| DELETE | /users/\<id\>      | Yes  | Admin          |
| GET    | /dashboard         | Yes  | All            |
| GET    | /health            | No   | All            |
| GET    | /properties        | Yes  | All            |
| POST   | /properties        | Yes  | Admin, Manager |
| PUT    | /properties/\<id\> | Yes  | Admin, Manager |
| DELETE | /properties/\<id\> | Yes  | Admin          |
| GET    | /maintenance       | Yes  | All            |
| POST   | /maintenance       | Yes  | All            |
| PUT    | /maintenance/\<id\>| Yes  | All            |
| GET    | /reports           | Yes  | Admin, Manager |

## Database Schema

**users** — id, name, email, password_hash, role, status, created_at

**properties** — id, property_name, city, address, occupancy_status, monthly_revenue, created_at

**maintenance_requests** — id, property_id, title, description, status, assigned_to, approved_by, created_at

**audit_logs** — id, user_id, action, timestamp

## Requirements Compliance Checklist

| Requirement              | Status | Implementation                                    |
|--------------------------|:------:|---------------------------------------------------|
| Operational Dashboard    | ✅     | Dashboard page with KPIs, charts, activity feed   |
| Role-Based Access Control| ✅     | RBAC in sidebar, API decorators, page visibility   |
| User Management          | ✅     | Admin-only Users page with full CRUD               |
| Reporting & Analytics    | ✅     | Reports page with occupancy, revenue, maintenance  |
| Workflow Management      | ✅     | 7-status maintenance workflow with transitions     |
| Approval Chains          | ✅     | Manager approval required before assignment        |
| Monitoring & Alerting    | ✅     | Monitoring page with CPU/RAM/Disk/DB/API status    |
| Database-backed Records  | ✅     | MySQL 8 + SQLAlchemy ORM + audit logging           |
| Executive Reporting      | ✅     | Plotly charts + CSV export on all reports           |
| Scalability Planning     | ✅     | Docker Compose, connection pooling, health checks  |
| Property CRUD            | ✅     | Full create/read/update/delete with filters        |
| CSV Export               | ✅     | Download buttons on all three report types          |
| Audit Logging            | ✅     | All CRUD ops logged to audit_logs table            |
| Professional UI          | ✅     | Clean SaaS design, no AI-generated gradients       |
| Single Sidebar Nav       | ✅     | views/ directory instead of pages/                 |

## AWS EC2 Deployment

```bash
ssh -i key.pem ec2-user@<ip>
sudo yum install docker -y && sudo service docker start
sudo usermod -aG docker ec2-user
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
sudo chmod +x /usr/local/bin/docker-compose
cd property_management_system
docker-compose up --build -d
```

Open Security Group ports: **8501** (Frontend), **5001** (API).

---

**PropTech v2.0** — Built for production deployment.
# PropTech
