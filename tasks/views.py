from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from .models import Task
from .serializers import TaskSerializers


class TaskViewSet(viewsets.ModelViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializers
    permission_classes = [IsAuthenticatedOrReadOnly]
