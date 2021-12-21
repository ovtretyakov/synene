from django import forms
from django.db import models
from django.utils.translation import ugettext_lazy as _
from django.core.exceptions import ValidationError
from django.template.defaultfilters import slugify

from bootstrap_modal_forms.forms import BSModalForm

from .models import HarvestHandler, Harvest, HarvestConfig, HarvestGroup, HarvestLeague

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
