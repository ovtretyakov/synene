import os
import time
from decimal import Decimal
from datetime import datetime, date, timedelta
import traceback
import logging
import requests

from django.db import models, transaction
from django.db.models import F
from django.utils import timezone
from django.conf import settings
from django.template.defaultfilters import slugify

from project.core.models import Country, Sport, LoadSource, League, Team, Match, MatchStats, Referee
from project.betting.models import Odd, ValueType, OddBookieConfig
from .exceptions import LoadError, TooMamyErrors
from .helpers import MatchDetail


logger = logging.getLogger(__name__)

###################################################################
class CommonHandler(MatchDetail, LoadSource):

    class Meta:
        proxy = True

    def get_load_date(self, default_date=date(2010, 1, 1)):
        if self.source_detail:
            load_date = self.source_detail.load_date if self.source_detail.load_date else default_date
        else:
            load_date = self.load_date if self.load_date else default_date
        return load_date

    @classmethod
    def get_sport(cls):
        return Sport.objects.get(slug=Sport.FOOTBALL)

    @classmethod
    def get_handler_dir(cls):
        return settings.SOURCE_DIR

    def get_request(self, url):
        is_error = True
        for i in range(1,5):
            try:
                time.sleep(1)
                r = requests.get(url)
                break
            except requests.exceptions.RequestException as e:
                if i == 4: 
                    logger.error(type(self).__name__ + ': RequestException while getting url "%s"' % url) 
                    raise e
                else:
                    logger.warning(type(self).__name__ + ': can not get "%s" %s' % (url, i)) 
                time.sleep(5*i)
        return r

    def get_html(self, file_name, url=None, get_from_file=False, is_debug_path=True):
        ''' Get html from url or saved file
            
            Parameters:
            file_name     - file name (save to or load from)
            url           - 
            get_from_file - get from url or from file 
            is_debug_path - if get from file - where file is placed (in debug or saved directory)
        '''
        hpath = self.get_handler_dir()
        if get_from_file:
            if is_debug_path:
                hpath = hpath.path('debug')
            else:
                hpath = hpath.path('cache')
            fname = hpath.path(file_name)
            html = open(fname, 'rb').read()
        else:
            fname = hpath.path('cache').path(file_name)
            r = self.get_request(url)
            html = r.text
            file = open(fname, 'wb')
            file.write(html.encode())
            file.close()
        self.file_name = fname
        return html


    def get_config(self, code):
        try:
            config = OddBookieConfig.objects.get(bookie=self, code=code)
        except OddBookieConfig.DoesNotExist:
            config = None
        return config

    def clear_handicap_param(self, param):
      ''' clear handicap param
          0 -> 0
          0.0 -> 0
          +0 -> 0
          -1,5 -> -1.5
          2.5 -> +2.5
      '''
      p0 = param.replace(',','.').replace(chr(int('0x2013',16)),'-')
      # print(param, p0, chr(int('0x2013',16)))
      # print(param, hex(ord(param[0])), chr(int(hex(ord(param[0])),16)) )
      p = Decimal(p0)
      if p == 0:
        s = '0'
      else:
        s = '{0:+.2f}'.format(p)
      return s

    def clear_total_param(self, param):
      if param == None: return None
      p = Decimal(param.replace(',','.'))
      if p == 0:
        s = '0'
      else:
        s = '{0:.2f}'.format(p)
      return s

    def clear_contents(self):
        self.source_session = None
        self.load_continue = False
        self.match_date = None
        self.league_name = None
        self.team_h = None
        self.team_a = None
        self.match = None
        self.match_name = None
        self.file_name = None
        self.context = None
        self.source_detail = None
        self.source_detail_league = None
        self.source_detail_match = None

    def handle_exception(self, e, raise_finish_error=True):
        logger.error(type(self).__name__ + ':')
        logger.exception(e)
        if self.source_session:
            try:
                #check if session exists
                self.source_session = SourceSession.objects.get(pk=self.source_session.pk)
            except SourceSession.DoesNotExist:
                self.source_session = None
        #Save error
        with transaction.atomic():
            error_text = str(e)[:255]
            if not error_text:
                error_text = "Load Error"
            ErrorLog.objects.create(
                                load_source = self,
                                source_session = self.source_session,
                                error_text = error_text,
                                error_context = str(self.context),
                                error_traceback = traceback.format_exc(),
                                error_time = timezone.now(),
                                league_name = '' if not self.league_name else self.league_name[:100],
                                match_name = '' if not self.match_name else self.match_name[:100],
                                file_name = '' if not self.file_name else self.file_name[:100],
                                source_detail = self.source_detail)
            self.is_error = True
            self.error_text = error_text
            self.save()
        if self.source_session:
            #check error count
            finish_loading = False
            with transaction.atomic():
                self.lock()
                self.source_session.refresh_from_db()
                self.source_session.err_cnt += 1
                if self.source_session.err_cnt >= self.error_limit:
                    self.source_session.status = SourceSession.ERROR
                    finish_loading = True
                self.source_session.save()
        if finish_loading and raise_finish_error:
            raise TooMamyErrors("Too many errors")

    def _start_or_skip_league(self, league_name, season_name='NA'):
        try:
            source_detail_league = SourceDetailLeague.objects.get(
                                        source_detail = self.source_detail,
                                        season_name = season_name,
                                        league_name = league_name)
        except SourceDetailLeague.DoesNotExist:
            source_detail_league = None
        if not source_detail_league:
            source_detail_league = SourceDetailLeague.objects.create(
                                        source_detail = self.source_detail,
                                        season_name = season_name,
                                        league_name = league_name,
                                        status = SourceDetail.IN_PROCESS)
            do_action = True
        else:
            do_action = (source_detail_league.status == SourceDetail.IN_PROCESS)
        self.source_detail_league = source_detail_league
        if do_action and self.source_detail:
            self.source_detail.league_name = league_name
            self.source_detail.last_update = timezone.now()
            self.source_detail.save()
            self.league_name = league_name
        return do_action


    def _start_or_skip_match(self, match_date, match_name):
        try:
            source_detail_match = SourceDetailMatch.objects.get(
                                        source_detail = self.source_detail,
                                        match_date = match_date,
                                        match_name = match_name)
        except SourceDetailMatch.DoesNotExist:
            source_detail_match = None
        if not source_detail_match:
            if not self.source_detail_league:
                do_action = self._start_or_skip_league(league_name='NA')
            else:
                do_action = True
            if do_action:
                source_detail_match = SourceDetailMatch.objects.create(
                                            source_detail = self.source_detail,
                                            source_detail_league = self.source_detail_league,
                                            match_date = match_date,
                                            match_name = match_name,
                                            status = SourceDetail.IN_PROCESS)
        else:
            do_action = (source_detail_match.status == SourceDetail.IN_PROCESS)
        self.source_detail_match = source_detail_match
        return do_action

    def _start_detail(self, slug):
        try:
            source_detail = SourceDetail.objects.get(load_source=self, slug=slug)
        except SourceDetail.DoesNotExist:
            source_detail = None
        if source_detail:
            if source_detail.status == SourceSession.FINISHED and (not source_detail.load_date or 
                                                                   self.load_date and source_detail.load_date > self.load_date
                                                                   ):
                source_detail.load_date = self.load_date
            #update old detail
            source_detail.last_update = timezone.now()
            source_detail.source_session = self.source_session
            source_detail.status = SourceSession.IN_PROCESS
            source_detail.save()
        else:
            #create new detail
            source_detail = SourceDetail.objects.create(
                            load_source = self,
                            slug = slug,
                            last_update = timezone.now(),
                            load_date = None,
                            league_name = '',
                            match_name = '',
                            source_session = self.source_session,
                            status = SourceSession.IN_PROCESS)
        self.source_detail = source_detail


    def set_load_date(self, load_date, is_set_main=False):
        try:
            with transaction.atomic():
                self.lock()
                if self.source_detail:
                    self.source_detail.set_load_date(load_date)
                if not self.source_detail or is_set_main:
                    self.load_date = load_date
                    self.save()
            self.match_date = load_date
        except Exception as e:
            self.handle_exception(e)
            raise LoadError


    def start_or_skip_league(self, league_name, country=None, season_name='NA', detail_slug=None, league_slug=None):
        try:
            with transaction.atomic():
                self.lock()

                if not country:
                    #try to find country from league name
                    league_upper = league_name.upper()
                    if not (league_upper.find('WORLD') >= 0):
                        i = 0
                        for c in Country.objects.raw(
                                    "SELECT * FROM core_country WHERE %s LIKE '%%' || UPPER(nationality) || '%%'",
                                    [league_upper]):
                            country = c
                            i += 1
                            if i >= 2:
                                break
                        if i > 1:
                            country = None

                logger.debug("League.get_or_create name=<%s> slug=<%s>" % (league_name,league_slug))
                self.league = League.get_or_create(
                                            sport=self.get_sport(),
                                            name=league_name,
                                            country=country,
                                            load_source=self,
                                            slug=league_slug)

                if not self.league:
                    logger.info(type(self).__name__ + ': Skip league ' + league_name)
                    do_action = False
                else:
                    do_action = True

                if do_action:
                    if detail_slug:
                        self._start_detail(detail_slug)
                    do_action = self._start_or_skip_league(league_name, season_name=season_name)

                if do_action:
                    logger.info(type(self).__name__ + ': Start league ' + league_name)
        except Exception as e:
            self.handle_exception(e)
            raise LoadError
        return do_action


    def create_league_session(self, start_date, end_date, load_source, name=None):
        try:
            with transaction.atomic():
                self.lock()
                if self.league:
                    season = self.league.get_or_create_season(start_date, end_date, self, name)
                    msg = ' Create or update session %s - %s(%s to %s)' % (str(self.league.name), season.name, start_date, end_date)
                    logger.debug(type(self).__name__ + ': ' + msg)
        except Exception as e:
            self.handle_exception(e)
            raise LoadError('Error creating session')


    def finish_league(self):
        try:
            with transaction.atomic():
                self.lock()
                if self.source_detail_league:
                    logger.info(type(self).__name__ + ': Finish league ' + self.source_detail_league.league_name)
                    self.source_detail_league.status=SourceDetail.FINISHED
                    self.source_detail_league.save()
        except Exception as e:
            self.handle_exception(e)
        finally:
            self.source_detail_league = None
            self.league_name = None


    def start_or_skip_match(self, name_h, name_a, match_status=Match.FINISHED, match_date=None,
                                referee=None, forecast_w=0, forecast_d=0, forecast_l=0):
        try:
            if not match_date:
                match_date = self.match_date
            with transaction.atomic():
                self.lock()
                slug_h = slugify(name_h)
                slug_h = slug_h if len(slug_h) < 30 else slug_h[:30]
                team_type = None
                if self.league:
                    team_type = self.league.team_type
                self.team_h = Team.get_or_create(
                                        sport=self.get_sport(),
                                        name=name_h,
                                        slug=slug_h,
                                        team_type = team_type,
                                        country=self.league.country,
                                        load_source=self)
                slug_a = slugify(name_a)
                slug_a = slug_a if len(slug_a) < 30 else slug_a[:30]
                self.team_a = Team.get_or_create(
                                        sport=self.get_sport(),
                                        name=name_a,
                                        slug=slug_a,
                                        team_type = team_type,
                                        country=self.league.country,
                                        load_source=self)
                do_action = (self.team_h != None and self.team_a != None)
                if do_action:
                    self.match = Match.get_or_create(
                                        league=self.league,
                                        team_h=self.team_h,
                                        team_a=self.team_a,
                                        match_date=match_date,
                                        load_source=self, 
                                        status=match_status)
                    do_action = self._start_or_skip_match(
                                        match_date=match_date, 
                                        match_name=str(self.match))
                if do_action:
                    if referee:
                        referee = Referee.get_or_create(
                                                sport=self.get_sport(),
                                                name=referee,
                                                country=self.league.country,
                                                load_source=self)
                    self.clear_match_context(
                                        referee=referee,
                                        forecast_w=forecast_w, forecast_d=forecast_d, forecast_l=forecast_l,
                                        name_h=name_h, name_a=name_a)
        except Exception as e:
            self.handle_exception(e)
            raise LoadError
        return do_action

    def _save_statistic(self, stat_type, competitor, period, value):
        self.match.add_stat(stat_type, competitor, period, value, self)


    def _save_competitor_data(self, competitor, data):
        for p in range(0,3):
            if data._goals[p] != None:
                self._save_statistic(Match.GOALS, competitor, p, data._goals[p])
            if data._xG[p] != None:
                self._save_statistic(Match.XG, competitor, p, data._xG[p])
            if data._y_cards[p] != None:
                self._save_statistic(Match.YCARD, competitor, p, data._y_cards[p])
            if data._r_cards[p] != None:
                self._save_statistic(Match.RCARD, competitor, p, data._r_cards[p])
            if data._penalties[p] != None:
                self._save_statistic(Match.PENALTY, competitor, p, data._penalties[p])
        for k in sorted(data.get_empty_detail().keys()):
            if data._goals_minutes != None:
                self._save_statistic(Match.GOALS_MINUTE, competitor, k, data._goals_minutes[k])
            if data._xG_minutes != None:
                self._save_statistic(Match.XG_MINUTE, competitor, k, data._xG_minutes[k])
            if data._y_cards_minutes != None:
                self._save_statistic(Match.YCARD_MINUTE, competitor, k, data._y_cards_minutes[k])
            if data._r_cards_minutes != None:
                self._save_statistic(Match.RCARD_MINUTE, competitor, k, data._r_cards_minutes[k])
        if data.goal_time != None:
            value = ','.join(str(t) for t in data.goal_time)
            self._save_statistic(Match.GOAL_TIME, competitor, 0, value)
        if data.shots != None:
            self._save_statistic(Match.SHOTS, competitor, 0, data.shots)
        if data.shots_on_target != None:
            self._save_statistic(Match.SHOTS_ON_TARGET, competitor, 0, data.shots_on_target)
        if data.deep != None:
            self._save_statistic(Match.DEEP, competitor, 0, data.deep)
        if data.ppda != None:
            self._save_statistic(Match.PPDA, competitor, 0, data.ppda)
        if data.corners != None:
            self._save_statistic(Match.CORNERS, competitor, 0, data.corners)
        if data.fouls != None:
            self._save_statistic(Match.FOULS, competitor, 0, data.fouls)
        if data.free_kicks != None:
            self._save_statistic(Match.FREE_KICKS, competitor, 0, data.free_kicks)
        if data.offsides != None:
            self._save_statistic(Match.OFFSIDES, competitor, 0, data.offsides)
        if data.possession != None:
            self._save_statistic(Match.POSSESSION, competitor, 0, data.possession)


    def finish_match(self):
        try:
            with transaction.atomic():
                self.lock()
                if self.source_detail_match:
                    if self.referee: 
                        self.match.set_referee(self.referee, self)
                    self._save_competitor_data(Match.COMPETITOR_HOME, self.h)
                    self._save_competitor_data(Match.COMPETITOR_AWAY, self.a)
                    for odd in self.odds:
                        # logger.debug(odd)
                        bet_type_slug = odd.pop('bet_type',None)
                        value_type_slug = odd.pop('value_type',None)
                        if not value_type_slug:
                            value_type_slug = ValueType.MAIN
                        bookie = self if self.is_betting else None
                        # logger.debug(odd)
                        Odd.create(self.match, bet_type_slug, value_type_slug, load_source=self, bookie=bookie, **odd)
                    self.odds.clear()
                    self.source_detail_match.refresh_from_db()
                    self.source_detail_match.status=SourceDetail.FINISHED
                    self.source_detail_match.save()
                if self.source_session:
                    SourceSession.objects.filter(pk=self.source_session.pk).update(match_cnt=F("match_cnt")+1)
                    self.source_session.refresh_from_db()
        except Exception as e:
            self.handle_exception(e)
            raise LoadError
        finally:
            self.source_detail_match = None

    
    def start_detail(self, slug):
        try:
            with transaction.atomic():
                self.lock()
                self._start_detail(slug)
        except Exception as e:
            self.handle_exception(e)
            raise LoadError


    def finish_detail(self):
        try:
            with transaction.atomic():
                self.lock()
                if self.source_detail:
                    self.source_detail.refresh_from_db()
                    self.source_detail.status=SourceDetail.FINISHED
                    self.source_detail.last_update=timezone.now()
                    self.source_detail.save()
                    SourceDetailLeague.objects.filter(source_detail=self.source_detail).delete()
        except Exception as e:
            self.handle_exception(e)
        finally:
            self.source_detail = None


    def start_load(self, detail_slug=None, is_debug=False):
        '''
        Start loading data

        Actions:
        1. Find old unfinished session
        2. Continue or finish old session
        3. If no old session - create new

        Return: result - True (success) or False (error) 

        '''
        self.clear_contents()
        
        #delete all cached files
        if not is_debug:
            cache_dir = self.get_handler_dir().path('cache')
            for f in os.listdir(cache_dir):
                file_for_deleting = cache_dir.path(f)
                if os.path.isfile(file_for_deleting):
                    os.remove(file_for_deleting)
        
        #start session
        try:
            with transaction.atomic():
                self.lock()
                self.refresh_from_db()
                self.source_session, self.load_continue = SourceSession.get_or_create(self)
                if not self.load_continue:
                    for detail in SourceDetail.objects.filter(load_source=self):
                        SourceDetailLeague.objects.filter(source_detail=detail).delete()
                if detail_slug:
                    self._start_detail(detail_slug)
                self.is_error = False
                self.error_text = ''
                self.last_update = timezone.now()
                self.save()
            result = True
        except Exception as e:
            result = False
            self.handle_exception(e)
        return result


    def finish_load(self):
        '''
        Finish loading data

        '''
        try:
            with transaction.atomic():
                self.lock()
                if self.source_session:
                    self.source_session.finish()
                self.last_update = timezone.now()
                self.save()
                details=SourceDetail.objects.filter(load_source=self, status=SourceDetail.IN_PROCESS)
                details.update(status=SourceDetail.FINISHED, last_update=timezone.now())
        except Exception as e:
            self.handle_exception(e)
        finally:
            self.clear_contents()


###################################################################
class SourceSession(models.Model):

    IN_PROCESS = 'p'
    FINISHED = 'f'
    ERROR = 'e'
    INTERRUPTED = 'i'

    STATUS_CHOICES = (
        (IN_PROCESS, 'In process'),
        (FINISHED, 'Finished'),
        (ERROR, 'Error'),
        (INTERRUPTED, 'Interrupted'),
    )

    load_source = models.ForeignKey(LoadSource, on_delete=models.CASCADE, verbose_name='Load source')
    start_time = models.DateTimeField('Start time', null=True, blank=True)
    end_time = models.DateTimeField('End time', null=True, blank=True)
    status = models.CharField('Status', max_length=5, choices=STATUS_CHOICES, default=IN_PROCESS)
    match_cnt = models.IntegerField('Match cnt')
    err_cnt = models.IntegerField('Errors')

    class Meta:
        indexes = [
            models.Index(fields=['load_source','status'], name='load_status_idx'),
        ]

    def __str__(self):
        return self.load_source.name + ' ' + start_time.strftime("%d.%m.%Y, %H:%M:%S")

    @classmethod
    def get_or_create(cls, load_source):
        try:
            source_session = SourceSession.objects.get(
                                            load_source=load_source, 
                                            status__in=(SourceSession.IN_PROCESS,SourceSession.ERROR))
            load_continue = True
        except SourceSession.DoesNotExist:
            source_session = None
        if source_session:
            if not source_session.start_time or source_session.start_time < timezone.now() - timedelta(hours=12):
                #session is too old - interrupt old and create new
                source_session.status = SourceSession.INTERRUPTED
                source_session.end_time = timezone.now()
                source_session.save()
                msg = 'Interrupt old session "%s" (%s)' % (str(load_source), 
                                                           source_session.start_time.strftime("%d.%m.%Y, %H:%M:%S"))
                logger.warning(cls.__name__ + ': ' + msg)
                source_session = None
            else:
                logger.debug(cls.__name__ + ': Continue processing old session "%s" (%s)' % 
                    (str(load_source), source_session.start_time.strftime("%d.%m.%Y %H:%M:%S")) )

        if not source_session:
            source_session = SourceSession.objects.create(
                                                            load_source = load_source,
                                                            start_time = timezone.now(),
                                                            status = SourceSession.IN_PROCESS,
                                                            match_cnt = 0,
                                                            err_cnt = 0)
            logger.info(cls.__name__ + ': Create new session "%s"'% str(load_source) )
            load_continue = False
        return source_session, load_continue

    def finish(self):
        self.end_date = timezone.now()
        self.status = SourceSession.FINISHED
        self.save()

###################################################################
class SourceDetail(models.Model):

    IN_PROCESS = 'p'
    FINISHED = 'f'

    DETAIL_STATUS_CHOICES = (
        (IN_PROCESS, 'In process'),
        (FINISHED, 'Finished'),
    )

    load_source = models.ForeignKey(LoadSource, on_delete=models.CASCADE, verbose_name='Load source')
    slug = models.SlugField()
    last_update = models.DateTimeField('Last update', null=True, blank=True)
    load_date = models.DateField('Load date', null=True, blank=True)
    league_name = models.CharField('League name', max_length=100, null=True, blank=True)
    match_name = models.CharField('League name', max_length=100, null=True, blank=True)
    source_session = models.ForeignKey(SourceSession, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Session')
    status = models.CharField('Status', max_length=5, choices=DETAIL_STATUS_CHOICES, default=IN_PROCESS)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['load_source', 'slug'], name='unique_source_detail'),
        ]

    def __str__(self):
        return self.load_source.name + ' ' + self.slug

    def set_load_date(self, load_date):
        self.load_date = load_date
        self.save()
        self.refresh_from_db()

###################################################################
class SourceDetailLeague(models.Model):

    source_detail = models.ForeignKey(SourceDetail, on_delete=models.CASCADE, verbose_name='Detail')
    season_name = models.CharField('Season', max_length=100, default='NA')
    league_name = models.CharField('League', max_length=100)
    status = models.CharField('Status', max_length=5, choices=SourceDetail.DETAIL_STATUS_CHOICES, 
                                default=SourceDetail.IN_PROCESS)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['source_detail','season_name','league_name'], 
                                    name='unique_source_detail_league'),
        ]

    def __str__(self):
        return str(self.source_detail) + ' ' + self.season_name + ' ' + self.league_name

###################################################################
class SourceDetailMatch(models.Model):

    source_detail = models.ForeignKey(SourceDetail, on_delete=models.CASCADE, verbose_name='Detail')
    source_detail_league = models.ForeignKey(SourceDetailLeague, on_delete=models.CASCADE, verbose_name='Detail league')
    match_date = models.DateField('Match date')
    match_name = models.CharField('Match', max_length=100)
    status = models.CharField('Status', max_length=5, choices=SourceDetail.DETAIL_STATUS_CHOICES, 
                                default=SourceDetail.IN_PROCESS)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['source_detail','match_date','match_name'], 
                                    name='unique_source_detail_match'),
        ]

    def __str__(self):
        return str(self.source_detail) + ' ' + self.match_date.strftime("%d.%m.%Y") + ' ' + self.match_name

#######################################################s############
class ErrorLog(models.Model):

    load_source = models.ForeignKey(LoadSource, on_delete=models.CASCADE, verbose_name='Load source')
    source_session = models.ForeignKey(SourceSession, on_delete=models.CASCADE,  null=True, blank=True, verbose_name='Session')
    error_text = models.CharField('Error text', max_length=255, null=True, blank=True)
    error_context = models.TextField('Context', null=True, blank=True)
    error_time = models.DateTimeField('Error time', null=True, blank=True)
    league_name = models.CharField('League name', max_length=100, null=True, blank=True)
    match_name = models.CharField('League name', max_length=100, null=True, blank=True)
    file_name = models.CharField('File name', max_length=100, null=True, blank=True)
    source_detail = models.ForeignKey(SourceDetail, on_delete=models.CASCADE, null=True, blank=True, verbose_name='Load detail')
    error_traceback = models.TextField('Traceback', null=True, blank=True)

    def __str__(self):
        return self.error_text
