from rest_framework import serializers

from project.core.helpers import DisplayChoiceField
from .models import Odd, VOdd, HarvestHandler, Harvest, HarvestConfig, HarvestGroup, ForecastHandler, Predictor, ForecastSet


class OddSerializer(serializers.ModelSerializer):
    match_date = serializers.DateField(format="%d.%m.%Y")
    result = DisplayChoiceField(choices = Odd.RESULT_CHOICES)

    class Meta:
        model = VOdd
        fields =    (
                    "id", 

                    "match_id", 
                    "match_name", 
                    "match_date", 

                    "league_id",
                    "league_name",
                    
                    "bookie_id", 
                    "bookie_name",

                    "bet_type_id",
                    "bet_type_name",

                    "value_type_id",
                    "value_type_name",

                    "period", 
                    "team", 
                    "param", 
                    "odd_value", 
                    "result", 
                    "result_value", 
                    )



class HarvestHandlerSerializer(serializers.ModelSerializer):
    class Meta:
        model = HarvestHandler
        fields = ("id", "slug", "name", "handler")

class HarvestSerializer(serializers.ModelSerializer):
    # harvest_handler = serializers.SlugRelatedField(many=False, read_only=True, slug_field='name')
    status = DisplayChoiceField(choices = Harvest.STATUS_CHOICES)
    class Meta:
        model = Harvest
        fields = ("id", "slug", "name", "harvest_handler", "value_type", "period", "status")
        depth = 1


class HarvestConfigSerializer(serializers.ModelSerializer):
    class Meta:
        model = HarvestConfig
        fields = ("id", "code", "value",)


class HarvestGroupSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    slug = serializers.SlugField(max_length=100)
    name = serializers.CharField(max_length=100)
    country_name = serializers.CharField(max_length=100)
    status = DisplayChoiceField(choices = HarvestGroup.STATUS_CHOICES)
    harvest_date = serializers.DateField(format="%d.%m.%Y")
    last_update = serializers.DateTimeField(format="%d.%m.%y %H:%M:%S")
    type = serializers.IntegerField()

class ForecastHandlerSerializer(serializers.ModelSerializer):
    class Meta:
        model = ForecastHandler
        fields = ("id", "slug", "name", "handler")

class PredictorSerializer(serializers.ModelSerializer):
    status = DisplayChoiceField(choices = Predictor.STATUS_CHOICES)
    class Meta:
        model = Predictor
        fields = ("id", "slug", "name", "forecast_handler", "harvest", "priority", "status", )
        depth = 1

class ForecastSetSerializer(serializers.ModelSerializer):
    status = DisplayChoiceField(choices = ForecastSet.STATUS_CHOICES)
    forecast_date = serializers.DateTimeField(format="%d.%m.%y %H:%M:%S")
    start_date = serializers.DateField(format="%d.%m.%Y")
    class Meta:
        model = ForecastSet
        fields = ("id", "slug", "name", "forecast_date", "forecast_time", "status", "match_cnt", "odd_cnt", 
                  "keep_only_best", "only_finished", "start_date")
        depth = 1

