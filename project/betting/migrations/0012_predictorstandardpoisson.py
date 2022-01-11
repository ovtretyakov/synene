# Generated by Django 2.2.1 on 2021-12-26 20:26

from django.db import migrations
import project.betting.predictor_mixins


class Migration(migrations.Migration):

    dependencies = [
        ('betting', '0011_create_harvest_schema'),
    ]

    def init_forecasting_data(apps, schema_editor):

        ForecastHandler = apps.get_model('betting', 'ForecastHandler')
        Predictor = apps.get_model('betting', 'Predictor')
        Harvest = apps.get_model('betting', 'Harvest')

        forecast_handler = ForecastHandler.objects.create(
                                            slug = "xg-std-forecast", name = "xG Std Handler", handler = "PredictorStandardPoisson"
                                            )
        predictor = Predictor.objects.create(
                                            slug = "xg-std-0",
                                            name = "xG Std Predictor",
                                            forecast_handler = forecast_handler,
                                            harvest = Harvest.objects.filter(slug="hg-0").first(),
                                            priority = 10,
                                            status = 'a'
                                            )

    operations = [
        migrations.CreateModel(
            name='PredictorStandardPoisson',
            fields=[
            ],
            options={
                'proxy': True,
                'indexes': [],
                'constraints': [],
            },
            bases=(project.betting.predictor_mixins.StandartExtraction, project.betting.predictor_mixins.PoissonForecasting, 'betting.predictor'),
        ),

        migrations.RunPython(init_forecasting_data),

    ]