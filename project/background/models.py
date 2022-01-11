from datetime import timedelta
import logging

from django.utils import timezone
from django.db import models

logger = logging.getLogger(__name__)




class ContentType(models.Model):
    id = models.IntegerField('pk', primary_key=True)
    app_label = models.CharField(max_length=100, blank=True)
    model = models.CharField(max_length=100, blank=True)

    class Meta:
        managed = False
        db_table = 'django_content_type'


class Task(models.Model):


    id = models.IntegerField('pk', primary_key=True)
    task_name = models.CharField(max_length=190, blank=True)
    task_params = models.TextField(blank=True)
    task_hash = models.CharField(max_length=40, blank=True)
    verbose_name = models.CharField(max_length=255, null=True, blank=True)
    priority = models.IntegerField()
    run_at = models.DateTimeField()
    repeat = models.BigIntegerField()
    repeat_until = models.DateTimeField(null=True)
    queue = models.CharField(max_length=190, null=True, blank=True)
    attempts = models.IntegerField()
    failed_at = models.DateTimeField(null=True)
    last_error = models.TextField(blank=True)
    locked_by = models.CharField(max_length=64, null=True, blank=True)
    locked_at = models.DateTimeField(null=True)
    creator_object_id = models.IntegerField(null=True)
    creator_content_type = models.ForeignKey(ContentType, on_delete=models.DO_NOTHING, null=True)

    class Meta:
        managed = False
        db_table = 'background_task'
