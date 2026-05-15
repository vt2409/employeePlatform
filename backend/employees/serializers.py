from rest_framework import serializers
from .models import Employee, EmploymentType


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = [
            "id",
            "full_name",
            "job_title",
            "department",
            "country",
            "country_code",
            "salary",
            "currency",
            "employment_type",
            "date_joined",
            "is_active",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "created_at", "updated_at"]

    def validate_salary(self, value):
        if value <= 0:
            raise serializers.ValidationError("Salary must be a positive value.")
        return value

    def validate_employment_type(self, value):
        valid = [choice[0] for choice in EmploymentType.choices]
        if value not in valid:
            raise serializers.ValidationError(
                f"Invalid employment type. Must be one of: {valid}"
            )
        return value


class EmployeeListSerializer(serializers.ModelSerializer):
    """Lighter serializer for list views — omits audit timestamps."""

    class Meta:
        model = Employee
        fields = [
            "id",
            "full_name",
            "job_title",
            "department",
            "country",
            "country_code",
            "salary",
            "currency",
            "employment_type",
            "date_joined",
            "is_active",
        ]


# ── Insights serializers ──────────────────────────────────────────────────────

class CountryInsightSerializer(serializers.Serializer):
    country = serializers.CharField()
    country_code = serializers.CharField()
    currency = serializers.CharField()
    headcount = serializers.IntegerField()
    min_salary = serializers.DecimalField(max_digits=12, decimal_places=2)
    max_salary = serializers.DecimalField(max_digits=12, decimal_places=2)
    avg_salary = serializers.DecimalField(max_digits=12, decimal_places=2)


class JobTitleInsightSerializer(serializers.Serializer):
    job_title = serializers.CharField()
    country = serializers.CharField()
    country_code = serializers.CharField()
    headcount = serializers.IntegerField()
    avg_salary = serializers.DecimalField(max_digits=12, decimal_places=2)


class DepartmentInsightSerializer(serializers.Serializer):
    department = serializers.CharField()
    headcount = serializers.IntegerField()
    avg_salary = serializers.DecimalField(max_digits=12, decimal_places=2)
    total_payroll = serializers.DecimalField(max_digits=15, decimal_places=2)


class TopEarnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ["id", "full_name", "job_title", "department", "country", "salary", "currency"]


class OverviewSerializer(serializers.Serializer):
    total_employees = serializers.IntegerField()
    active_employees = serializers.IntegerField()
    total_countries = serializers.IntegerField()
    total_departments = serializers.IntegerField()
    top_earners = TopEarnerSerializer(many=True)
    employment_type_breakdown = serializers.DictField(child=serializers.IntegerField())
