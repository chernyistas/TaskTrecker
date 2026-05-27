from django.db.models import Count, Q
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from employees.models import Employee

from .models import Task
from .serializers import TaskSerializers


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializers
    permission_classes = [IsAuthenticatedOrReadOnly]

    def _find_candidates_for_task(self, task):
        least_busy_employee = (
            Employee.objects.annotate(active_count=Count("tasks", filter=Q(tasks__status__in=["new", "in_progress"])))
            .order_by("active_count")
            .first()
        )
        if not least_busy_employee:
            return []

        least_busy_load = getattr(least_busy_employee, "active_count", 0)
        candidates = [least_busy_employee]

        if task.parent_task and task.parent_task.executor:
            parent_executor = task.parent_task.executor
            parent_load = Task.objects.filter(executor=parent_executor, status__in=["new", "in_progress"]).count()
            if parent_load <= least_busy_load + 2:
                if parent_executor not in candidates:
                    candidates.append(parent_executor)

        return candidates

    @action(detail=False, methods=["get"], url_path="important")
    def important_task(self, request):
        important_tasks = Task.objects.filter(status="new", children__status="in_progress").distinct()
        result = []
        for task in important_tasks:
            candidates = self._find_candidates_for_task(task)
            result.append(
                {
                    "task_name": task.name,
                    "deadline": task.deadline,
                    "candidates": [candidate.full_name for candidate in candidates],
                }
            )

        return Response(result)
