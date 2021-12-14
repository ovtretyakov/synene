# Generated by Django 2.2.1 on 2021-12-10 13:04

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0017_auto_20211210_1604'),
        ('betting', '0010_merge_20211205_2310'),
    ]

    operations = [
        migrations.CreateModel(
            name='ForecastHandler',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(unique=True)),
                ('name', models.CharField(max_length=100, verbose_name='Forecast Handler')),
                ('handler', models.CharField(blank=True, max_length=100, verbose_name='Handler')),
            ],
        ),
        migrations.CreateModel(
            name='Harvest',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(max_length=100, unique=True)),
                ('name', models.CharField(max_length=100, verbose_name='Script')),
                ('comment', models.CharField(blank=True, max_length=1000, verbose_name='Comment')),
                ('period', models.IntegerField(verbose_name='Period')),
                ('status', models.CharField(choices=[('a', 'Active'), ('n', 'Inactive')], default='n', max_length=5, verbose_name='Status')),
            ],
        ),
        migrations.CreateModel(
            name='HarvestGroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(max_length=100, unique=True)),
                ('name', models.CharField(max_length=100, verbose_name='Group')),
                ('status', models.CharField(choices=[('a', 'Active'), ('n', 'Inactive')], default='n', max_length=5, verbose_name='Status')),
                ('harvest_date', models.DateField(blank=True, null=True, verbose_name='Harvest date')),
                ('last_update', models.DateTimeField(blank=True, null=True, verbose_name='Last update')),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.Country', verbose_name='Country')),
                ('harvest', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='betting.Harvest', verbose_name='Harvest')),
            ],
        ),
        migrations.CreateModel(
            name='HarvestHandler',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(unique=True)),
                ('name', models.CharField(max_length=100, verbose_name='Harvest Type')),
                ('param_descr', models.CharField(blank=True, max_length=1000, verbose_name='Parameter Description')),
                ('handler', models.CharField(blank=True, max_length=100, verbose_name='Handler')),
            ],
        ),
        migrations.CreateModel(
            name='TeamSkill',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('event_date', models.DateField(verbose_name='Event date')),
                ('match_cnt', models.IntegerField(verbose_name='Match Count')),
                ('lvalue1', models.DecimalField(decimal_places=5, max_digits=10, verbose_name='LValue1')),
                ('lvalue2', models.DecimalField(decimal_places=5, max_digits=10, verbose_name='LValue1')),
                ('lvalue3', models.DecimalField(decimal_places=5, max_digits=10, verbose_name='LValue1')),
                ('lvalue4', models.DecimalField(decimal_places=5, max_digits=10, verbose_name='LValue1')),
                ('lvalue5', models.DecimalField(decimal_places=5, max_digits=10, verbose_name='LValue1')),
                ('lvalue6', models.DecimalField(decimal_places=5, max_digits=10, verbose_name='LValue1')),
                ('lvalue7', models.DecimalField(decimal_places=5, max_digits=10, verbose_name='LValue1')),
                ('lvalue8', models.DecimalField(decimal_places=5, max_digits=10, verbose_name='LValue1')),
                ('lvalue9', models.DecimalField(decimal_places=5, max_digits=10, verbose_name='LValue1')),
                ('lvalue10', models.DecimalField(decimal_places=5, max_digits=10, verbose_name='LValue1')),
                ('value1', models.DecimalField(decimal_places=5, max_digits=10, verbose_name='LValue1')),
                ('value2', models.DecimalField(decimal_places=5, max_digits=10, verbose_name='LValue1')),
                ('value3', models.DecimalField(decimal_places=5, max_digits=10, verbose_name='LValue1')),
                ('value4', models.DecimalField(decimal_places=5, max_digits=10, verbose_name='LValue1')),
                ('value5', models.DecimalField(decimal_places=5, max_digits=10, verbose_name='LValue1')),
                ('value6', models.DecimalField(decimal_places=5, max_digits=10, verbose_name='LValue1')),
                ('value7', models.DecimalField(decimal_places=5, max_digits=10, verbose_name='LValue1')),
                ('value8', models.DecimalField(decimal_places=5, max_digits=10, verbose_name='LValue1')),
                ('value9', models.DecimalField(decimal_places=5, max_digits=10, verbose_name='LValue1')),
                ('value10', models.DecimalField(decimal_places=5, max_digits=10, verbose_name='LValue1')),
                ('harvest_group', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='betting.HarvestGroup', verbose_name='Harvest Group')),
                ('match', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.Match', verbose_name='Match')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.Team', verbose_name='Team')),
            ],
        ),
        migrations.CreateModel(
            name='Predictor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(unique=True)),
                ('name', models.CharField(max_length=100, verbose_name='Predictor')),
                ('comment', models.CharField(blank=True, max_length=1000, verbose_name='Comment')),
                ('priority', models.IntegerField(verbose_name='Priority')),
                ('status', models.CharField(choices=[('a', 'Active'), ('n', 'Inactive')], default='n', max_length=5, verbose_name='Status')),
                ('forecast_handler', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='betting.ForecastHandler', verbose_name='Forecast Type')),
                ('harvest', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='betting.Harvest', verbose_name='Harvest')),
            ],
        ),
        migrations.CreateModel(
            name='HarvestLeague',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('harvest_group', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='betting.HarvestGroup', verbose_name='Harvest Group')),
                ('league', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.League', verbose_name='League')),
            ],
        ),
        migrations.CreateModel(
            name='HarvestConfig',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=100, verbose_name='Code')),
                ('value', models.CharField(blank=True, max_length=1000, verbose_name='Value')),
                ('harvest', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='betting.Harvest', verbose_name='Harvest')),
            ],
        ),
        migrations.AddField(
            model_name='harvest',
            name='harvest_handler',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='betting.HarvestHandler', verbose_name='Harvest Type'),
        ),
        migrations.AddField(
            model_name='harvest',
            name='sport',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.Sport', verbose_name='Sport'),
        ),
        migrations.AddField(
            model_name='harvest',
            name='value_type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='betting.ValueType', verbose_name='Vaue Type'),
        ),
        migrations.CreateModel(
            name='Forecast',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('set', models.CharField(default='m', max_length=10, verbose_name='Set')),
                ('success_chance', models.DecimalField(decimal_places=3, max_digits=10, verbose_name='LValue1')),
                ('lose_chance', models.DecimalField(decimal_places=3, max_digits=10, verbose_name='LValue1')),
                ('result_value', models.DecimalField(decimal_places=3, max_digits=10, verbose_name='Result value')),
                ('Kelly', models.DecimalField(decimal_places=3, max_digits=10, verbose_name='Kelly')),
                ('harvest', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='betting.Harvest', verbose_name='Harvest')),
                ('match', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.Match', verbose_name='Match')),
                ('odd', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='betting.Odd', verbose_name='Odd')),
                ('predictor', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='betting.Predictor', verbose_name='Predictor')),
            ],
        ),
        migrations.AddConstraint(
            model_name='teamskill',
            constraint=models.UniqueConstraint(fields=('harvest_group', 'team', 'event_date', 'match'), name='unique_team_skill'),
        ),
        migrations.AddConstraint(
            model_name='harvestleague',
            constraint=models.UniqueConstraint(fields=('harvest_group', 'league'), name='unique_harvest_league'),
        ),
        migrations.AddConstraint(
            model_name='harvestconfig',
            constraint=models.UniqueConstraint(fields=('harvest', 'code'), name='unique_harvest_conf'),
        ),
        migrations.AddConstraint(
            model_name='forecast',
            constraint=models.UniqueConstraint(fields=('set', 'odd', 'predictor'), name='unique_forecast'),
        ),
    ]
