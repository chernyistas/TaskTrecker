from datetime import date

from rest_framework import serializers

from .models import Task


class TaskSerializers(serializers.ModelSerializer):
    class Meta:
        model = Task
        fields = "__all__"

    def validate_deadline(self, value):
        if value < date.today():
            raise serializers.ValidationError("Дедлайн не может быть в прошлом!")
        return value

    def validate_parent_task(self, value):
        if value and self.instance and value == self.instance:
            raise serializers.ValidationError("Задача не может быть создателем самой себя")
        return value
