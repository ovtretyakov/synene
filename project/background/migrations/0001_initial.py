# Generated by Django 2.2.1 on 2022-02-01 09:12

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ContentType',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False, verbose_name='pk')),
                ('app_label', models.CharField(blank=True, max_length=100)),
                ('model', models.CharField(blank=True, max_length=100)),
            ],
            options={
                'db_table': 'django_content_type',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.IntegerField(primary_key=True, serialize=False, verbose_name='pk')),
                ('task_name', models.CharField(blank=True, max_length=190)),
                ('task_params', models.TextField(blank=True)),
                ('task_hash', models.CharField(blank=True, max_length=40)),
                ('verbose_name', models.CharField(blank=True, max_length=255, null=True)),
                ('priority', models.IntegerField()),
                ('run_at', models.DateTimeField()),
                ('repeat', models.BigIntegerField()),
                ('repeat_until', models.DateTimeField(null=True)),
                ('queue', models.CharField(blank=True, max_length=190, null=True)),
                ('attempts', models.IntegerField()),
                ('failed_at', models.DateTimeField(null=True)),
                ('last_error', models.TextField(blank=True)),
                ('locked_by', models.CharField(blank=True, max_length=64, null=True)),
                ('locked_at', models.DateTimeField(null=True)),
                ('creator_object_id', models.IntegerField(null=True)),
            ],
            options={
                'db_table': 'background_task',
                'managed': False,
            },
        ),
    ]