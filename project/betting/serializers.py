from rest_framework import serializers

from project.core.helpers import DisplayChoiceField
from project.core.models import Match
from .models import (Odd, VOdd, BetType,
                     HarvestHandler, Harvest, HarvestConfig, HarvestGroup, 
                     ForecastHandler, Predictor, ForecastSet, Forecast, ForecastSandbox,
                     Distribution, Bet, BetOdd, Transaction
                     )


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


class BetTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BetType
        fields =    ("id", "slug", "name", "description", "handler",)


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

class DistributionSerializer(serializers.ModelSerializer):
    start_date = serializers.DateField(format="%d.%m.%Y")
    end_date = serializers.DateField(format="%d.%m.%Y")
    gathering_date = serializers.DateTimeField(format="%d.%m.%y %H:%M:%S")
    class Meta:
        model = Distribution
        fields = ("id", "slug", "name", "gathering_date", "start_date", "end_date", "interpolation", "step")


class ForecastMatchesSerializer(serializers.Serializer):
    match_id = serializers.IntegerField()
    league_name = serializers.CharField(max_length=100)
    name_h = serializers.CharField(max_length=100)
    name_a = serializers.CharField(max_length=100)
    match_score = serializers.CharField(max_length=20)
    match_date = serializers.DateField(format="%d.%m.%Y")
    odds = serializers.IntegerField()
    odds_plus = serializers.IntegerField()
    match_status = DisplayChoiceField(choices = Match.STATUS_CHOICES)
    best_chance = serializers.DecimalField(max_digits=10, decimal_places=3)
    best_result_value = serializers.DecimalField(max_digits=10, decimal_places=3)
    best_kelly = serializers.DecimalField(max_digits=10, decimal_places=3)


class ForecastSerializer(serializers.ModelSerializer):
    odd_status = DisplayChoiceField(choices = Odd.RESULT_CHOICES)
    growth = serializers.DecimalField(max_digits=10, decimal_places=3)
    class Meta:
        model = ForecastSandbox
        fields = ("id", "predictor", "success_chance", "lose_chance", "result_value", "kelly", "odd", "odd_status", "growth", )
        depth = 2


class PreviousMatchesSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    result = serializers.CharField(max_length=5)
    ha = serializers.CharField(max_length=5)
    match_date = serializers.DateField(format="%d.%m.%Y")
    score = serializers.CharField(max_length=20)
    team_h_id = serializers.IntegerField()
    team_a_id = serializers.IntegerField()
    h_name = serializers.CharField(max_length=100)
    a_name = serializers.CharField(max_length=100)
    gx = serializers.CharField(max_length=20)
    fore_gx = serializers.CharField(max_length=20)
    fore_g = serializers.CharField(max_length=20)


class SeasonChartSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    n = serializers.IntegerField()
    team_name = serializers.CharField(max_length=100)
    m = serializers.IntegerField()
    w = serializers.IntegerField()
    d = serializers.IntegerField()
    l = serializers.IntegerField()
    g = serializers.IntegerField()
    ga = serializers.IntegerField()
    pts = serializers.IntegerField()


class SelectedOddsSerializer(serializers.Serializer):
    id = serializers.IntegerField()
    league_id = serializers.IntegerField()
    match_id = serializers.IntegerField()
    select_id = serializers.IntegerField()
    odd_id = serializers.IntegerField()
    league_grp = serializers.IntegerField()
    match_grp = serializers.IntegerField()
    match_bid = serializers.IntegerField()
    name = serializers.CharField(max_length=255)
    success_chance = serializers.DecimalField(max_digits=10, decimal_places=3)
    lose_chance = serializers.DecimalField(max_digits=10, decimal_places=3)
    result_value = serializers.DecimalField(max_digits=10, decimal_places=3)
    kelly = serializers.DecimalField(max_digits=10, decimal_places=3)
    odd_value = serializers.DecimalField(max_digits=10, decimal_places=3)
    period = serializers.IntegerField()
    param = serializers.CharField(max_length=100)
    team = serializers.CharField(max_length=10)
    yes = serializers.CharField(max_length=10)
    bookie_name = serializers.CharField(max_length=255)
    predictor_name = serializers.CharField(max_length=255)
    selected = serializers.CharField(max_length=10)


class MyBetSerializer(serializers.ModelSerializer):
    status = DisplayChoiceField(choices = Bet.STATUS_CHOICES)
    result = DisplayChoiceField(choices = Bet.RESULT_CHOICES)
    betting_type = DisplayChoiceField(choices = Bet.BETTING_TYPE_CHOICES)
    ins_time = serializers.DateTimeField(format="%d.%m.%y %H:%M:%S")
    min_date = serializers.DateField(format="%d.%m.%y")
    max_date = serializers.DateField(format="%d.%m.%y")
    class Meta:
        model = Bet
        fields = ("id", "bookie", "name", "status", "result", "betting_type", "odd_cnt", "ins_time", "min_date", "max_date",
                  "success_chance", "lose_chance", "odd_value", "expect_value", "kelly", "bet_amt", "result_value", "win_amt",
                 )
        depth = 1


class BetOddSerializer(serializers.ModelSerializer):
    status = DisplayChoiceField(choices = Bet.STATUS_CHOICES)
    result = DisplayChoiceField(choices = Bet.RESULT_CHOICES)
    ins_time = serializers.DateTimeField(format="%d.%m.%y %H:%M:%S")
    settled_time = serializers.DateTimeField(format="%d.%m.%y %H:%M:%S")
    finish_time = serializers.DateTimeField(format="%d.%m.%y %H:%M:%S")
    match_date = serializers.DateField(format="%d.%m.%y")
    match_name = serializers.CharField(max_length=255)
    class Meta:
        model = BetOdd
        fields = ("id", "match", "odd", "status", "result", "ins_time", "settled_time", "finish_time", "predictor", "match_date",
                  "harvest", "success_chance", "lose_chance", "odd_value", "expect_value", "kelly", "result_value", "match_name",
                 )
        depth = 2


class TransactionSerializer(serializers.ModelSerializer):
    trans_type = DisplayChoiceField(choices = Transaction.TYPE_CHOICES)
    ins_time = serializers.DateTimeField(format="%d.%m.%y %H:%M:%S")
    trans_date = serializers.DateField(format="%d.%m.%y")
    class Meta:
        model = Transaction
        fields = ("id", "bookie", "trans_type", "trans_date", "ins_time", "amount", "comment", )
        depth = 1
    