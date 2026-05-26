from rest_framework import serializers

from .models import Employee


class EmployeeSerializer(serializers.ModelSerializer):

    active_tasks_count = serializers.IntegerField(read_only=True, default=0)

    class Meta:
        model = Employee
        fields = ["id", "full_name", "position", "created_at", "updated_at", "active_tasks_count"]
