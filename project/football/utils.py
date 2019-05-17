from .models import FootballTeam

###################################################################
def get_or_create_football_league(slug, source=None, country=None, team_type=None):
    #!!!!!
    if not country:
        country = Country.objects.get(slug='na')
    league, created = FootballLeague.objects.get_or_create(country=country,slug=slug)
    return league


###################################################################
def get_or_create_football_team(slug, source=None, country=None, team_type=None):
    #!!!!!
    if not country:
        country = Country.objects.get(slug='na')
    team, created = FootballTeam.objects.get_or_create(country=country,slug=slug)
    return team
