from rest_framework import serializers

from project.core.helpers import DisplayChoiceField
from .models import Season, Match, MatchStats


class SeasonSerializer(serializers.ModelSerializer):
    # league = serializers.SlugRelatedField(many=False, read_only=True, slug_field='name')
    start_date = serializers.DateField(format="%d.%m.%Y")
    end_date = serializers.DateField(format="%d.%m.%Y")
    # load_source = serializers.SlugRelatedField(many=False, read_only=True, slug_field='name')
    class Meta:
        model = Season
        fields = ("id", "name", "league", "start_date", "end_date", "load_source",)
        depth = 2

class MatchSerializer(serializers.ModelSerializer):
    match_date = serializers.DateField(format="%d.%m.%Y")
    result = DisplayChoiceField(choices = Match.RESULT_CHOICES)
    class Meta:
        model = Match
        fields = ("id", "league", "season", "team_h", "team_a", "match_date", "score", "result", "load_source",)
        depth = 1


class MatchStatsSerializer(serializers.ModelSerializer):
    stat_type = DisplayChoiceField(choices = MatchStats.STAT_CHOICES)
    competitor = DisplayChoiceField(choices = MatchStats.COMPETITOR_CHOICES)
    class Meta:
        model = MatchStats
        fields = ("id", "stat_type", "competitor", "period", "value", "load_source",)
        depth = 1
