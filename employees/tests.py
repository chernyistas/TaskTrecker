from datetime import date, timedelta

from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient, APITestCase

from employees.models import Employee
from tasks.models import Task


class EmployeeTestCase(APITestCase):
    """Тестирование класса сотрудников"""

    def setUp(self):
        """Создаём тестовые данные"""

        self.client = APIClient()

        self.employee1 = Employee.objects.create(full_name="Иван Иваныч", position="Developer")
        self.employee2 = Employee.objects.create(full_name="Мария Петровна", position="QA")

    def test_get_employees_list(self):
        """Тест на получение списка сотрудников"""
        url = reverse("employee-list")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data["results"]), 2)
        self.assertEqual(response.data["results"][0]["full_name"], "Иван Иваныч")
        self.assertEqual(response.data["results"][1]["full_name"], "Мария Петровна")

    def test_create_employee(self):
        """Тест на создание сотрудника"""
        url = reverse("employee-list")

        data = {"full_name": "Пётр Петрович", "position": "Team Lead"}
        response = self.client.post(url, data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Employee.objects.count(), 3)
        self.assertEqual(response.data["full_name"], "Пётр Петрович")

    def test_update_employee(self):
        """Тест на обновление сотрудника"""
        url = reverse("employee-detail", args=[self.employee1.id])
        data = {"full_name": "Иван Петрович", "position": "Senior Developer"}
        response = self.client.put(url, data)

        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.employee1.refresh_from_db()

        self.assertEqual(self.employee1.full_name, "Иван Петрович")

    def test_delete_employee(self):
        """Тест на удаление сотрудника"""
        url = reverse("employee-detail", args=[self.employee2.id])
        response = self.client.delete(url)

        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Employee.objects.count(), 1)

    def test_busy_employees_endpoint(self):
        """Тест на сортировку п загруженности"""
        future_date = date.today() + timedelta(days=30)

        Task.objects.create(name="Задача 1", executor=self.employee1, deadline=future_date, status="in_progress")
        Task.objects.create(name="Задача 2", executor=self.employee1, deadline=future_date, status="new")
        Task.objects.create(name="Задача 3", executor=self.employee2, deadline=future_date, status="done")

        url = reverse("employee-busy-employees")
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]["full_name"], "Мария Петровна")
        self.assertEqual(response.data[0]["active_tasks_count"], 0)

        self.assertEqual(response.data[1]["full_name"], "Иван Иваныч")
        self.assertEqual(response.data[1]["active_tasks_count"], 2)
