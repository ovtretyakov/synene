# Generated by Django 2.2.1 on 2022-04-22 11:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0018_loadsource_saldo_amt'),
    ]

    operations = [
        migrations.AddField(
            model_name='loadsource',
            name='unsettled_amt',
            field=models.DecimalField(decimal_places=2, default=0, max_digits=10, verbose_name='Unsettled amt'),
        ),
        migrations.AddField(
            model_name='loadsource',
            name='unsettled_cnt',
            field=models.IntegerField(default=0, verbose_name='Unsettled cnt'),
        ),
    ]
