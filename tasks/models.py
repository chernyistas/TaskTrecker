from django.db import models

from employees.models import Employee


class Task(models.Model):

    STATUS_CHOICES = [
        ("new", "Новая"),
        ("in_progress", "В работе"),
        ("done", "Выполнена"),
    ]

    name = models.CharField(max_length=255, verbose_name="Наименование", help_text="Введите название задачи")
    parent_task = models.ForeignKey(
        "self",
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="children",
        verbose_name="Родительская задача",
        help_text="Задача, от которой зависит текущая",
    )
    executor = models.ForeignKey(
        Employee,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="tasks",
        verbose_name="Исполнитель",
        help_text="Выберите сотрудника, ответственного за задачу",
    )
    deadline = models.DateField(
        verbose_name="Срок выполнения", help_text="Укажите дату выполнения задачи (ГГГГ-ММ-ДД)"
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="new",
        verbose_name="Статус",
        help_text="Текущий статус выполнения задачи",
    )
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата и время создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата и время последнего обновления")

    class Meta:
        verbose_name = "Задача"
        verbose_name_plural = "Задачи"
        ordering = ["-created_at"]

    def __str__(self):
        return f"{self.name}-{self.status}"
