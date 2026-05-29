from datetime import date, timedelta

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from employees.models import Employee
from tasks.models import Task


class TaskTestCase(APITestCase):
    """Тестирование класса задач"""

    def setUp(self):
        """Создаем тестовые данные"""
        self.client = APIClient()

        self.employee1 = Employee.objects.create(full_name="Иван Иваныч", position="Developer")
        self.employee2 = Employee.objects.create(full_name="Пётр Петрович", position="Senior")

        self.future_date = date.today() + timedelta(days=30)
        self.past_date = date.today() - timedelta(days=1)

    def test_create_success_task(self):
        """Тест на успешное создание задачи"""
        url = reverse("task-list")
        data = {"name": "Новая задача", "executor": self.employee1.id, "deadline": self.future_date, "status": "new"}

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Task.objects.count(), 1)
        self.assertEqual(response.data["name"], "Новая задача")

    def test_task_deadline_validation_past_date(self):
        """Тест на создание задачи с дедлайном в прошлом"""
        url = reverse("task-list")
        data = {"name": "Просроченная задача", "executor": self.employee1, "deadline": self.past_date, "status": "new"}

        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("deadline", response.data)

    def test_task_parent_task_self_reference(self):
        """Тест на то, что нельзя назначить задачу родителем самой себя"""
        url = reverse("task-list")
        data = {"name": "Задача", "executor": self.employee1.id, "deadline": self.future_date, "status": "new"}
        response = self.client.post(url, data)
        task_id = response.data["id"]

        update_url = reverse("task-detail", args=[task_id])
        update_data = {
            "name": "Задача",
            "executor": self.employee1.id,
            "deadline": self.future_date,
            "status": "new",
            "parent_task": task_id,
        }

        response = self.client.put(update_url, update_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn("parent_task", response.data)

    def test_important_task_endpoint(self):
        """Тест на поиск важных задач и кандидатов"""
        parent_task = Task.objects.create(
            name="Родительская важная задача", executor=None, deadline=self.future_date, status="new"
        )

        Task.objects.create(
            name="Дочерняя задача в работе",
            parent_task=parent_task,
            executor=self.employee2,
            deadline=self.future_date,
            status="in_progress",
        )

        url = reverse("task-important-task")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]["task_name"], "Родительская важная задача")

        candidates = response.data[0]["candidates"]
        self.assertIn("Иван Иваныч", candidates)

    def test_regular_tasks_not_in_important(self):
        """Тест на то, что обычные задачи не попадают в important"""
        Task.objects.create(name="Обычная задача", executor=self.employee1, deadline=self.future_date, status="new")
        parent_without_children = Task.objects.create(
            name="Родитель без детей в работе", executor=self.employee1, deadline=self.future_date, status="new"
        )
        Task.objects.create(
            name="Дочка нового родителя", parent_task=parent_without_children, deadline=self.future_date, status="new"
        )

        url = reverse("task-important-task")
        response = self.client.get(url)

        self.assertEqual(len(response.data), 0)

    def test_update_task(self):
        """Тест на обновление задачи"""

        task = Task.objects.create(
            name="Старое название", executor=self.employee1, deadline=self.future_date, status="new"
        )

        url = reverse("task-detail", args=[task.id])
        data = {
            "name": "Новое название",
            "executor": self.employee2.id,
            "deadline": self.future_date,
            "status": "in_progress",
        }

        response = self.client.put(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        task.refresh_from_db()
        self.assertEqual(task.name, "Новое название")
        self.assertEqual(task.status, "in_progress")

    def test_delete_task(self):
        """Тест на удаление задачи"""
        task = Task.objects.create(name="Задача", executor=self.employee1, deadline=self.future_date, status="new")

        self.assertEqual(Task.objects.count(), 1)

        url = reverse("task-detail", args=[task.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Task.objects.count(), 0)

    def test_get_task_list(self):
        """Тест на получение списка задач"""
        Task.objects.create(name="Задача1", executor=self.employee1, deadline=self.future_date, status="new")
        Task.objects.create(name="Задача2", executor=self.employee2, deadline=self.future_date, status="in_progress")
        Task.objects.create(name="Задача3", executor=self.employee1, deadline=self.future_date, status="done")

        url = reverse("task-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 3)
