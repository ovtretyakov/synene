from rest_framework import serializers

from project.core.helpers import DisplayChoiceField
from .models import Season


class SeasonSerializer(serializers.ModelSerializer):
    # league = serializers.SlugRelatedField(many=False, read_only=True, slug_field='name')
    start_date = serializers.DateField(format="%d.%m.%Y")
    end_date = serializers.DateField(format="%d.%m.%Y")
    # load_source = serializers.SlugRelatedField(many=False, read_only=True, slug_field='name')
    class Meta:
        model = Season
        fields = ("id", "name", "league", "start_date", "end_date", "load_source",)
        depth = 2

