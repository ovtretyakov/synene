# Generated by Django 2.2.1 on 2019-05-14 18:29

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_auto_20190512_2217'),
    ]

    operations = [
        migrations.AddField(
            model_name='matchstats',
            name='load_source',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.LoadSource'),
        ),
    ]
