# Generated by Django 2.2.1 on 2019-05-05 15:26

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0003_auto_20190505_1804'),
    ]

    operations = [
        migrations.AddField(
            model_name='match',
            name='load_source',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.LoadSource'),
        ),
        migrations.AddField(
            model_name='referee',
            name='confirmed',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Confirmed'),
        ),
        migrations.AddField(
            model_name='referee',
            name='created',
            field=models.DateTimeField(blank=True, null=True, verbose_name='Created'),
        ),
        migrations.AddField(
            model_name='referee',
            name='load_status',
            field=models.CharField(choices=[('c', 'Confirmed'), ('u', 'Unconfirmed')], default='c', max_length=5, verbose_name='Status'),
        ),
        migrations.AlterField(
            model_name='referee',
            name='load_source',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='core_referee_load_source', to='core.LoadSource', verbose_name='Source'),
        ),
        migrations.CreateModel(
            name='RefereeLoadSource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField()),
                ('name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Object name')),
                ('status', models.CharField(choices=[('a', 'Active'), ('d', 'Deleted')], default='a', max_length=5, verbose_name='Status')),
                ('created', models.DateTimeField(blank=True, null=True, verbose_name='Created')),
                ('confirmed', models.DateTimeField(blank=True, null=True, verbose_name='Confirmed')),
                ('selected', models.DateTimeField(blank=True, null=True, verbose_name='Selected')),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='core_refereeloadsource_country', to='core.Country', verbose_name='Country')),
                ('load_source', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='core_refereeloadsource_load_source', to='core.LoadSource', verbose_name='Source')),
                ('referee', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='object', to='core.Referee', verbose_name='Referee')),
                ('sport', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='core_refereeloadsource_sport', to='core.Sport', verbose_name='Sport')),
            ],
        ),
        migrations.AddConstraint(
            model_name='refereeloadsource',
            constraint=models.UniqueConstraint(fields=('sport', 'country', 'slug', 'load_source'), name='unique_referee_load_source'),
        ),
    ]
