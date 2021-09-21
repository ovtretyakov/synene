from decimal import Decimal

from django import forms
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError

from bootstrap_modal_forms.forms import BSModalForm

from project.core.models import LoadSource

######################################################################
class LoadSourceForm(BSModalForm):

    # max_odd = forms.DecimalField(max_digits=6,decimal_places=2,initial=5.00,required=True)

    class Meta:
        model = LoadSource
        fields = ["slug", "name", "reliability", "source_handler", "source_url",
                    "is_loadable", "is_betting", "is_error", "error_text", 
                    "load_date", "min_odd", "max_odd", "error_limit",  "load_days",]
        widgets = {
                    "min_odd": forms.TextInput(attrs={"localization": True}),
                    "max_odd": forms.TextInput(attrs={"localization": True}),
                    }

    def __init__(self, *args, **kwargs):
        if "instance" in kwargs:
            kwargs["instance"].min_odd = kwargs["instance"].min_odd.quantize(Decimal("0.01"))
            kwargs["instance"].max_odd = kwargs["instance"].max_odd.quantize(Decimal("0.01"))
        super(LoadSourceForm, self).__init__(*args, **kwargs) 
        # self.fields["min_odd"].decimal_places = 2
        # self.fields["max_odd"].decimal_places = 2

    def clean_min_odd(self):
        data = self.cleaned_data["min_odd"]
        if data < 0:
            raise ValidationError(_("This field must be greater than 0"))
        return data
    def clean_max_odd(self):
        data = self.cleaned_data["max_odd"]
        if data < 0:
            raise ValidationError(_("This field must be greater than 0"))
        return data
    def clean_error_limit(self):
        data = self.cleaned_data["error_limit"]
        if data < 0:
            raise ValidationError(_("This field must be greater than 0"))
        return data
    def clean_load_days(self):
        data = self.cleaned_data["load_days"]
        if data < 0:
            raise ValidationError(_("This field must be greater than 0"))
        return data

    def clean(self):
        cleaned_data = super().clean()
        min_odd = cleaned_data.get("min_odd")
        max_odd = cleaned_data.get("max_odd")
        if min_odd > max_odd:
            raise ValidationError(_("Parameter \"Max Odd\" must be grater than  \"Min Odd\""))


######################################################################
class LoadSourceProcessForm(BSModalForm):

    local_files = forms.BooleanField(required=False)

    class Meta:
        model = LoadSource
        fields = ["local_files",]

    # def clean(self):
    #     cleaned_data = super().clean()
    #     raise ValidationError(_("Processing error"))
