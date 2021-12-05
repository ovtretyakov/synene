from rest_framework import serializers

from project.core.helpers import DisplayChoiceField
from project.core.models import Loadable
from .models import FootballLeague, FootballTeam, FootballReferee


class FootballLeagueSerializer(serializers.ModelSerializer):
    team_type = serializers.SlugRelatedField(many=False, read_only=True, slug_field='name')
    country = serializers.SlugRelatedField(many=False, read_only=True, slug_field='name')
    load_status = DisplayChoiceField(choices = Loadable.STATUS_CHOICES)
    load_source = serializers.SlugRelatedField(many=False, read_only=True, slug_field='name')
    created = serializers.DateTimeField(format="%d.%m.%y %H:%M:%S")
    class Meta:
        model = FootballLeague
        fields = ("id", "name", "team_type", "country", "load_status", "load_source", "created")
        depth = 1

class FootballTeamSerializer(serializers.ModelSerializer):
    load_status = DisplayChoiceField(choices = Loadable.STATUS_CHOICES)
    created = serializers.DateTimeField(format="%d.%m.%y %H:%M:%S")
    class Meta:
        model = FootballTeam
        fields = ("id", "name", "team_type", "country", "load_status", "load_source", "created", )
        depth = 1

class FootballRefereeSerializer(serializers.ModelSerializer):
    load_status = DisplayChoiceField(choices = Loadable.STATUS_CHOICES)
    created = serializers.DateTimeField(format="%d.%m.%y %H:%M:%S")
    class Meta:
        model = FootballReferee
        fields = ("id", "name", "country", "load_status", "load_source", "created", )
        depth = 1
