from decimal import Decimal, DecimalException

def clear_non_negative_integer(value):
    try:
        d = Decimal(value)
    except (ValueError, DecimalException):
        d = None
    if d != None and d != round(d):
        d = None
    if d != None and d < 0:
        d = None
    i = None if d==None else int(d)
    return i

def clear_non_negative_decimal(value):
    try:
        d = round(Decimal(value),3)
    except (ValueError, DecimalException):
        d = None
    if d != None and d < 0:
        d = None
    return d


class MatchDetail(object):
    def clear_match_context(self, 
                referee=None,forecast_w=0, forecast_d=0, forecast_l=0,
                name_h='', name_a=''):
        self.forecast_w = forecast_w
        self.forecast_d = forecast_d
        self.forecast_l = forecast_l
        self.referee    = referee if not referee == None else None
        self._h         = MatchTeamDetail()
        self._a         = MatchTeamDetail()
        self.odds       = []
        self.name_h     = name_h if not name_h else self.team_h.name
        self.name_a     = name_a if not name_a else self.team_a.name


    @property
    def h(self):
        return self._h

    @property
    def a(self):
        return self._a

    @property
    def result(self):
        if    self.h.goals == None or self.a.goals == None: ret = None
        elif  self.h.goals > self.a.goals: ret = 'w'
        elif  self.h.goals < self.a.goals: ret = 'l'
        else: ret = 'd'
        return ret

    @property
    def result_h(self):
        return self.result

    @property
    def result_a(self):
        if    self.h.goals == None or self.a.goals == None: ret = None
        elif  self.h.goals > self.a.goals: ret = 'l'
        elif  self.h.goals < self.a.goals: ret = 'w'
        else: ret = 'd'
        return ret

    def set_goals(self, h_goals, a_goals):
        ''' Set goals for hole match

        Arguments:
        h_goals    - home team goals
        a_goals    - against team goals
        '''
        self.set_half_goals(0, h_goals, a_goals)

    def set_half_goals(self, half, h_goals, a_goals):
        ''' Set goals for match half

        Arguments:
        half       - half of match(0-all match, 1, 2)
        h_goals    - home team goals
        a_goals    - against team goals
        '''
        self.h.set_half_detail(half, goals=h_goals)
        self.a.set_half_detail(half, goals=a_goals)

    def set_xG(self, h_xG, a_xG):
        ''' Set xG for hole match

        Arguments:
        h_xG    - home team xG
        a_xG    - against team xG
        '''
        self.set_half_xG(0, h_xG, a_xG)

    def set_half_xG(self, half, h_xG, a_xG):
        ''' Set xG for match half

        Arguments:
        half       - half of match(0-all match, 1, 2)
        h_xG    - home team xG
        a_xG    - against team xG
        '''
        self.h.set_half_detail(half, xG=h_xG)
        self.a.set_half_detail(half, xG=a_xG)

    def set_y_cards(self, h_y_cards, a_y_cards):
        ''' Set y_cards for hole match

        Arguments:
        h_y_cards    - home team y_cards
        a_y_cards    - against team y_cards
        '''
        self.set_half_y_cards(0, h_y_cards, a_y_cards)

    def set_half_y_cards(self, half, h_y_cards, a_y_cards):
        ''' Set y_cards for match half

        Arguments:
        half       - half of match(0-all match, 1, 2)
        h_y_cards    - home team y_cards
        a_y_cards    - against team y_cards
        '''
        self.h.set_half_detail(half, y_cards=h_y_cards)
        self.a.set_half_detail(half, y_cards=a_y_cards)

    def set_r_cards(self, h_r_cards, a_r_cards):
        ''' Set r_cards for hole match

        Arguments:
        h_r_cards    - home team r_cards
        a_r_cards    - against team r_cards
        '''
        self.set_half_r_cards(0, h_r_cards, a_r_cards)

    def set_half_r_cards(self, half, h_r_cards, a_r_cards):
        ''' Set r_cards for match half

        Arguments:
        half       - half of match(0-all match, 1, 2)
        h_r_cards    - home team r_cards
        a_r_cards    - against team r_cards
        '''
        self.h.set_half_detail(half, r_cards=h_r_cards)
        self.a.set_half_detail(half, r_cards=a_r_cards)

    def set_shots(self, h_shots=None, a_shots=None):
        if not h_shots == None: 
            value = clear_non_negative_integer(h_shots)
            if value == None:
                raise ValueError('Invalid h_shots param "%s" (should be integer)' % h_shots)
            self.h.shots = value
        if not a_shots == None: 
            value = clear_non_negative_integer(a_shots)
            if value == None:
                raise ValueError('Invalid a_shots param "%s" (should be integer)' % a_shots)
                self.h.shots = value
            self.a.shots = value

    def set_shots_on_target(self, h_shots_on_target=None, a_shots_on_target=None):
        if not h_shots_on_target == None: 
            value = clear_non_negative_integer(h_shots_on_target)
            if value == None:
                raise ValueError('Invalid h_shots_on_target param "%s" (should be integer)' % h_shots_on_target)
            self.h.shots_on_target = value
        if not a_shots_on_target == None: 
            value = clear_non_negative_integer(a_shots_on_target)
            if value == None:
                raise ValueError('Invalid a_shots_on_target param "%s" (should be integer)' % a_shots_on_target)
            self.a.shots_on_target = value

    def set_deep(self, h_deep=None, a_deep=None):
        if not h_deep == None: 
            value = clear_non_negative_integer(h_deep)
            if value == None:
                raise ValueError('Invalid h_deep param "%s" (should be integer)' % h_deep)
            self.h.deep = value
        if not a_deep == None: 
            value = clear_non_negative_integer(a_deep)
            if value == None:
                raise ValueError('Invalid a_deep param "%s" (should be integer)' % a_deep)
            self.a.deep = value

    def set_ppda(self, h_ppda=None, a_ppda=None):
        if not h_ppda == None: 
            value = clear_non_negative_decimal(h_ppda)
            if value == None:
                raise ValueError('Invalid h_ppda param "%s" (should be decimal)' % h_ppda)
            self.h.ppda = value
        if not a_ppda == None: 
            value = clear_non_negative_decimal(a_ppda)
            if value == None:
                raise ValueError('Invalid a_ppda param "%s" (should be decimal)' % a_ppda)
            self.a.ppda = value

    def add_h_event(self, minute, goals=None, xG=None, y_cards=None, r_cards=None):
        self.h.add_event(minute, goals, xG, y_cards, r_cards)

    def add_a_event(self, minute, goals=None, xG=None, y_cards=None, r_cards=None):
        self.a.add_event(minute, goals, xG, y_cards, r_cards)    


class MatchTeamDetail(object):
    """Team statistics in match"""
    def __init__(self):
        super(MatchTeamDetail, self).__init__()
        self._goals             = [None, None, None]
        self._xG                = [None, None, None]
        self._y_cards           = [None, None, None]
        self._r_cards           = [None, None, None]
        self._penalties         = [None, None, None]
        #information by minutes
        self._goals_minutes     = None
        self._xG_minutes        = None
        self._y_cards_minutes   = None
        self._r_cards_minutes   = None
        #statisics
        self.goal_time          = None # []
        self.shots              = None
        self.shots_on_target    = None
        self.deep               = None #Passes completed within an estimated 20 yards of goal (crosses excluded)
        self.ppda               = None #Passes allowed per defensive action in the opposition half
        self.corners            = None
        self.fouls              = None
        self.free_kicks         = None
        self.offsides           = None
        self.possession         = None

    def set_stats(self,
                goals=None, xG=None, y_cards=None, r_cards=None, penalties=None,
                goals_1st=None, xG_1st=None, y_cards_1st=None, r_cards_1st=None, penalties_1st=None,
                goals_2nd=None, xG_2nd=None, y_cards_2nd=None, r_cards_2nd=None, penalties_2nd=None,
                init_goals_minutes=False, init_xG_minutes=False, init_y_cards_minutes=False, init_r_cards_minutes=False,
                init_goals_times=False,
                shots=None, shots_on_target=None, deep=None, ppda=None, corners=None, fouls=None,
                free_kicks=None, offsides=None, possession=None):
        """Initialization team stats"""
        self.set_detail(goals, xG, y_cards, r_cards, penalties)
        self.set_half_detail(1, goals_1st, xG_1st, y_cards_1st, r_cards_1st, penalties_1st)
        self.set_half_detail(2, goals_2nd, xG_2nd, y_cards_2nd, r_cards_2nd, penalties_2nd)
        if init_goals_minutes:   self._goals_minutes   = MatchTeamDetail.get_empty_detail()
        if init_xG_minutes:      self._xG_minutes      = MatchTeamDetail.get_empty_detail()
        if init_y_cards_minutes: self._y_cards_minutes = MatchTeamDetail.get_empty_detail()
        if init_r_cards_minutes: self._r_cards_minutes = MatchTeamDetail.get_empty_detail()
        if init_goals_times: self.goal_time = []
        if not shots == None:
            value = clear_non_negative_integer(shots)
            if value == None:
                raise ValueError('Invalid shots param "%s" (should be integer)' % shots)
            self.shots = value
        if not shots_on_target == None:
            value = clear_non_negative_integer(shots_on_target)
            if value == None:
                raise ValueError('Invalid shots_on_target param "%s" (should be integer)' % shots_on_target)
            self.shots_on_target = value
        if not deep == None:
            value = clear_non_negative_integer(deep)
            if value == None:
                raise ValueError('Invalid deep param "%s" (should be integer)' % deep)
            self.deep = value
        if not ppda == None:
            value = clear_non_negative_decimal(ppda)
            if value == None:
                raise ValueError('Invalid ppda param "%s" (should be decimal)' % ppda)
            self.ppda = value
        if not corners == None:
            value = clear_non_negative_integer(corners)
            if value == None:
                raise ValueError('Invalid corners param "%s" (should be decimal)' % corners)
            self.corners = value
        if not fouls == None:
            value = clear_non_negative_integer(fouls)
            if value == None:
                raise ValueError('Invalid fouls param "%s" (should be decimal)' % fouls)
            self.fouls = value
        if not free_kicks == None:
            value = clear_non_negative_integer(free_kicks)
            if value == None:
                raise ValueError('Invalid free_kicks param "%s" (should be decimal)' % free_kicks)
            self.free_kicks = value
        if not offsides == None:
            value = clear_non_negative_integer(offsides)
            if value == None:
                raise ValueError('Invalid offsides param "%s" (should be decimal)' % offsides)
            self.offsides = value
        if not possession == None:
            value = clear_non_negative_decimal(possession)
            if value == None:
                raise ValueError('Invalid possession param "%s" (should be decimal)' % possession)
            self.possession = value
  
    @classmethod
    def get_empty_detail(cls):
        return {15:0,30:0,45:0,60:0,75:0,90:0,}

    def trunc_minute(minute):
        if minute <= 15: ret = 15
        elif minute <= 30: ret = 30
        elif minute <= 45: ret = 45
        elif minute <= 60: ret = 60
        elif minute <= 75: ret = 75
        else: ret = 90
        return ret

    def set_detail(self, goals=None, xG=None, y_cards=None, r_cards=None, penalties=None):
        self.set_half_detail(0, goals, xG, y_cards, r_cards, penalties)

    def set_half_detail(self, half, goals=None, xG=None, y_cards=None, r_cards=None, penalties=None):
        if not half == None:

            half = int(half)
            if not half in(0,1,2,):
                raise ValueError('Invalid half param "%s" (should be 0,1,2)' % half)

            if not goals == None:
                value = clear_non_negative_integer(goals)
                if value == None:
                    raise ValueError('Invalid goals param "%s" (should be integer)' % goals)
                self._goals[half] = value
            
            if not xG == None: 
                value = clear_non_negative_decimal(xG)
                if value == None:
                    raise ValueError('Invalid xG param "%s" (should be decimal)' % xG)
                self._xG[half] = value

            if not y_cards == None: 
                value = clear_non_negative_integer(y_cards)
                if value == None:
                    raise ValueError('Invalid y_cards param "%s" (should be integer)' % y_cards)
                self._y_cards[half] = value

            if not r_cards == None: 
                value = clear_non_negative_integer(r_cards)
                if value == None:
                    raise ValueError('Invalid r_cards param "%s" (should be integer)' % r_cards)
                self._r_cards[half] = value
            
            if not penalties == None: 
                value = clear_non_negative_integer(penalties)
                if value == None:
                    raise ValueError('Invalid penalties param "%s" (should be integer)' % penalties)
                self._penalties[half] = value

    def set_minute_detail(self, minute, goals=None, xG=None, y_cards=None, r_cards=None):
        if minute == None:
            raise ValueError('Invalid minute param "%s" (should be between 0 and 90)' % minute)
        minute0 = minute
        minute = int(minute)
        if minute < 0 :
            raise ValueError('Invalid minute param "%s" (should be between 0 and 90)' % minute0)
        minute = MatchTeamDetail.trunc_minute(minute)
        if minute <= 90:
            if not goals == None:
                value = clear_non_negative_integer(goals)
                if value == None:
                    raise ValueError('Invalid goals param "%s" (should be integer)' % goals)
                if self._goals_minutes == None: self._goals_minutes = MatchTeamDetail.get_empty_detail()
                self._goals_minutes[minute] = value

            if not xG == None: 
                value = clear_non_negative_decimal(xG)
                if value == None:
                    raise ValueError('Invalid xG param "%s" (should be decimal)' % xG)
                if self._xG_minutes == None: self._xG_minutes = MatchTeamDetail.get_empty_detail()
                self._xG_minutes[minute] = value
            
            if not y_cards == None:
                value = clear_non_negative_integer(y_cards)
                if value == None:
                    raise ValueError('Invalid y_cards param "%s" (should be integer)' % y_cards)
                if self._y_cards_minutes == None: self._y_cards_minutes = MatchTeamDetail.get_empty_detail()
                self._y_cards_minutes[minute] = value
            
            if not r_cards == None: 
                value = clear_non_negative_integer(r_cards)
                if value == None:
                    raise ValueError('Invalid r_cards param "%s" (should be integer)' % r_cards)
                if self._r_cards_minutes == None: self._r_cards_minutes = MatchTeamDetail.get_empty_detail()
                self._r_cards_minutes[minute] = value

    def add_event(self, minute, goals=None, xG=None, y_cards=None, r_cards=None, penalties=None):
        if minute == None:
            raise ValueError('Invalid minute param "%s" (should be between 0 and 90)' % minute)
        minute_save = minute
        minute = int(minute)
        if minute < 0 :
            raise ValueError('Invalid minute param "%s" (should be between 0 and 90)' % minute_save)
        minute0 = minute
        minute = MatchTeamDetail.trunc_minute(minute)
        if minute <= 45: 
            half = 1
        elif minute <= 90:
            half = 2
        else:
            return

        if not goals == None:
            value = clear_non_negative_integer(goals)
            if value == None:
                raise ValueError('Invalid goals param "%s" (should be integer)' % goals)
            if self.goal_time == None:
                self.goal_time = [minute0,]
            else: 
                self.goal_time.append(minute0)
            if not self._goals[0] == None: 
                self._goals[0] += value
            else:
                self._goals[0] = value
            if not self._goals[half] == None: 
                self._goals[half] += value
            else:
                self._goals[half] = value
            if self._goals_minutes == None: 
                self._goals_minutes = MatchTeamDetail.get_empty_detail()
            self._goals_minutes[minute] += value

        if not xG == None:
            value = clear_non_negative_decimal(xG)
            if value == None:
                raise ValueError('Invalid xG param "%s" (should be decimal)' % xG)
            if not self._xG[0] == None: 
                self._xG[0] = round(self._xG[0] + value,3)
            else:
                self._xG[0] = round(value,3)
            if not self._xG[half] == None: 
                self._xG[half] = round(self._xG[half] + value,3)
            else:
                self._xG[half] = round(value,3)
            if self._xG_minutes == None: 
                self._xG_minutes = MatchTeamDetail.get_empty_detail()
            self._xG_minutes[minute] = round(self._xG_minutes[minute] + value,3)

        if not y_cards == None:
            value = clear_non_negative_integer(y_cards)
            if value == None:
                raise ValueError('Invalid y_cards param "%s" (should be integer)' % y_cards)
            if not self._y_cards[0] == None: 
                self._y_cards[0] += value
            else:
                self._y_cards[0] = value
            if not self._y_cards[half] == None: 
                self._y_cards[half] += value
            else:
                self._y_cards[half] = value
            if self._y_cards_minutes == None: 
                self._y_cards_minutes = MatchTeamDetail.get_empty_detail()
            self._y_cards_minutes[minute] += value

        if not r_cards == None:
            value = clear_non_negative_integer(r_cards)
            if value == None:
                raise ValueError('Invalid r_cards param "%s" (should be integer)' % r_cards)
            if not self._r_cards[0] == None: 
                self._r_cards[0] += value
            else:
                self._r_cards[0] = value
            if not self._r_cards[half] == None: 
                self._r_cards[half] += value
            else:
                self._r_cards[half] = value
            if self._r_cards_minutes == None: 
                self._r_cards_minutes = MatchTeamDetail.get_empty_detail()
            self._r_cards_minutes[minute] += value
        
        if not penalties == None:
            value = clear_non_negative_integer(penalties)
            if value == None:
                raise ValueError('Invalid penalties param "%s" (should be integer)' % penalties)
            if not self._penalties[0] == None: 
                self._penalties[0] += value
            else:
                self._penalties[0] = value
            if not self._penalties[half] == None: 
                self._penalties[half] += value
            else:
                self._penalties[half] = value

    @property
    def goals(self):
        return self._goals[0]

    @property
    def xG(self):
        return self._xG[0]

    @property
    def y_cards(self):
        return self._y_cards[0]

    @property
    def r_cards(self):
        return self._r_cards[0]

    @property
    def penalties(self):
        return self._penalties[0]

    @property
    def goals_half(self):
        return self._goals

    @property
    def xG_half(self):
        return self._xG

    @property
    def y_cards_half(self):
        return self._y_cards

    @property
    def r_cards_half(self):
        return self._r_cards

    @property
    def penalties_half(self):
        return self._penalties

    @property
    def goals_minutes(self):
        return self._goals_minutes

    @property
    def xG_minutes(self):
        return self._xG_minutes

    @property
    def y_cards_minutes(self):
        return self._y_cards_minutes

    @property
    def r_cards_minutes(self):
        return self._r_cards_minutes

