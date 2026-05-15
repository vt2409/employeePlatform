from django.db.models import Min, Max, Avg, Count, Sum
from rest_framework import viewsets, filters, status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .models import Employee
from .serializers import (
    EmployeeSerializer,
    EmployeeListSerializer,
    CountryInsightSerializer,
    JobTitleInsightSerializer,
    DepartmentInsightSerializer,
    OverviewSerializer,
)


class EmployeeViewSet(viewsets.ModelViewSet):
    """
    Full CRUD for employees.
    - GET    /api/employees/          → paginated list (active only by default)
    - POST   /api/employees/          → create
    - GET    /api/employees/{id}/     → retrieve
    - PUT    /api/employees/{id}/     → full update
    - PATCH  /api/employees/{id}/     → partial update
    - DELETE /api/employees/{id}/     → soft delete
    """

    queryset = Employee.objects.filter(is_active=True)
    serializer_class = EmployeeSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ["full_name", "job_title", "department", "country", "country_code"]
    ordering_fields = ["full_name", "salary", "date_joined", "department", "country"]
    ordering = ["full_name"]

    def get_serializer_class(self):
        if self.action == "list":
            return EmployeeListSerializer
        return EmployeeSerializer

    def get_queryset(self):
        qs = Employee.objects.all()

        # Allow ?active=all to include inactive employees
        active_param = self.request.query_params.get("active", "true")
        if active_param.lower() != "all":
            qs = qs.filter(is_active=True)

        # Optional filters
        country_code = self.request.query_params.get("country_code")
        department = self.request.query_params.get("department")
        employment_type = self.request.query_params.get("employment_type")

        if country_code:
            qs = qs.filter(country_code__iexact=country_code)
        if department:
            qs = qs.filter(department__iexact=department)
        if employment_type:
            qs = qs.filter(employment_type__iexact=employment_type)

        return qs

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()  # Soft delete
        return Response(
            {"detail": "Employee deactivated successfully."},
            status=status.HTTP_200_OK,
        )


# ── Insights Views ────────────────────────────────────────────────────────────

@api_view(["GET"])
def country_insights(request):
    """
    Min / Max / Avg salary and headcount grouped by country.
    Optional: ?country_code=IN
    """
    qs = Employee.objects.filter(is_active=True)
    country_code = request.query_params.get("country_code")
    if country_code:
        qs = qs.filter(country_code__iexact=country_code)

    data = (
        qs.values("country", "country_code", "currency")
        .annotate(
            headcount=Count("id"),
            min_salary=Min("salary"),
            max_salary=Max("salary"),
            avg_salary=Avg("salary"),
        )
        .order_by("country")
    )

    serializer = CountryInsightSerializer(data, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def job_title_insights(request):
    """
    Avg salary for each job title, optionally filtered by country.
    Optional: ?country_code=IN&job_title=Software Engineer
    """
    qs = Employee.objects.filter(is_active=True)
    country_code = request.query_params.get("country_code")
    job_title = request.query_params.get("job_title")

    if country_code:
        qs = qs.filter(country_code__iexact=country_code)
    if job_title:
        qs = qs.filter(job_title__iexact=job_title)

    data = (
        qs.values("job_title", "country", "country_code")
        .annotate(
            headcount=Count("id"),
            avg_salary=Avg("salary"),
        )
        .order_by("country", "job_title")
    )

    serializer = JobTitleInsightSerializer(data, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def department_insights(request):
    """
    Headcount, avg salary, and total payroll per department.
    """
    data = (
        Employee.objects.filter(is_active=True)
        .values("department")
        .annotate(
            headcount=Count("id"),
            avg_salary=Avg("salary"),
            total_payroll=Sum("salary"),
        )
        .order_by("-total_payroll")
    )

    serializer = DepartmentInsightSerializer(data, many=True)
    return Response(serializer.data)


@api_view(["GET"])
def overview_insights(request):
    """
    High-level org overview: total headcount, top earners, employment type breakdown.
    """
    all_employees = Employee.objects.all()
    active_employees = all_employees.filter(is_active=True)

    top_earners = active_employees.order_by("-salary")[:5]

    employment_breakdown = dict(
        active_employees.values_list("employment_type")
        .annotate(count=Count("id"))
        .values_list("employment_type", "count")
    )

    data = {
        "total_employees": all_employees.count(),
        "active_employees": active_employees.count(),
        "total_countries": active_employees.values("country_code").distinct().count(),
        "total_departments": active_employees.values("department").distinct().count(),
        "top_earners": top_earners,
        "employment_type_breakdown": employment_breakdown,
    }

    serializer = OverviewSerializer(data)
    return Response(serializer.data)
