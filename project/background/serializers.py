from rest_framework import serializers

from .models import Task

class TaskSerializer(serializers.ModelSerializer):
    run_at = serializers.DateTimeField(format="%d.%m.%y %H:%M:%S")
    failed_at = serializers.DateTimeField(format="%d.%m.%y %H:%M:%S")
    locked_at = serializers.DateTimeField(format="%d.%m.%y %H:%M:%S")
    class Meta:
        model = Task
        fields = ("id", "task_name", "task_params", "verbose_name", "priority", "run_at", "attempts", "failed_at", "last_error", "locked_by", "locked_at")

