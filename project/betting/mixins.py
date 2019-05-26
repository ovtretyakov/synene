import re

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

class EvenOddParam(object):
    @classmethod
    def clean_param(cls, param):
        param_ = param.strip().lower()
        if not param_ or param_ not in('even','odd',):
            raise ValueError('Invalid odd param (should be "even" or "odd"): %s' % param)
        return param_

###################################################################
# period
###################################################################
class OnlyMatchPeriod(object):
    @classmethod
    def clean_period(cls, period):
        if not period in(0,1,2,):
            raise ValueError('Invalid period param (valid: 0,1,2): %s' % period)
        return period

class OnlyFootballMinutes(object):
    @classmethod
    def clean_period(cls, period):
        if not period in(15,30,45,60,75,90,):
            raise ValueError('Invalid period param (valid: 15,30,45,60,75,90): %s' % period)
        return period

class Only0Period(object):
    @classmethod
    def clean_period(cls, period):
        if not period in(0,):
            raise ValueError('Invalid period param (valid: 0): %s' % period)
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
        if team:
            raise ValueError('Invalid team param (should be empty team): %s' % team)
        return team


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



