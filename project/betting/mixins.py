from django.utils.translation import ugettext_lazy as _
from django.forms import ValidationError

###################################################################
class WDLParamClean(object):
    @classmethod
    def clean_param(cls, param):
        param = param.strip().lower()
        if param == 'dw': param = 'wd'
        if param == 'ld': param = 'dl'
        if param == 'lw': param = 'wl'
        if param == None or param not in('w','d','l','wd','dl','wl'):
            ValidationError(_('Invalid odd param: %(param)s'), params={'param': param},  code='invalid_param')
        return param
