from rest_framework import serializers

class DisplayChoiceField(serializers.ChoiceField):
    def __init__(self, *args, **kwargs):
        choices = kwargs.get('choices')
        self._choices = choices
        super(DisplayChoiceField, self).__init__(*args, **kwargs)

    def to_representation(self, obj):
        """Used while retrieving value for the field."""
        return self._choices[obj]
