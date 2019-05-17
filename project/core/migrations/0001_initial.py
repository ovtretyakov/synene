# Generated by Django 2.2.1 on 2019-05-04 08:04

import core.models
from django.db import migrations, models
import django.db.models.deletion

import requests
from bs4 import BeautifulSoup

class Migration(migrations.Migration):

    initial = True

    def insertSport(apps, schema_editor):
        Sport = apps.get_model('core', 'Sport')
        sport = Sport(slug='football', name="Football", is_loadable=True, is_calculated=True)
        sport.save()
        sport = Sport(slug='na', name="Unknown", is_loadable=False, is_calculated=False)
        sport.save()


    def load_countries(apps, schema_editor):
        def create_or_update_country(apps, slug, country_code, country_name):
            slug = slug.lower()
            Country = apps.get_model('core', 'Country')
            person, created = Country.objects.get_or_create(
                slug=slug, 
                defaults={"name": country_name, "code": country_code}
            )

        create_or_update_country(apps, 'na', '0', 'Unknown')

        r = requests.get('https://countrycode.org/')
        html = r.text
        soup = BeautifulSoup(html, 'lxml')

        table = soup.select_one('table.table')
        for tr in table.select('tr'):
            tds = tr.select('td')
            if tds:
                s = tds[2].get_text().split('/')
                country_name = tds[0].get_text()
                country_code = tds[1].get_text()
                slug = s[1].strip()
                create_or_update_country(apps, slug, country_code, country_name)

    def insertTeamTypes(apps, schema_editor):
        TeamType = apps.get_model('core', 'TeamType')
        team_type = TeamType(slug='regular', name="Regular")
        team_type.save()
        team_type = TeamType(slug='national', name="National")
        team_type.save()


    def insertLoadSources(apps, schema_editor):
        Sport = apps.get_model('core', 'Sport')
        sport = Sport.objects.get(slug='football')
        LoadSource = apps.get_model('core', 'LoadSource')
        load_source = LoadSource(slug='manual', 
                                 sport=sport,
                                 name='Manual update',
                                 reliability=10,
                                 source_handler='',
                                 source_url='',
                                 is_loadable=False,
                                 is_betting=False
                                )
        load_source.save()
        load_source = LoadSource(slug='espn',
                                 sport=sport,
                                 name='ESPN Soccer Scores',
                                 reliability=20,
                                 source_handler='',
                                 source_url='http://www.espn.com/soccer/scoreboard',
                                 is_loadable=False,
                                 is_betting=False
                                )
        load_source.save()
        load_source = LoadSource(slug='understat',
                                 sport=sport,
                                 name='xG statistics',
                                 reliability=30,
                                 source_handler='',
                                 source_url='https://understat.com/',
                                 is_loadable=False,
                                 is_betting=False
                                )
        load_source.save()
        load_source = LoadSource(slug='football_data',
                                 sport=sport,
                                 name='Historical Football Results',
                                 reliability=40,
                                 source_handler='',
                                 source_url='http://www.football-data.co.uk/data.php',
                                 is_loadable=False,
                                 is_betting=False
                                )
        load_source.save()
        load_source = LoadSource(slug='xscores',
                                 sport=sport,
                                 name='Live Scores for Football',
                                 reliability=50,
                                 source_handler='',
                                 source_url='https://www.xscores.com/soccer/livescores',
                                 is_loadable=False,
                                 is_betting=False
                                )
        load_source.save()
        load_source = LoadSource(slug='1xbet',
                                 sport=sport,
                                 name='1XBET Betting Company',
                                 reliability=60,
                                 source_handler='',
                                 source_url='https://1xmavemv.com/',
                                 is_loadable=False,
                                 is_betting=False
                                )
        load_source.save()
        load_source = LoadSource(slug='parimatch',
                                 sport=sport,
                                 name='Parimatch Betting Company',
                                 reliability=70,
                                 source_handler='',
                                 source_url='https://www.parimatch.com/en/',
                                 is_loadable=False,
                                 is_betting=False
                                )
        load_source.save()




    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Country',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('load_status', models.CharField(choices=[('c', 'Confirmed'), ('u', 'Unconfirmed')], default='c', max_length=5, verbose_name='Status')),
                ('created', models.DateTimeField(blank=True, null=True, verbose_name='Created')),
                ('confirmed', models.DateTimeField(blank=True, null=True, verbose_name='Confirmed')),
                ('slug', models.SlugField(unique=True)),
                ('code', models.CharField(max_length=100, verbose_name='Code')),
                ('name', models.CharField(max_length=100, verbose_name='Country')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='League',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField()),
                ('name', models.CharField(max_length=100, verbose_name='League')),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.Country', verbose_name='Country')),
            ],
            bases=(core.models.SaveSlugCountryMixin, models.Model),
        ),
        migrations.CreateModel(
            name='LoadSource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField()),
                ('name', models.CharField(max_length=100, verbose_name='Source')),
                ('reliability', models.IntegerField(verbose_name='Reliability')),
                ('source_handler', models.CharField(blank=True, max_length=100, null=True, verbose_name='Handler')),
                ('source_url', models.CharField(blank=True, max_length=255, null=True, verbose_name='URL')),
                ('is_loadable', models.BooleanField(blank=True, null=True, verbose_name='Load data')),
                ('is_betting', models.BooleanField(blank=True, null=True, verbose_name='Betting')),
                ('is_error', models.BooleanField(blank=True, null=True, verbose_name='Error')),
                ('error_text', models.CharField(blank=True, max_length=255, null=True, verbose_name='Error text')),
                ('last_update', models.DateTimeField(blank=True, null=True, verbose_name='Last update')),
                ('load_date', models.DateField(blank=True, null=True, verbose_name='Load date')),
            ],
        ),
        migrations.CreateModel(
            name='Match',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('match_date', models.DateField(verbose_name='Match date')),
                ('score', models.CharField(max_length=100, verbose_name='Score')),
                ('result', models.CharField(blank=True, choices=[('w', 'Win'), ('d', 'Draw'), ('l', 'Loose')], max_length=5, null=True, verbose_name='Result')),
                ('status', models.CharField(choices=[('Fin', 'Finished'), ('Sch', 'Scheduled'), ('Can', 'Cancelled'), ('Int', 'Interrupted')], default='n', max_length=5, verbose_name='Status')),
                ('league', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.League', verbose_name='League')),
            ],
        ),
        migrations.CreateModel(
            name='Season',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, verbose_name='Season')),
                ('start_date', models.DateField(blank=True, null=True, verbose_name='Start')),
                ('end_date', models.DateField(blank=True, null=True, verbose_name='End')),
                ('league', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.League', verbose_name='League')),
                ('load_source', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.LoadSource', verbose_name='Source')),
            ],
        ),
        migrations.CreateModel(
            name='Sport',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(unique=True)),
                ('name', models.CharField(max_length=100, verbose_name='sport')),
                ('last_update', models.DateTimeField(blank=True, null=True, verbose_name='Last update')),
                ('is_loadable', models.BooleanField(verbose_name='Load data')),
                ('is_calculated', models.BooleanField(verbose_name='Calculate data')),
            ],
        ),
        migrations.CreateModel(
            name='Team',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField()),
                ('name', models.CharField(max_length=100, verbose_name='Team')),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.Country', verbose_name='Country')),
                ('load_source', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.LoadSource', verbose_name='Source')),
                ('sport', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.Sport', verbose_name='Sport')),
            ],
            bases=(core.models.SaveSlugCountryMixin, models.Model),
        ),
        migrations.CreateModel(
            name='TeamType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField(unique=True)),
                ('name', models.CharField(max_length=100, verbose_name='Team type')),
            ],
        ),
        migrations.CreateModel(
            name='TeamMembership',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('load_source', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.LoadSource')),
                ('season', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Season')),
                ('team', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Team')),
            ],
        ),
        migrations.AddField(
            model_name='team',
            name='team_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.TeamType', verbose_name='Team type'),
        ),
        migrations.CreateModel(
            name='Referee',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField()),
                ('name', models.CharField(max_length=100, verbose_name='Referee')),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.Country', verbose_name='Country')),
                ('load_source', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.LoadSource', verbose_name='Source')),
                ('sport', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.Sport', verbose_name='Sport')),
            ],
            bases=(core.models.SaveSlugCountryMixin, models.Model),
        ),
        migrations.CreateModel(
            name='MatchStats',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('stat_type', models.CharField(choices=[('g', 'Goals'), ('xg', 'xG'), ('yc', 'Yellow cards'), ('rc', 'Red cards'), ('pen', 'Penalies'), ('gm', 'Goals (minutes)'), ('xgm', 'xG (minutes)'), ('ycm', 'Yellow cards (minutes)'), ('rcm', 'Red cards (minutes)'), ('gt', 'Goal time'), ('s', 'Shots'), ('sot', 'Shots on target'), ('d', 'Deep passes'), ('ppda', 'PPDA'), ('c', 'Corners'), ('f', 'Fouls'), ('fk', 'Free kicks'), ('o', 'Offsides'), ('pos', 'Possession')], max_length=10, verbose_name='Stat')),
                ('competitor', models.CharField(choices=[('h', 'Home team'), ('a', 'Away team')], max_length=5, verbose_name='Competitor')),
                ('period', models.IntegerField(verbose_name='Period')),
                ('value', models.CharField(max_length=255, verbose_name='Value')),
                ('match', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Match', verbose_name='Match')),
            ],
        ),
        migrations.CreateModel(
            name='MatchReferee',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('load_source', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.LoadSource')),
                ('match', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Match')),
                ('referee', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Referee')),
            ],
        ),
        migrations.AddField(
            model_name='match',
            name='season',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.Season', verbose_name='Season'),
        ),
        migrations.AddField(
            model_name='match',
            name='team_a',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bcore_match_team_a_fk', to='core.Team', verbose_name='Away team'),
        ),
        migrations.AddField(
            model_name='match',
            name='team_h',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='bcore_match_team_h_fk', to='core.Team', verbose_name='Home team'),
        ),
        migrations.AddField(
            model_name='loadsource',
            name='sport',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.Sport', verbose_name='Sport'),
        ),
        migrations.AddField(
            model_name='league',
            name='load_source',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.LoadSource', verbose_name='Source'),
        ),
        migrations.AddField(
            model_name='league',
            name='sport',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='core.Sport', verbose_name='Sport'),
        ),
        migrations.AddField(
            model_name='league',
            name='team_type',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='core.TeamType', verbose_name='Team type'),
        ),
        migrations.CreateModel(
            name='CountryLoadSource',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('slug', models.SlugField()),
                ('name', models.CharField(blank=True, max_length=255, null=True, verbose_name='Object name')),
                ('status', models.CharField(choices=[('a', 'Active'), ('d', 'Deleted')], default='a', max_length=5, verbose_name='Status')),
                ('created', models.DateTimeField(blank=True, null=True, verbose_name='Created')),
                ('confirmed', models.DateTimeField(blank=True, null=True, verbose_name='Confirmed')),
                ('selected', models.DateTimeField(blank=True, null=True, verbose_name='Selected')),
                ('country', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='core_countryloadsource_country', to='core.Country', verbose_name='Country')),
                ('country_obj', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, related_name='object', to='core.Country', verbose_name='Country')),
                ('load_source', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='core_countryloadsource_load_source', to='core.LoadSource', verbose_name='Source')),
                ('sport', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='core_countryloadsource_sport', to='core.Sport', verbose_name='Sport')),
            ],
        ),
        migrations.AddField(
            model_name='country',
            name='load_source',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='core_country_load_source', to='core.LoadSource', verbose_name='Source'),
        ),
        migrations.AddConstraint(
            model_name='teammembership',
            constraint=models.UniqueConstraint(fields=('team', 'season'), name='unique_team_membership'),
        ),
        migrations.AddConstraint(
            model_name='team',
            constraint=models.UniqueConstraint(fields=('sport', 'country', 'slug'), name='unique_team'),
        ),
        migrations.AddConstraint(
            model_name='referee',
            constraint=models.UniqueConstraint(fields=('sport', 'country', 'slug'), name='unique_referee'),
        ),
        migrations.AddConstraint(
            model_name='matchstats',
            constraint=models.UniqueConstraint(fields=('match', 'stat_type', 'competitor', 'period'), name='unique_match_stats'),
        ),
        migrations.AddConstraint(
            model_name='matchreferee',
            constraint=models.UniqueConstraint(fields=('match', 'referee'), name='unique_match_referee'),
        ),
        migrations.AddIndex(
            model_name='match',
            index=models.Index(fields=['match_date'], name='match_date_idx'),
        ),
        migrations.AddConstraint(
            model_name='match',
            constraint=models.UniqueConstraint(fields=('league', 'team_h', 'team_a', 'match_date'), name='unique_match'),
        ),
        migrations.AddConstraint(
            model_name='loadsource',
            constraint=models.UniqueConstraint(fields=('sport', 'slug'), name='unique_load_source'),
        ),
        migrations.AddConstraint(
            model_name='league',
            constraint=models.UniqueConstraint(fields=('sport', 'country', 'slug'), name='unique_league'),
        ),
        migrations.AddConstraint(
            model_name='countryloadsource',
            constraint=models.UniqueConstraint(fields=('sport', 'slug', 'load_source'), name='unique_country_load_source'),
        ),

        migrations.RunPython(insertSport),
        migrations.RunPython(load_countries),
        migrations.RunPython(insertTeamTypes),
        migrations.RunPython(insertLoadSources),
    ]
