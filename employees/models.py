from django.db import models


class Employee(models.Model):

    full_name = models.CharField(max_length=255, verbose_name="ФИО", help_text="Введите полное имя сотрудника")
    position = models.CharField(max_length=255, verbose_name="Должность", help_text="Введите должность сотрудника")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата и время создания")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата и время последнего обновления")

    def __str__(self):
        return self.full_name
