from django import forms
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

from bootstrap_modal_forms.forms import BSModalForm

from .models import Task

######################################################################

class TaskDeleteForm(BSModalForm):
    object_id = forms.IntegerField()

    class Meta:
        model = Task
        fields = []

    def clean(self):
        cleaned_data = super().clean()
        object_id = cleaned_data.get("object_id")
        if not object_id:
            raise ValidationError(_("No task to delete"))

