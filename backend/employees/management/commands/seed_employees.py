"""
Seed 10,000 employees from first_names.txt + last_names.txt.

Performance strategy:
- Load name files into memory once.
- Use bulk_create() in batches of 1000 → minimises DB round trips.
- Idempotent: skips if 10,000 active employees already exist.

Usage:
    python manage.py seed_employees
    python manage.py seed_employees --count 500   # custom count
    python manage.py seed_employees --force        # re-seed even if data exists
"""

import random
import time
from datetime import date, timedelta
from pathlib import Path
from decimal import Decimal

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction

from employees.models import Employee, EmploymentType

# ── Static data ───────────────────────────────────────────────────────────────

COUNTRY_DATA = [
    {"country": "India", "country_code": "IN", "currency": "INR", "salary_range": (500000, 4000000)},
    {"country": "United States", "country_code": "US", "currency": "USD", "salary_range": (60000, 250000)},
    {"country": "United Kingdom", "country_code": "GB", "currency": "GBP", "salary_range": (35000, 150000)},
    {"country": "Germany", "country_code": "DE", "currency": "EUR", "salary_range": (45000, 160000)},
    {"country": "Canada", "country_code": "CA", "currency": "CAD", "salary_range": (55000, 180000)},
    {"country": "Australia", "country_code": "AU", "currency": "AUD", "salary_range": (65000, 200000)},
    {"country": "Singapore", "country_code": "SG", "currency": "SGD", "salary_range": (60000, 220000)},
    {"country": "Japan", "country_code": "JP", "currency": "JPY", "salary_range": (4000000, 15000000)},
]

DEPARTMENTS = [
    "Engineering",
    "Product",
    "Design",
    "Data Science",
    "Marketing",
    "Sales",
    "HR",
    "Finance",
    "Operations",
    "Customer Success",
]

JOB_TITLES_BY_DEPT = {
    "Engineering": ["Software Engineer", "Senior Software Engineer", "Staff Engineer", "Engineering Manager", "DevOps Engineer", "QA Engineer"],
    "Product": ["Product Manager", "Senior Product Manager", "Principal Product Manager", "Product Analyst"],
    "Design": ["UI Designer", "UX Designer", "Product Designer", "Design Lead"],
    "Data Science": ["Data Analyst", "Data Scientist", "ML Engineer", "Data Engineer", "Analytics Lead"],
    "Marketing": ["Marketing Manager", "Content Strategist", "SEO Specialist", "Growth Manager"],
    "Sales": ["Sales Executive", "Account Manager", "Sales Lead", "Business Development Manager"],
    "HR": ["HR Manager", "Recruiter", "HR Business Partner", "Talent Acquisition Lead"],
    "Finance": ["Financial Analyst", "Accountant", "Finance Manager", "Controller"],
    "Operations": ["Operations Manager", "Program Manager", "Business Analyst", "Ops Lead"],
    "Customer Success": ["Customer Success Manager", "Support Engineer", "Onboarding Specialist"],
}

EMPLOYMENT_TYPES = [choice[0] for choice in EmploymentType.choices]
EMPLOYMENT_WEIGHTS = [0.75, 0.15, 0.10]  # full-time heavy

BATCH_SIZE = 1000


class Command(BaseCommand):
    help = "Seed the database with employee records."

    def add_arguments(self, parser):
        parser.add_argument("--count", type=int, default=10000, help="Number of employees to create (default: 10000)")
        parser.add_argument("--force", action="store_true", help="Re-seed even if data already exists")

    def handle(self, *args, **options):
        count = options["count"]
        force = options["force"]

        existing = Employee.objects.filter(is_active=True).count()
        if existing >= count and not force:
            self.stdout.write(self.style.WARNING(
                f"Database already has {existing} active employees. Use --force to re-seed."
            ))
            return

        # Load name files
        data_dir = Path(__file__).resolve().parents[5] / "data"
        first_names = self._load_names(data_dir / "first_names.txt")
        last_names = self._load_names(data_dir / "last_names.txt")

        self.stdout.write(f"Loaded {len(first_names)} first names, {len(last_names)} last names.")
        self.stdout.write(f"Seeding {count} employees in batches of {BATCH_SIZE}...")

        start = time.perf_counter()
        created = self._seed(count, first_names, last_names)
        elapsed = time.perf_counter() - start

        self.stdout.write(self.style.SUCCESS(
            f"✓ Created {created} employees in {elapsed:.2f}s "
            f"({created / elapsed:.0f} records/sec)"
        ))

    def _load_names(self, filepath: Path) -> list[str]:
        if not filepath.exists():
            raise CommandError(f"Name file not found: {filepath}. Ensure data/ directory is mounted.")
        names = [line.strip() for line in filepath.read_text().splitlines() if line.strip()]
        if not names:
            raise CommandError(f"Name file is empty: {filepath}")
        return names

    def _seed(self, count: int, first_names: list, last_names: list) -> int:
        start_date = date(2015, 1, 1)
        end_date = date.today()
        date_range = (end_date - start_date).days

        employees = []
        for _ in range(count):
            dept = random.choice(DEPARTMENTS)
            country_info = random.choice(COUNTRY_DATA)
            salary_min, salary_max = country_info["salary_range"]

            employees.append(Employee(
                full_name=f"{random.choice(first_names)} {random.choice(last_names)}",
                job_title=random.choice(JOB_TITLES_BY_DEPT[dept]),
                department=dept,
                country=country_info["country"],
                country_code=country_info["country_code"],
                salary=Decimal(str(round(random.uniform(salary_min, salary_max), 2))),
                currency=country_info["currency"],
                employment_type=random.choices(EMPLOYMENT_TYPES, weights=EMPLOYMENT_WEIGHTS, k=1)[0],
                date_joined=start_date + timedelta(days=random.randint(0, date_range)),
                is_active=True,
            ))

        created_count = 0
        with transaction.atomic():
            for i in range(0, len(employees), BATCH_SIZE):
                batch = employees[i: i + BATCH_SIZE]
                Employee.objects.bulk_create(batch, batch_size=BATCH_SIZE)
                created_count += len(batch)
                self.stdout.write(f"  → {created_count}/{count} records inserted...")

        return created_count
