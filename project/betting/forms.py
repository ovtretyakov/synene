from django import forms
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.template.defaultfilters import slugify

from bootstrap_modal_forms.forms import BSModalForm

from project.core.models import Match
from .models import (HarvestHandler, Harvest, HarvestConfig, HarvestGroup, HarvestLeague,
                    ForecastHandler, Predictor, ForecastSet,
                    Distribution
                    )

######################################################################
class HarvestHandlerForm(BSModalForm):

    class Meta:
        model = HarvestHandler
        fields = ["slug", "name", "param_descr", "handler",]

    def clean_slug(self):
        data = slugify(self.cleaned_data["slug"])
        return data


class HarvestHandlerDeleteForm(BSModalForm):
    object_id = forms.IntegerField()

    class Meta:
        model = HarvestHandler
        fields = []

    def clean(self):
        cleaned_data = super().clean()
        object_id = cleaned_data.get("object_id")
        if not object_id:
            raise ValidationError(_("No handler to delete"))

######################################################################
class HarvestForm(BSModalForm):

    class Meta:
        model = Harvest
        fields = ["slug", "name", "comment", "sport", "harvest_handler", "value_type", "period", "status",]

    def clean_slug(self):
        data = slugify(self.cleaned_data["slug"])
        return data

class HarvestDeleteForm(BSModalForm):
    object_id = forms.IntegerField()

    class Meta:
        model = Harvest
        fields = []

    def clean(self):
        cleaned_data = super().clean()
        object_id = cleaned_data.get("object_id")
        if not object_id:
            raise ValidationError(_("No harvestor to delete"))

class HarvestDoHarvestForm(BSModalForm):

    harvest_date = forms.DateField(required=False)
    class Meta:
        model = Harvest
        fields = ["slug", "name", ]


class HarvestDoHarvestAllForm(BSModalForm):

    harvest_date = forms.DateField(required=False)
    class Meta:
        model = Harvest
        fields = []


######################################################################
class HarvestConfigForm(BSModalForm):

    class Meta:
        model = HarvestConfig
        fields = ["harvest", "code", "value",]

class HarvestConfigDeleteForm(BSModalForm):
    object_id = forms.IntegerField()

    class Meta:
        model = HarvestConfig
        fields = []

    def clean(self):
        cleaned_data = super().clean()
        object_id = cleaned_data.get("object_id")
        if not object_id:
            raise ValidationError(_("No configuration parameter to delete"))


######################################################################
class HarvestGroupForm(BSModalForm):

    class Meta:
        model = HarvestGroup
        fields = ["slug", "name", "harvest", "country", "status", "harvest_date",]

class HarvestGroupDeleteForm(BSModalForm):
    object_id = forms.IntegerField()

    class Meta:
        model = HarvestGroup
        fields = []

    def clean(self):
        cleaned_data = super().clean()
        object_id = cleaned_data.get("object_id")
        if not object_id:
            raise ValidationError(_("No harvestor group to delete"))

class HarvestGroupDoHarvestForm(BSModalForm):

    class Meta:
        model = HarvestGroup
        fields = ["slug", "name", "harvest_date",]

######################################################################
class HarvestLeagueForm(BSModalForm):

    class Meta:
        model = HarvestLeague
        fields = ["harvest_group", "league",]

class HarvestLeagueDeleteForm(BSModalForm):
    object_id = forms.IntegerField()

    class Meta:
        model = HarvestLeague
        fields = []

    def clean(self):
        cleaned_data = super().clean()
        object_id = cleaned_data.get("object_id")
        if not object_id:
            raise ValidationError(_("No harvestor league to delete"))

######################################################################
class ForecastHandlerForm(BSModalForm):

    class Meta:
        model = ForecastHandler
        fields = ["slug", "name", "handler",]

    def clean_slug(self):
        data = slugify(self.cleaned_data["slug"])
        return data


class ForecastHandlerDeleteForm(BSModalForm):
    object_id = forms.IntegerField()

    class Meta:
        model = ForecastHandler
        fields = []

    def clean(self):
        cleaned_data = super().clean()
        object_id = cleaned_data.get("object_id")
        if not object_id:
            raise ValidationError(_("No handler to delete"))

######################################################################
class PredictorForm(BSModalForm):

    class Meta:
        model = Predictor
        fields = ["slug", "name", "forecast_handler", "harvest", "priority", "status", ]

    def clean_slug(self):
        data = slugify(self.cleaned_data["slug"])
        return data

class PredictorDeleteForm(BSModalForm):
    object_id = forms.IntegerField()

    class Meta:
        model = Predictor
        fields = []

    def clean(self):
        cleaned_data = super().clean()
        object_id = cleaned_data.get("object_id")
        if not object_id:
            raise ValidationError(_("No predictor to delete"))

######################################################################
class ForecastSetForm(BSModalForm):
    delete_old = forms.BooleanField(required=False)

    class Meta:
        model = ForecastSet
        fields = ["slug", "name", "start_date", ]

    def clean_slug(self):
        data = slugify(self.cleaned_data["slug"])
        return data

class ForecastSetDeleteForm(BSModalForm):
    object_id = forms.IntegerField()

    class Meta:
        model = ForecastSet
        fields = []

    def clean(self):
        cleaned_data = super().clean()
        object_id = cleaned_data.get("object_id")
        if not object_id:
            raise ValidationError(_("No predictor to delete"))


######################################################################
class DistributionForm(BSModalForm):

    class Meta:
        model = Distribution
        fields = ["slug", "name", "comment", "gathering_handler", "start_date", "end_date", "interpolation", "step", ]

    def clean_slug(self):
        data = slugify(self.cleaned_data["slug"])
        return data


class DistributionGatherForm(BSModalForm):

    class Meta:
        model = Distribution
        fields = ["slug", "name", "start_date", "end_date",  ]


class DistributionDeleteForm(BSModalForm):
    object_id = forms.IntegerField()

    class Meta:
        model = Distribution
        fields = []

    def clean(self):
        cleaned_data = super().clean()
        object_id = cleaned_data.get("object_id")
        if not object_id:
            raise ValidationError(_("No predictor to delete"))

######################################################################
class MatchXGForm(BSModalForm):

    xG_h = forms.DecimalField(max_digits=10, decimal_places=3, localize=True)
    xA_h = forms.DecimalField(max_digits=10, decimal_places=3, localize=True)
    G_h  = forms.DecimalField(max_digits=10, decimal_places=3, localize=True)
    A_h  = forms.DecimalField(max_digits=10, decimal_places=3, localize=True)
    xG_a = forms.DecimalField(max_digits=10, decimal_places=3, localize=True)
    xA_a = forms.DecimalField(max_digits=10, decimal_places=3, localize=True)
    G_a  = forms.DecimalField(max_digits=10, decimal_places=3, localize=True)
    A_a  = forms.DecimalField(max_digits=10, decimal_places=3, localize=True)

    class Meta:
        model = Match
        fields = []
        
    def clean_xG_h(self):
        data = self.cleaned_data["xG_h"]
        if data is None or data < 0:
            raise ValidationError(_("This field must be greater than 0"))
        return data
    def clean_xA_h(self):
        data = self.cleaned_data["xA_h"]
        if data is None or data < 0:
            raise ValidationError(_("This field must be greater than 0"))
        return data
    def clean_G_h(self):
        data = self.cleaned_data["G_h"]
        if data is None or data < 0:
            raise ValidationError(_("This field must be greater than 0"))
        return data
    def clean_A_h(self):
        data = self.cleaned_data["A_h"]
        if data is None or data < 0:
            raise ValidationError(_("This field must be greater than 0"))
        return data
    def clean_xG_a(self):
        data = self.cleaned_data["xG_a"]
        if data is None or data < 0:
            raise ValidationError(_("This field must be greater than 0"))
        return data
    def clean_xA_a(self):
        data = self.cleaned_data["xA_a"]
        if data is None or data < 0:
            raise ValidationError(_("This field must be greater than 0"))
        return data
    def clean_G_a(self):
        data = self.cleaned_data["G_a"]
        if data is None or data < 0:
            raise ValidationError(_("This field must be greater than 0"))
        return data
    def clean_A_a(self):
        data = self.cleaned_data["A_a"]
        if data is None or data < 0:
            raise ValidationError(_("This field must be greater than 0"))
        return data


######################################################################
class RestoreMatchXGForm(BSModalForm):

    class Meta:
        model = Match
        fields = []


######################################################################
class ProcessAllForm(BSModalForm):

    only_betting = forms.BooleanField(required=False)
    process_date = forms.DateField(required=False)
    forecast_set_name = forms.CharField(max_length=100)

    class Meta:
        model = Match
        fields = []

    def clean_forecast_set_name(self):
        data = self.cleaned_data["forecast_set_name"]
        if not ForecastSet.objects.filter(slug=data).exists():
            raise ValidationError(_("Unknown forecast set"))
        return data

