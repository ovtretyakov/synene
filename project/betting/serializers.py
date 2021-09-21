from rest_framework import serializers

from project.core.helpers import DisplayChoiceField
from .models import Odd, VOdd


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


