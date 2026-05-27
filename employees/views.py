from django.db.models import Count, Q
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny
from rest_framework.response import Response

from .models import Employee
from .serializers import EmployeeSerializer


class EmployeeViewSet(viewsets.ModelViewSet):
    queryset = Employee.objects.all()
    serializer_class = EmployeeSerializer
    permission_classes = [AllowAny]

    @action(detail=False, methods=["get"], url_path="busy")
    def busy_employees(self, request):
        employees = Employee.objects.annotate(
            active_tasks_count=Count("tasks", filter=Q(tasks__status__in=["new", "in_progress"]))
        ).order_by("active_tasks_count")
        serializer = self.get_serializer(employees, many=True)

        return Response(serializer.data)
