# Salary Management Tool — Design Notes

## Overview
A minimal yet production-quality salary management tool for an organization with 10,000 employees.  
Target persona: **HR Manager**.

---

## Architecture

```
┌─────────────────────┐        ┌──────────────────────────┐
│   React + Ant Design│ <───>  │  Django REST Framework   │
│   (Vite, port 5173) │  HTTP  │  (port 8000)             │
└─────────────────────┘        └────────────┬─────────────┘
                                            │
                                ┌───────────▼──────────────┐
                                │     PostgreSQL            │
                                │   (port 5432)             │
                                └──────────────────────────┘
```

---

## Tech Stack Decisions

| Layer      | Choice               | Reason                                                   |
|------------|----------------------|----------------------------------------------------------|
| Backend    | Django 5 + DRF       | Mature, batteries-included, fast CRUD with serializers   |
| Database   | PostgreSQL           | Production-grade, excellent aggregation support          |
| Frontend   | React + Vite         | Fast HMR dev experience                                  |
| UI Library | Ant Design           | Enterprise-focused components; tables, charts, forms     |
| Container  | Docker Compose       | One-command local setup                                  |
| Testing    | pytest-django + unittest | Coverage + readable test structure                   |

---

## Employee Data Model

```
Employee
├── id (UUID)
├── full_name
├── job_title
├── department
├── country (ISO code, e.g., "IN", "US")
├── salary (Decimal)
├── currency (e.g., "INR", "USD")
├── employment_type (Full-time / Part-time / Contract)
├── date_joined
├── is_active
├── created_at
└── updated_at
```

**Why UUID?** Safer for external APIs — avoids sequential ID enumeration.

---

## API Design

```
GET    /api/employees/              List with pagination + search + filter
POST   /api/employees/              Create employee
GET    /api/employees/{id}/         Retrieve
PUT    /api/employees/{id}/         Full update
PATCH  /api/employees/{id}/         Partial update
DELETE /api/employees/{id}/         Soft delete (sets is_active=False)

GET    /api/insights/country/       Min/Max/Avg by country
GET    /api/insights/job-title/     Avg salary by job title + country
GET    /api/insights/overview/      Headcount, top earners, dept distribution
```

---

## Seed Script Strategy

- Django management command: `python manage.py seed_employees`
- Uses `bulk_create()` in batches of **1000** → minimizes DB round trips
- First/last names loaded into memory once from `data/first_names.txt` and `data/last_names.txt`
- Idempotent: checks existing count before seeding
- Target: seed 10,000 employees in under 10 seconds

---

## Insights Provided

1. **By Country**: min, max, avg salary; headcount
2. **By Job Title + Country**: avg salary
3. **Overview**: total headcount, top 5 earners, salary distribution by department
4. **Employment type breakdown** per country

---

## Trade-offs

- **Soft delete vs hard delete**: Chose soft delete (`is_active=False`) so salary history is preserved.
- **SQLite vs PostgreSQL**: PostgreSQL chosen for proper decimal handling and aggregation performance at 10k+ scale.
- **Pagination**: Server-side pagination (page size 20) to keep UI fast at 10k rows.
- **Currency**: Stored per employee; insights aggregate within same currency groups.

---

## AI Tools Used
- Claude (claude.ai) — architecture planning, boilerplate generation, test scaffolding
- All generated code reviewed and validated manually for correctness and production quality
