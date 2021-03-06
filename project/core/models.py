import random
from datetime import timedelta

from django.utils import timezone
from django.db import models
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from django.template.defaultfilters import slugify


###################################################################
class SaveSlugCountryMixin(object):
    def save(self, *args, **kwargs):
        unknown_country = Country.objects.get(slug='na')
        if not self.slug:
            self.slug = slugify(self.name)
        if not self.country_id:
            self.country = unknown_country
        if self.country == unknown_country and not self.slug.endswith('newteam'):
            self.slug += ('_' + str(random.randint(1,1000000000)) + 'newteam')
        super(SaveSlugCountryMixin, self).save(*args, **kwargs)

###################################################################
class Mergable(object):

    def merge_related(self, dst):
        raise NotImplementedError("Subclasses should implement this")

    def change_data(self, src):
        raise NotImplementedError("Subclasses should implement this")

    def merge_to(self, dst):
        ''' Merge current object to dst object '''
        if dst==None or self==dst:
            return
        if self.load_source.reliability <= dst.load_source.reliability:
            dst.load_source = self.load_source
            dst.change_data(self)
        self.merge_related(dst)
        self.delete()


###################################################################
class Loadable(Mergable, models.Model):

    CONFIRMED = 'c'
    UNCONFIRMED = 'u'

    STATUS_CHOICES = (
        (CONFIRMED, 'Confirmed'),
        (UNCONFIRMED, 'Unconfirmed'),
    )

    load_status = models.CharField('Status', max_length=5, choices=STATUS_CHOICES, default='c')
    load_source = models.ForeignKey('LoadSource', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Source',
                                    related_name="%(app_label)s_%(class)s_load_source")
    created = models.DateTimeField('Created', null=True, blank=True)
    confirmed = models.DateTimeField('Confirmed', null=True, blank=True)

    class Meta:
        abstract = True,

    @classmethod
    def get_object_load_source_class(cls):
        raise NotImplementedError("Subclasses should implement this")

    @classmethod
    def create(cls, **kwargs):
        raise NotImplementedError("Subclasses should implement this")

    @classmethod
    def get_object(cls, sport=None, country=None, slug=None, **kwargs):
        try:
            obj = cls.objects.get(sport=sport, country=country, slug=slug)
        except cls.DoesNotExist:
            obj = None
        return obj

    def _create(self, **kwargs):
        self.load_status=Loadable.UNCONFIRMED
        self.load_source=kwargs.get('load_source',None)
        self.created=timezone.now()
        self.save()

    @classmethod
    def get_or_create(cls, **kwargs):

        #prepare parameters
        sport = kwargs.get('sport',None)
        if not sport:
            raise ValueError('Missing parameter "sport"')
        slug = kwargs.get('slug',None)
        if not slug:
            name = kwargs.get('name',None)
            if not name:
                raise ValueError('Missing parameter "name"')
            slug = slugify(name)
            kwargs['slug'] = slug
        load_source = kwargs.get('load_source',None)
        if not load_source:
            raise ValueError('Missing parameter "load_source"')
        country = kwargs.get('country',None)
        if not country:
            country = Country.objects.get(slug='na')
            kwargs['country'] = country

        load_source_class = cls.get_object_load_source_class()

        # get main object if it's already saved in table <real object name>LoadSource
        try:
            source_obj = load_source_class.objects.get(sport=sport, 
                                                       country=country, 
                                                       slug=slug, 
                                                       load_source=load_source)
            obj = cls.objects.get(object=source_obj)
            found = True
        except load_source_class.DoesNotExist:
            obj = None
            found = False
 
        if not found:
            # get object from main table 
            obj = cls.get_object(**kwargs)

        if not obj:
            #Can't find main object
            #Create it
            # obj = cls.objects.create(**kwargs, load_status=Loadable.UNCONFIRMED, created=timezone.now())
            obj = cls.create(**kwargs)

        if found:
            source_obj.selected = timezone.now()
            source_obj.save()
        else:
            #Create new row in table <real object name>LoadSource
            source_obj = load_source_class.objects.create(
                            slug = slug,
                            sport = sport,
                            country = country,
                            name = kwargs.get('name',None),
                            load_source = load_source,
                            created = timezone.now(),
                            confirmed = None,
                            selected = timezone.now()
                            )
            source_obj.init_object(obj)
        return obj


    def confirm(self, load_source):
        ''' Confirm object '''
        if not load_source:
            raise ValueError('Missing parameter "load_source"')

        self.refresh_from_db()

        is_changed = False
        if self.load_status == Loadable.UNCONFIRMED:
            self.load_status = Loadable.CONFIRMED
            self.load_source = load_source
            self.confirmed = timezone.now()
            is_changed = True
        elif load_source.reliability < self.load_source.reliability:
            self.load_source = load_source
            is_changed = True
        if is_changed:
            self.save()



###################################################################
class ObjectLoadSource(models.Model):

    ACTIVE = 'a'
    DELETED = 'd'

    STATUS_CHOICES = (
        (ACTIVE, 'Active'),
        (DELETED, 'Deleted'),
    )

    slug = models.SlugField()
    sport = models.ForeignKey('Sport', on_delete=models.CASCADE, verbose_name='Sport', 
                              related_name="%(app_label)s_%(class)s_sport",)
    country = models.ForeignKey('Country', on_delete=models.CASCADE, verbose_name='Country',
                              related_name="%(app_label)s_%(class)s_country",)
    name = models.CharField('Object name', max_length=255, null=True, blank=True)
    load_source = models.ForeignKey('LoadSource', on_delete=models.CASCADE, verbose_name='Source',
                                     related_name="%(app_label)s_%(class)s_load_source")
    status = models.CharField('Status', max_length=5, choices=STATUS_CHOICES, default=ACTIVE)
    created = models.DateTimeField('Created', null=True, blank=True)
    confirmed = models.DateTimeField('Confirmed', null=True, blank=True)
    selected = models.DateTimeField('Selected', null=True, blank=True)

    class Meta:
        abstract = True,

    def init_object(self, real_object):
        raise NotImplementedError("Subclasses should implement this")

    def __str__(self):
        return ('%(sport)s-%(country)s-%(slug)s-%(source)s' % 
                {'sport':self.sport, 'country':self.country, 'slug':self.slug, 'source':self.load_source,})




###################################################################
class Sport(models.Model):

    FOOTBALL = 'football'

    slug = models.SlugField(unique=True)
    name = models.CharField('sport', max_length=100)
    last_update = models.DateTimeField('Last update', null=True, blank=True)
    is_loadable = models.BooleanField('Load data')
    is_calculated = models.BooleanField('Calculate data')

    def __str__(self):
        return self.name


###################################################################
class LoadSource(models.Model):

    SRC_MANUAL        = 'manual'

    SRC_ESPN          = 'espn'
    SRC_FOOTBALL_DATA = 'football_data'
    SRC_UNDERSTAT     = 'understat'
    SRC_XSCORES       = 'xscores'

    SRC_1XBET         = '1xbet'
    SRC_PARIMATCH     = 'parimatch'

    slug = models.SlugField()
    sport = models.ForeignKey(Sport, on_delete=models.PROTECT, verbose_name='Sport')
    name = models.CharField('Source', max_length=100)
    reliability = models.IntegerField('Reliability')
    source_handler = models.CharField('Handler', max_length=100, null=True, blank=True)
    source_url = models.CharField('URL', max_length=255, null=True, blank=True)
    is_loadable = models.BooleanField('Load data', null=True, blank=True)
    is_betting = models.BooleanField('Betting', null=True, blank=True)
    is_error = models.BooleanField('Error', null=True, blank=True)
    error_text = models.CharField('Error text', max_length=255, null=True, blank=True)
    last_update = models.DateTimeField('Last update', null=True, blank=True)
    load_date = models.DateField('Load date', null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['sport', 'slug'], name='unique_load_source'),
        ]

    def __str__(self):
        return self.name


###################################################################
class Country(Loadable):

    slug = models.SlugField(unique=True)
    code = models.CharField('Code', max_length=100)
    name = models.CharField('Country', max_length=100)

    @classmethod
    def get_object(cls, slug=None, **kwargs):
        try:
            obj = cls.objects.get(slug=slug)
        except cls.DoesNotExist:
            obj = None
        return obj

    @classmethod
    def get_object_load_source_class(cls):
        return CountryLoadSource

    @classmethod
    def create(cls, **kwargs):
        slug = kwargs.get('slug', None)
        code = kwargs.get('code', None)
        name = kwargs.get('name', None)
        if not name:
            raise ValueError('Missing country name')
        if not slug:
            slug = slugify(name)
        if not code:
            code = slug
        country = Country(slug=slug, code=code, name=name)
        country._create(**kwargs)
        return country

    @classmethod
    def get_or_create(cls, name, load_source):
        sport = Sport.objects.get(slug='na')
        country = Country.objects.get(slug='na')
        return super(Country, cls).get_or_create(country=country, name=name, sport=sport, load_source=load_source)

    def __str__(self):
        return self.name    

    def merge_related(self, dst):
        for league in League.objects.filter(country=self):
            league.change_country(dst)
        for team in Team.objects.filter(country=self):
            team.change_country(dst)
        for referee in Referee.objects.filter(country=self):
            referee.change_country(dst)
        CountryLoadSource.objects.filter(country_obj=self).update(country_obj=dst) 


    def change_data(self, src):
        self.code = src.code
        self.name = src.name
        self.save()


class CountryLoadSource(ObjectLoadSource):

    country_obj = models.ForeignKey(Country, on_delete=models.CASCADE, verbose_name='Country', related_name='object', null=True)

    def init_object(self, real_object):
        self.country_obj = real_object
        self.save()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['sport','slug','load_source'], name='unique_country_load_source'),
        ]


###################################################################
class TeamType(models.Model):

    REGULAR = 'regular'
    NATIONAL = 'national'

    slug = models.SlugField(unique=True)
    name = models.CharField('Team type', max_length=100)

    def __str__(self):
        return self.name        

###################################################################
class League(SaveSlugCountryMixin, Loadable):

    slug = models.SlugField()
    name = models.CharField('League', max_length=100)
    team_type = models.ForeignKey(TeamType, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Team type')
    sport = models.ForeignKey(Sport, on_delete=models.PROTECT, verbose_name='Sport')
    country = models.ForeignKey(Country, on_delete=models.PROTECT, verbose_name='Country')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['sport', 'country', 'slug'], name='unique_league'),
        ]

    def __str__(self):
        return self.name        

    @classmethod
    def get_object_load_source_class(cls):
        return LeagueLoadSource

    @classmethod
    def create(cls, **kwargs):
        slug = kwargs.get('slug', None)
        name = kwargs.get('name', None)
        team_type = kwargs.get('team_type', None)
        sport = kwargs.get('sport', None)
        country = kwargs.get('country', None)
        if not name:
            raise ValueError('Missing league name')
        if not slug:
            slug = slugify(name)
        league = League(slug=slug, name=name, team_type=team_type, sport=sport, country=country)
        league._create(**kwargs)
        return league

    def merge_related(self, dst):
        for season in Season.objects.filter(league=self):
            season.change_league(dst)
        for match in Match.objects.filter(league=self):
            match.change_league(dst)
        dst.process_empty_season()
        LeagueLoadSource.objects.filter(league=self).update(league=dst) 

    def change_data(self, src):
        self.name = src.name
        self.team_type = src.team_type
        self.save()

    def change_country(self, country_dst):
        '''Change league country'''
        if country_dst == None or country_dst == self.country:
            return
        #find league destination
        league_dst = League.get_object(sport=self.sport, country=country_dst, slug=self.slug)
        if league_dst == None:
            self.country = country_dst
            self.save()
        else:
            self.merge_to(league_dst)

    def get_season(self, match_date):
        ''' Get league season by match date '''
        return Season.get_season(self, match_date)

    def get_or_create_season(self, start_date, end_date, load_source, name=None):
        ''' Get or create league season '''
        return Season.get_or_create(self, start_date, end_date, load_source, name)

    def process_empty_season(self, load_source=None):
        for match in Match.objects.filter(league=self, season__isnull=True):
            match.set_season(load_source=load_source)



class LeagueLoadSource(ObjectLoadSource):

    league = models.ForeignKey(League, on_delete=models.CASCADE, verbose_name='League', related_name='object', null=True)

    def init_object(self, real_object):
        self.league = real_object
        self.save()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['sport','country','slug','load_source'], name='unique_league_load_source'),
        ]



###################################################################
class Season(models.Model):

    name = models.CharField('Season', max_length=100)
    league = models.ForeignKey(League, on_delete=models.CASCADE, verbose_name='League')
    start_date = models.DateField('Start', null=True, blank=True)
    end_date = models.DateField('End', null=True, blank=True)
    load_source = models.ForeignKey(LoadSource, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Source')

    def __str__(self):
        return self.name

    @staticmethod
    def get_season(league, match_date):
        try:
            season = Season.objects.get(league=league, start_date__lte=match_date, end_date__gte=match_date)
        except ObjectDoesNotExist:
            season = None
        return season

    @staticmethod
    def get_or_create(league, start_date, end_date, load_source, name=None):
        if not league:
            raise ValueError('Missing league')
        if not start_date or not end_date:
            season = Season.objects.filter(league=league).order_by('start_date').first()
            if season:
                raise ValueError('Season already exists "%s"' % season)
            else:
                if not name:
                    raise ValueError('Missing season name')
                season = Season.objects.create(league=league, 
                                               start_date=start_date,
                                               end_date=end_date,
                                               load_source=load_source,
                                               name=name)
        else:
            if start_date > end_date:
                raise ValueError('Incorrect season dates %s - %s' % (start_date,end_date))
            if not name:
                name = str(start_date.year) + '\\' + str(end_date.year)
            mid_date = (start_date + (end_date-start_date)/2)
            season = Season.get_season(league, mid_date)
            if not season:
                season = Season.get_season(league, start_date)
            if not season:
                season = Season.objects.create(league=league, 
                                               start_date=start_date,
                                               end_date=end_date,
                                               load_source=load_source,
                                               name=name)
            else:
                if load_source and (not season.load_source or 
                                    load_source.reliability <= season.load_source.reliability
                                    ):
                    changed = False
                    if season.start_date != start_date: season.start_date=start_date; changed = True;
                    if season.end_date != end_date: season.end_date=end_date; changed = True;
                    if season.name != name: season.name=name; changed = True;
                    if season.load_source != load_source: season.load_source=load_source; changed = True;
                    if changed: season.save()
        return season

    def change_league(self, league_dst):
        '''Change league'''
        if league_dst == None or league_dst == self.league:
            return

        change_season = (self.load_source.reliability < league_dst.load_source.reliability)

        if self.start_date==None or self.end_date==None:
            #unknown season date interval
            #delete all team membership
            #later all teams of this league should connected with season (after changing teams league)
            TeamMembership.objects.filter(season=self).delete()
            seasons_dst = Season.objects.all()
            if seasons_dst.exists():
                self.delete()
            else:
                self.league = league_dst
                self.save()
        else:
            #define date interval
            #check - if there are seasons in interval self.start_date and self.end_date
            seasons_dst = Season.objects.filter(league=league_dst, 
                                                end_date__gte=self.start_date,
                                                start_date__lte=self.end_date,
                                                )
            if self.load_source.reliability < league_dst.load_source.reliability:
                #new league is more reliable
                seasons_dst.delete()
                TeamMembership.objects.filter(season=self).delete()
                self.league = league_dst
                self.save()
            else:
                #dst league is more reliable
                if seasons_dst.exists():
                    #dst season exists - delete new season
                    self.delete()
                else:
                    #remove memberships of current season
                    #and change season league  
                    TeamMembership.objects.filter(season=self).delete()
                    self.league = league_dst
                    self.save()


###################################################################
class Team(SaveSlugCountryMixin, Loadable):

    slug = models.SlugField()
    name = models.CharField('Team', max_length=100)
    team_type = models.ForeignKey(TeamType, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Team type')
    sport = models.ForeignKey(Sport, on_delete=models.PROTECT, verbose_name='Sport')
    country = models.ForeignKey(Country, on_delete=models.PROTECT, verbose_name='Country')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['sport', 'country', 'slug'], name='unique_team'),
        ]

    def __str__(self):
        return self.name        

    @classmethod
    def get_object_load_source_class(cls):
        return TeamLoadSource

    @classmethod
    def create(cls, **kwargs):
        slug = kwargs.get('slug', None)
        name = kwargs.get('name', None)
        team_type = kwargs.get('team_type', None)
        sport = kwargs.get('sport', None)
        country = kwargs.get('country', None)
        if not name:
            raise ValueError('Missing team name')
        if not slug:
            slug = slugify(name)
        team = Team(slug=slug, name=name, team_type=team_type, sport=sport, country=country)
        team._create(**kwargs)
        return team

    def merge_related(self, dst):
        for match in Match.objects.filter(team_h=self):
            match.change_team_h(dst)
        for match in Match.objects.filter(team_a=self):
            match.change_team_a(dst)
        #Change in team membersiip
        for tm in TeamMembership.objects.filter(team=self):
            if not TeamMembership.objects.filter(team=dst, season=tm.season).exists():
                tm.team = dst
                tm.save()
        TeamLoadSource.objects.filter(team=self).update(team=dst) 

    def change_data(self, src):
        self.name = src.name
        self.team_type = src.team_type
        self.save()

    def change_country(self, country_dst):
        '''Change team country'''
        if country_dst == None or country_dst == self.country:
            return
        #find team destination
        team_dst = Team.get_object(sport=self.sport, country=country_dst, slug=self.slug)
        if team_dst == None:
            self.country = country_dst
            self.save()
        else:
            self.merge_to(team_dst)

    def set_membership(self, season, load_source=None):
        if not season:
            raise ValueError('Missing season')
        if not TeamMembership.objects.filter(team=self, season=season).exists():
            TeamMembership.objects.create(team=self, season=season, load_source=load_source)


class TeamLoadSource(ObjectLoadSource):

    team = models.ForeignKey(Team, on_delete=models.CASCADE, verbose_name='Team', related_name='object', null=True)

    def init_object(self, real_object):
        self.team = real_object
        self.save()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['sport','country','slug','load_source'], name='unique_team_load_source'),
        ]


###################################################################
class TeamMembership(models.Model):

    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    season = models.ForeignKey(Season, on_delete=models.CASCADE)
    load_source = models.ForeignKey(LoadSource, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['team', 'season'], name='unique_team_membership'),
        ]


###################################################################
class Referee(SaveSlugCountryMixin, Loadable):

    slug = models.SlugField()
    name = models.CharField('Referee', max_length=100)
    sport = models.ForeignKey(Sport, on_delete=models.PROTECT, verbose_name='Sport')
    country = models.ForeignKey(Country, on_delete=models.PROTECT, verbose_name='Country')

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['sport', 'country', 'slug'], name='unique_referee'),
        ]

    def __str__(self):
        return self.name

    @classmethod
    def get_object_load_source_class(cls):
        return RefereeLoadSource

    @classmethod
    def create(cls, **kwargs):
        slug = kwargs.get('slug', None)
        name = kwargs.get('name', None)
        sport = kwargs.get('sport', None)
        country = kwargs.get('country', None)
        if not name:
            raise ValueError('Missing referee name')
        if not slug:
            slug = slugify(name)
        referee = Referee(slug=slug, name=name, sport=sport, country=country)
        referee._create(**kwargs)
        return referee

    def merge_related(self, dst):
        #!!! TODO: process other related objects
        MatchReferee.change_referee(self, dst)
        RefereeLoadSource.objects.filter(referee=self).update(referee=dst) 

    def change_data(self, src):
        self.name = src.name
        self.save()

    def change_country(self, country_dst):
        '''Change team country'''
        if country_dst == None or country_dst == self.country:
            return
        #find referee dst
        referee_dst = Referee.get_object(sport=self.sport, country=country_dst, slug=self.slug)
        if referee_dst == None:
            self.country = country_dst
            self.save()
        else:
            self.merge_to(referee_dst)


class RefereeLoadSource(ObjectLoadSource):

    referee = models.ForeignKey(Referee, on_delete=models.CASCADE, verbose_name='Referee', related_name='object', null=True)

    def init_object(self, real_object):
        self.referee = real_object
        self.save()

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['sport','country','slug','load_source'], name='unique_referee_load_source'),
        ]


###################################################################
class Match(Mergable, models.Model):

    FINISHED = 'F'
    SCHEDULED = 'S'
    CANCELLED = 'C'
    INTERRUPTED = 'I'

    WIN = 'w'
    DRAW = 'd'
    LOOSE = 'l'

    COMTETITOR_HOME = 'h'
    COMTETITOR_AWAY = 'a'

    STATUS_CHOICES = (
        (FINISHED, 'Finished'),
        (SCHEDULED, 'Scheduled'),
        (CANCELLED, 'Cancelled'),
        (INTERRUPTED, 'Interrupted'),
    )
    RESULT_CHOICES = (
        (WIN, 'Win'),
        (DRAW, 'Draw'),
        (LOOSE, 'Loose'),
    )

    league = models.ForeignKey(League, on_delete=models.CASCADE, verbose_name='League')
    season = models.ForeignKey(Season, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Season')
    team_h = models.ForeignKey(Team, on_delete=models.CASCADE, verbose_name='Home team', related_name='bcore_match_team_h_fk')
    team_a = models.ForeignKey(Team, on_delete=models.CASCADE, verbose_name='Away team', related_name='bcore_match_team_a_fk')
    match_date = models.DateField('Match date')
    score = models.CharField('Score', max_length=100, null=True, blank=True)
    result = models.CharField('Result', max_length=5, choices=RESULT_CHOICES, null=True, blank=True)
    status = models.CharField('Status', max_length=5, choices=STATUS_CHOICES, default='S')
    load_source = models.ForeignKey(LoadSource, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        indexes = [
            models.Index(fields=['match_date'], name='match_date_idx'),
        ]
        constraints = [
            models.UniqueConstraint(fields=['league', 'team_h', 'team_a', 'match_date'], name='unique_match'),
        ]

    def __str__(self):
        return '%s - %s' % (self.team_h.name, self.team_a.name)


    @classmethod
    def get_object(cls, league=None, team_h=None, team_a=None, match_date=None, **kwargs):
        try:
            obj = cls.objects.get(league=league, team_h=team_h, team_a=team_a, match_date=match_date)
        except cls.DoesNotExist:
            obj = None
        if not obj and match_date:
            date_from = match_date - timedelta(days=1)
            date_to = match_date + timedelta(days=1)
            try:
                obj = cls.objects.filter(league=league, 
                                         team_h=team_h, 
                                         team_a=team_a, 
                                         match_date__range=(date_from,date_to)
                                         ).first()
            except cls.DoesNotExist:
                obj = None
        return obj

    @classmethod
    def get_or_create(cls, league=None, team_h=None, team_a=None, match_date=None, load_source=None, 
                           status=FINISHED, season=None):
        match = cls.get_object(league=league, team_h=team_h, team_a=team_a, match_date=match_date)

        if match:
            #match is found - change data if needed 
            if load_source and (not match.load_source or 
                                load_source.reliability <= match.load_source.reliability
                                ):
                changed = False
                if status and match.status != status: match.status=status; changed = True;
                if season and match.season != season: match.season=season; changed = True;
                if match.load_source != load_source: match.load_source=load_source; changed = True;
                if changed: match.save()
        else:
            #create new match
            if not league: raise ValueError('Missing league')
            if not team_h: raise ValueError('Missing home team')
            if not team_a: raise ValueError('Missing away team')
            if team_h==team_a: raise ValueError('Teams are the same')
            if not match_date: raise ValueError('Missing match date')
            if not season: season = league.get_season(match_date)
            match = Match.objects.create(league=league, 
                                         season=season,
                                         team_h=team_h,
                                         team_a=team_a,
                                         match_date=match_date,
                                         status=status,
                                         load_source=load_source
                                         )
            if season:
                team_h.set_membership(season=season, load_source=load_source)
                team_a.set_membership(season=season, load_source=load_source)
        return match

    def set_referee(self, referee, load_source=None):
        try:
            match_referee = MatchReferee.objects.get(match=self)
        except MatchReferee.DoesNotExist:
            match_referee = None
        if match_referee:
            if load_source and (not match_referee.load_source or
                                load_source.reliability <= match_referee.load_source.reliability):
                match_referee.referee = referee
                match_referee.load_source = load_source
                match_referee.save()
        else:
            match_referee = MatchReferee.objects.create(match=self, referee=referee, load_source=load_source)

    def change_league(self, league_dst):
        '''Change match league'''
        if league_dst == None or league_dst == self.league:
            return
        #find match destination
        match_dst = Match.get_object(league=league_dst, team_h=self.team_h, team_a=self.team_a, match_date=self.match_date)
        if match_dst:
            self.merge_to(match_dst)
        else:
            self.league = league_dst
            self.save()

    def change_team_h(self, team_dst):
        '''Change home team of match'''
        if team_dst == None or team_dst == self.team_h:
            return
        #find match destination
        match_dst = Match.get_object(league=self.league, team_h=team_dst, team_a=self.team_a, match_date=self.match_date)
        if match_dst:
            self.merge_to(match_dst)
        else:
            self.team_h = team_dst
            self.save()

    def change_team_a(self, team_dst):
        '''Change home team of match'''
        if team_dst == None or team_dst == self.team_a:
            return
        #find match destination
        match_dst = Match.get_object(league=self.league, team_h=self.team_a, team_a=team_dst, match_date=self.match_date)
        if match_dst:
            self.merge_to(match_dst)
        else:
            self.team_a = team_dst
            self.save()

    def change_data(self, src):
        self.status = src.status
        self.save()

    def set_season(self, season=None, load_source=None):
        if not season:
            season = Season.get_season(self.league, self.match_date)
        if season:
            if season != self.season:
                self.season = season
                self.save()
            self.team_h.set_membership(season=season, load_source=load_source)
            self.team_a.set_membership(season=season, load_source=load_source)

    def merge_related(self, dst):
        #!!! TODO: process other related objects
        MatchReferee.change_match(self, dst)

###################################################################
class MatchReferee(models.Model):

    match = models.ForeignKey(Match, on_delete=models.CASCADE)
    referee = models.ForeignKey(Referee, on_delete=models.CASCADE)
    load_source = models.ForeignKey(LoadSource, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['match'], name='unique_match_referee'),
        ]

    @staticmethod
    def change_referee(referee_from, referee_to):
        if referee_to == None or referee_to == referee_from:
            return
        MatchReferee.objects.filter(referee=referee_from).update(referee=referee_to)

    @staticmethod
    def change_match(match_from, match_to):
        if match_to == None or match_to == match_from:
            return
        for mr in MatchReferee.objects.filter(match=match_from):
            match_to.set_referee(mr.referee, load_source=mr.load_source)


###################################################################
class MatchStats(Mergable, models.Model):

    GOALS = 'g'
    XG = 'xg'
    YCARD = 'yc'
    RCARD = 'rc'
    PENALTY = 'pen'
    GOALS_MINUTE = 'gm'
    XG_MINUTE = 'xgm'
    YCARD_MINUTE = 'ycm'
    RCARD_MINUTE = 'rcm'
    GOAL_TIME = 'gt'
    SHOTS = 's'
    SHOTS_ON_TARGET = 'sot'
    DEEP = 'd'
    PPDA = 'ppda'
    CORENERS = 'c'
    FOULS = 'f'
    FREE_KICKS = 'fk'
    OFFSIDES = 'o'
    POSSESSION = 'pos'

    STAT_CHOICES = (
        (GOALS, 'Goals'),
        (XG, 'xG'),
        (YCARD, 'Yellow cards'),
        (RCARD, 'Red cards'),
        (PENALTY, 'Penalies'),
        (GOALS_MINUTE, 'Goals (minutes)'),
        (XG_MINUTE, 'xG (minutes)'),
        (YCARD_MINUTE, 'Yellow cards (minutes)'),
        (RCARD_MINUTE, 'Red cards (minutes)'),
        (GOAL_TIME, 'Goal time'),
        (SHOTS, 'Shots'),
        (SHOTS_ON_TARGET, 'Shots on target'),
        (DEEP, 'Deep passes'),    #Passes completed within an estimated 20 yards of goal (crosses excluded)
        (PPDA, 'PPDA'),           #Passes allowed per defensive action in the opposition half
        (CORENERS, 'Corners'),
        (FOULS, 'Fouls'),
        (FREE_KICKS, 'Free kicks'),
        (OFFSIDES, 'Offsides'),
        (POSSESSION, 'Possession'),
    )

    COMPETITOR_CHOICES = (
        (Match.COMTETITOR_HOME, 'Home team'),
        (Match.COMTETITOR_AWAY, 'Away team'),
    )

    match = models.ForeignKey(Match, on_delete=models.CASCADE, verbose_name='Match')
    stat_type = models.CharField('Stat', max_length=10, choices=STAT_CHOICES)
    competitor = models.CharField('Competitor', max_length=5, choices=COMPETITOR_CHOICES)
    period = models.IntegerField('Period')
    value = models.CharField('Value', max_length=255)
    load_source = models.ForeignKey(LoadSource, on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        constraints = [
            models.UniqueConstraint(fields=['match','stat_type','competitor', 'period'], name='unique_match_stats'),
        ]

    def __str__(self):
        return '%s %s(%s): %s' % (self.competitor, self.stat_type, self.period, self.value)


