import re
from decimal import Decimal, DecimalException

from core.utils import get_int

###################################################################
#  params
###################################################################
class WDLParam(object):
    @classmethod
    def clean_param(cls, param):
        param_ = param.strip().lower()
        if param_ == 'dw': param_ = 'wd'
        if param_ == 'ld': param_ = 'dl'
        if param_ == 'lw': param_ = 'wl'
        if not param_ or param_ not in('w','d','l','wd','dl','wl'):
            raise ValueError('Invalid odd param (should be wdl): %s' % param)
        return param_

class Double1X2Param(object):
    @classmethod
    def clean_param(cls, param):
        param_ = param.strip().upper()
        params = param_.split('/')
        if len(params)!=2 or not params[0] in['1','2','X',] or not params[1] in['1','2','X',]:
            raise ValueError('Invalid odd param (should be <1,2,X>/<1,2,X>): %s' % param)
        return param_

class EmptyParam(object):
    @classmethod
    def clean_param(cls, param):
        param_ = param.strip()
        if param_ == None: param_ = ''
        if param_:
            raise ValueError('Invalid odd param (should be empty): %s' % param)
        return param_

class ScoreListParam(object):
    score_pattern = re.compile(r"\d+:\d+") #2:1
    @classmethod
    def clean_param(cls, param):
        param_ = param.replace(' ','')
        if param_ == None: param_ = ''
        if not param_:
            raise ValueError('Invalid odd param. Should be list of scores (1:0 or 1:0,1:1,0:1): %s' % param)
        for score in param_.split(','):
            if not cls.score_pattern.search(score):
                raise ValueError('Invalid odd param. Should be list of scores (1:0 or 1:0,1:1,0:1): %s' % param)
        return param_

class PositiveIntegerParam(object):
    @classmethod
    def clean_param(cls, param):
        param_ = param.strip()
        if param_ == None or param_ == '':
            raise ValueError('Invalid odd param (must not be empty)')
        try:
            i = Decimal(param_)
        except (ValueError, DecimalException):
            raise ValueError('Invalid odd param. Should be integer: %s' % param)
        if i != round(i):
            raise ValueError('Invalid odd param. Should be integer: %s' % param)
        if i <= 0:
            raise ValueError('Invalid odd param. Should be positive integer: %s' % param)
        return param_

class IntegerListParam(object):
    @classmethod
    def clean_param(cls, param):
        param_ = param.replace(' ','')
        if param_ == None: param_ = ''
        for value in param_.split(','):
            if value == '':
                continue
            try:
                i = Decimal(value)
            except (ValueError, DecimalException):
                raise ValueError('Invalid odd param. Should be list of values (1 or 0,1,2): %s' % param)
            if i < 0:
                raise ValueError('Invalid odd param (should be positive): %s' % param)
            if i != round(i):
                raise ValueError('Invalid odd param. Should be list of values (1 or 0,1,2): %s' % param)
        return param_

class IntegerListOrEmptyParam(object):
    @classmethod
    def clean_param(cls, param):
        param_ = param.replace(' ','')
        if param_ == None: param_ = ''
        for value in param_.split(','):
            try:
                i = Decimal(value)
            except (ValueError, DecimalException):
                raise ValueError('Invalid odd param. Should be list of values (1 or 0,1,2): %s' % param)
            if i != round(i):
                raise ValueError('Invalid odd param. Should be list of values (1 or 0,1,2): %s' % param)
        return param_

class EvenOddParam(object):
    @classmethod
    def clean_param(cls, param):
        param_ = param.strip().lower()
        if not param_ or param_ not in('even','odd',):
            raise ValueError('Invalid odd param (should be "even" or "odd"): %s' % param)
        return param_

class TotalParam(object):
    @classmethod
    def clean_param(cls, param):
        param_ = param.strip()
        if param == None:
            raise ValueError('Invalid odd param (empty total value)')
        try:
            param_ = Decimal(param_.replace(',','.'))
        except (ValueError, DecimalException):
            raise ValueError('Invalid odd param (cannot be used as "total" parameter): %s' % param)
        if param_ <= 0:
            raise ValueError('Invalid odd param (must be a positive number): %s' % param)
        if int(4*param_) != 4*param_:
            raise ValueError('Invalid odd param (cannot be used as "total" parameter): %s' % param)
        if param_ == 0:
            param_ = '0'
        else:
            param_ = '{0:.2f}'.format(param_)
        return param_

class HandicapParam(object):
    @classmethod
    def clean_param(cls, param):
        param_ = param.strip()
        if param == None:
            raise ValueError('Invalid odd param (empty handicap value)')
        try:
            param_ = Decimal(param_.replace(',','.').replace(chr(int('0x2013',16)),'-'))
        except (ValueError, DecimalException):
            raise ValueError('Invalid odd param (cannot be used as "handicap" parameter): %s' % param)
        if int(4*param_) != 4*param_:
            raise ValueError('Invalid odd param (cannot be used as "handicap" parameter): %s' % param)
        if param_ == 0:
            param_ = '0'
        else:
            param_ = '{0:+.2f}'.format(param_)
        return param_

class HalfIntegerParam(object):
    @classmethod
    def clean_param(cls, param):
        param_ = param.strip()
        if param == None:
            raise ValueError('Invalid odd param (empty param)')
        try:
            param_ = Decimal(param_.replace(',','.'))
        except (ValueError, DecimalException):
            raise ValueError('Invalid odd param (should be "half-integer"): %s' % param)
        if param_ <= 0:
            raise ValueError('Invalid odd param (must be a positive number): %s' % param)
        if int(param_) == param_ or int(2*param_) != 2*param_:
            raise ValueError('Invalid odd param (should be "half-integer"): %s' % param)
        param_ = '{0:.1f}'.format(param_)
        return param_

class Two0or1Param(object):
    @classmethod
    def clean_param(cls, param):
        param_ = param.replace(' ','')
        if not param_ or param_ not in('0\\0','0\\1','1\\0','1\\1'):
            raise ValueError('Invalid odd param (should be 0\\0,0\\1,1\\0 or 1\\1): %s' % param)
        return param_

###################################################################
# period
###################################################################
class OnlyMatchPeriod(object):
    @classmethod
    def clean_period(cls, period, match="", bet_type="", source="", config=""):
        if not period in(0,1,2,):
            raise ValueError('Invalid period param (valid: 0,1,2): %s (match=%s, bet_type=%s, source=%s, config=%s)' % 
                              (period,match,bet_type,source,config))
        return period

class OnlyFootballMinutes(object):
    @classmethod
    def clean_period(cls, period, match="", bet_type="", source="", config=""):
        if not period in(15,30,45,60,75,90,):
            raise ValueError('Invalid period param (valid: 15,30,45,60,75,90): %s (match=%s, bet_type=%s, source=%s, config=%s)' %
                              (period,match,bet_type,source,config))
        return period

class Only0Period(object):
    @classmethod
    def clean_period(cls, period, match="", bet_type="", source="", config=""):
        if not period in(0,):
            raise ValueError('Invalid period param (valid: 0): %s (match=%s, bet_type=%s, source=%s, config=%s)' % 
                              (period,match,bet_type,source,config))
        return period

###################################################################
# team
###################################################################
class HomeOrAwayTeam(object):
    @classmethod
    def clean_team(cls, team):
        if team in('H','A'): team = team.lower()
        elif team.lower() == 'home': team = 'h'
        elif team.lower() == 'away': team = 'a'
        if not team in('h','a'):
            raise ValueError('Invalid team param (should be "h" or "a"): %s' % team)
        return team

class HomeAwayOrEmptyTeam(object):
    @classmethod
    def clean_team(cls, team):
        if team in('H','A'): team = team.lower()
        elif team.lower() == 'home': team = 'h'
        elif team.lower() == 'away': team = 'a'
        if not team in('h','a','',):
            raise ValueError('Invalid team param (should be "h", "a" or ""): %s' % team)
        return team

class OnlyEmptyTeam(object):
    @classmethod
    def clean_team(cls, team):
        if team == None or team:
            raise ValueError('Invalid team param (should be empty team): %s' % team)
        return team

###################################################################
# yes or no
###################################################################
class OnlyYes(object):
    @classmethod
    def clean_yes(cls, yes):
        if yes in('y',): yes = yes.upper()
        elif yes.lower() == 'yes': yes = 'Y'
        elif yes == '1': yes = 'Y'
        if not yes in('Y',):
            raise ValueError('Invalid yes-no param (should by "Y"): %s' % yes)
        return yes

###################################################################
# result
###################################################################
class WDLResult(object):
    def get_result(self):
        value_h, value_a = self.get_odd_values()
        value_h = get_int(value_h)
        value_a = get_int(value_a)
        if value_h == None or value_a == None: win = None
        elif self.param == 'w': win = (value_h > value_a)
        elif self.param == 'd': win = (value_h == value_a)
        elif self.param == 'l': win = (value_h < value_a)
        elif self.param == 'wd': win = (value_h >= value_a)
        elif self.param == 'dl': win = (value_h <= value_a)
        elif self.param == 'wl': win = (value_h != value_a)
        else: 
            raise ValueError('Invalid odd param (expected: w,d,l,wd,dl,wl): %s' % self.param)
        return self.calc_result_with_field_yes(win)



