from datetime import datetime, date, timedelta
import traceback
import logging

from django.db import models, transaction
from django.utils import timezone

from core.models import LoadSource
from .exceptions import LoadError

logger = logging.getLogger(__name__)

###################################################################
class CommonHandler(LoadSource):

    class Meta:
        proxy = True

    def get_load_date(self, default_date=date(2010, 1, 1)):
        if self.source_detail:
            load_date = self.source_detail.load_date if self.source_detail.load_date else default_date
        else:
            load_date = self.load_date if self.load_date else default_date
        return load_date

    def clear_contents(self):
        self.source_session = None
        self.load_continue = False
        self.league_name = None
        self.match_name = None
        self.file_name = None
        self.context = None
        self.source_detail = None
        self.source_detail_league = None
        self.source_detail_match = None

    def handle_exception(self, e):
        logger.exception(e)
        if self.source_session:
            try:
                #check if session exists
                self.source_session = SourceSession.objects.get(pk=self.source_session.pk)
            except SourceSession.DoesNotExist:
                self.source_session = None
        #Save error
        ErrorLog.objects.create(
                            load_source = self,
                            source_session = self.source_session,
                            error_text = str(e)[:255],
                            error_context = self.context,
                            error_traceback = traceback.format_exc(),
                            error_time = timezone.now(),
                            league_name = self.league_name,
                            match_name = self.match_name,
                            file_name = self.match_name,
                            source_detail = self.source_detail)
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
            if finish_loading:
                raise LoadError

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


    def set_load_date(self, load_date):
        try:
            with transaction.atomic():
                self.lock()
                if self.source_detail:
                    self.source_detail.set_load_date(load_date)
                else:
                    self.load_date = load_date
                    self.save()
        except Exception as e:
            self.handle_exception(e)
            raise LoadError


    def start_or_skip_league(self, league_name, season_name='NA'):
        try:
            with transaction.atomic():
                self.lock()
                do_action = self._start_or_skip_league(league_name, season_name=season_name)
        except Exception as e:
            self.handle_exception(e)
            raise LoadError
        return do_action


    def finish_league(self):
        try:
            with transaction.atomic():
                self.lock()
                if self.source_detail_league:
                    self.source_detail_league.status=SourceDetail.FINISHED
                    self.source_detail_league.save()
        except Exception as e:
            self.handle_exception(e)
        finally:
            self.source_detail_league = None


    def start_or_skip_match(self, match_date, match_name):
        try:
            with transaction.atomic():
                self.lock()
                do_action = self._start_or_skip_match(match_date, match_name)
        except Exception as e:
            self.handle_exception(e)
            raise LoadError
        return do_action


    def finish_match(self):
        try:
            with transaction.atomic():
                self.lock()
                if self.source_detail_match:
                    self.source_detail_match.refresh_from_db()
                    self.source_detail_match.status=SourceDetail.FINISHED
                    self.source_detail_match.save()
        except Exception as e:
            self.handle_exception(e)
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
                    self.source_detail.save()
        except Exception as e:
            self.handle_exception(e)
        finally:
            self.source_detail = None


    def start_load(self, detail_slug=None):
        '''
        Start loading data

        Actions:
        1. Find old unfinished session
        2. Continue or finish old session
        3. If no old session - create new

        Return: result - True (success) or False (error) 

        '''
        self.clear_contents()
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
                logger.warning(msg)
                source_session = None
            else:
                logger.debug('Continue processing old session "%s" (%s)' % 
                    (str(load_source), source_session.start_time.strftime("%d.%m.%Y %H:%M:%S")) )

        if not source_session:
            source_session = SourceSession.objects.create(
                                                            load_source = load_source,
                                                            start_time = timezone.now(),
                                                            status = SourceSession.IN_PROCESS,
                                                            match_cnt = 0,
                                                            err_cnt = 0)
            logger.info('Create new session "%s"'% str(load_source) )
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
        return str(source_detail) + ' ' + self.season_name + ' ' + self.league_name

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
        return str(source_detail) + ' ' + self.match_date.strftime("%d.%m.%Y") + ' ' + self.match_name

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
