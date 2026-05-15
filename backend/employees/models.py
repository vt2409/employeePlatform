import uuid
from django.db import models


class EmploymentType(models.TextChoices):
    FULL_TIME = "Full-time", "Full-time"
    PART_TIME = "Part-time", "Part-time"
    CONTRACT = "Contract", "Contract"


class Employee(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    full_name = models.CharField(max_length=200)
    job_title = models.CharField(max_length=200)
    department = models.CharField(max_length=200)
    country = models.CharField(max_length=100)
    country_code = models.CharField(max_length=10)  # ISO alpha-2, e.g. "IN"
    salary = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=10, default="USD")
    employment_type = models.CharField(
        max_length=20,
        choices=EmploymentType.choices,
        default=EmploymentType.FULL_TIME,
    )
    date_joined = models.DateField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["full_name"]
        indexes = [
            models.Index(fields=["country_code"]),
            models.Index(fields=["job_title"]),
            models.Index(fields=["department"]),
            models.Index(fields=["is_active"]),
        ]

    def __str__(self):
        return f"{self.full_name} — {self.job_title} ({self.country_code})"

    def delete(self, *args, **kwargs):
        """Soft delete: preserve salary history."""
        self.is_active = False
        self.save(update_fields=["is_active", "updated_at"])
