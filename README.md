# Salary Manager

A minimal yet production-quality salary management tool for an organization with 10,000 employees.

**HR Manager persona** — manage employees, view salary insights by country, job title, and department.

---

## Project Overview

This is a full-stack application with:
- **Backend**: Django REST API with PostgreSQL database
- **Frontend**: React + Vite single-page application

Both applications run locally for development and can be deployed independently.

---

## Local Setup

### Step 1: Backend Setup

```bash
cd backend

# Create virtual environment
python -m venv .venv

# Activate virtual environment
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Seed 10,000 employees
python manage.py seed_employees

# Start the development server (runs on http://localhost:8000)
python manage.py runserver
```

### Step 2: Frontend Setup

Open a **new terminal** and run:

```bash
cd frontend

# Install dependencies
npm install

# Start the development server (runs on http://localhost:5173)
npm run dev
```

### Step 3: Access the Application

- **Frontend**: Open http://localhost:5173 in your browser
- **Backend API**: http://localhost:8000/api/

---

## Seeding Employees

```bash
# Default: 10,000 employees
python manage.py seed_employees

# Custom count
python manage.py seed_employees --count 500

# Force re-seed
python manage.py seed_employees --force
```

---

## Running Tests

```bash
cd backend

# pytest (with coverage)
pytest --cov=employees --cov-report=term-missing

# Django unittest
python manage.py test employees
```

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/employees/` | List (paginated, searchable) |
| POST | `/api/employees/` | Create employee |
| GET | `/api/employees/{id}/` | Retrieve |
| PATCH | `/api/employees/{id}/` | Update |
| DELETE | `/api/employees/{id}/` | Soft delete |
| GET | `/api/insights/country/` | Min/Max/Avg by country |
| GET | `/api/insights/job-title/` | Avg salary by job title |
| GET | `/api/insights/department/` | Dept headcount & payroll |
| GET | `/api/insights/overview/` | Org overview + top earners |

---

## Project Structure

```
salary-manager/
├── backend/
│   ├── config/           # Django settings, urls, wsgi
│   ├── employees/
│   │   ├── models.py
│   │   ├── serializers.py
│   │   ├── views.py
│   │   ├── urls.py
│   │   ├── admin.py
│   │   ├── management/commands/seed_employees.py
│   │   └── tests/
│   │       ├── factories.py
│   │       ├── test_models.py
│   │       ├── test_api.py
│   │       └── test_insights.py
│   └── manage.py
├── frontend/
│   └── src/
│       ├── App.jsx
│       ├── main.jsx
│       ├── services/api.js
│       └── pages/
│           ├── EmployeesPage.jsx
│           └── InsightsPage.jsx
├── data/
│   ├── first_names.txt
│   └── last_names.txt
├── docker-compose.yml
├── DESIGN.md
└── README.md
```
