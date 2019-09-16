from rest_framework import serializers

from project.core import models as CoreModels
from project.core.helpers import DisplayChoiceField
from .models import ErrorLog, SourceDetail, SourceSession


class LoadSourceSerializer(serializers.ModelSerializer):
    class Meta:
        model = CoreModels.LoadSource
        fields = ("id", "name", "reliability", "load_date", "error_limit", "is_loadable", "is_betting", "error_text")


class ErrorLogSerializer(serializers.ModelSerializer):
    load_source = serializers.SlugRelatedField(many=False, read_only=True, slug_field='name')
    error_time = serializers.DateTimeField(format="%d.%m.%y %H:%M:%S")
    class Meta:
        model = ErrorLog
        fields = ("id", "load_source", "error_text", "error_time", "league_name", "match_name")
        depth = 1


class SourceDetailSerializer(serializers.ModelSerializer):
    status = DisplayChoiceField(choices = SourceDetail.DETAIL_STATUS_CHOICES)
    last_update = serializers.DateTimeField(format="%d.%m.%y %H:%M:%S")
    class Meta:
        model = SourceDetail
        fields = ("slug", "last_update", "load_date", "league_name", "match_name", "status")


class SourceSessionsSerializer(serializers.ModelSerializer):
    status = DisplayChoiceField(choices = SourceSession.STATUS_CHOICES)
    start_time = serializers.DateTimeField(format="%d.%m.%y %H:%M:%S")
    end_time = serializers.DateTimeField(format="%d.%m.%y %H:%M:%S")
    class Meta:
        model = SourceSession
        fields = ("start_time", "end_time", "status", "match_cnt", "err_cnt")

class SourceAllSessionsSerializer(serializers.ModelSerializer):
    load_source = serializers.SlugRelatedField(many=False, read_only=True, slug_field='name')
    status = DisplayChoiceField(choices = SourceSession.STATUS_CHOICES)
    start_time = serializers.DateTimeField(format="%d.%m.%y %H:%M:%S")
    end_time = serializers.DateTimeField(format="%d.%m.%y %H:%M:%S")
    class Meta:
        model = SourceSession
        fields = ("id", "load_source", "start_time", "end_time", "status", "match_cnt", "err_cnt")
        depth = 1
