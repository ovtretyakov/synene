from django.core.exceptions import ObjectDoesNotExist


def get_sport(slug):
    from .models import Sport
    try:
        sport = Sport.objects.get(slug=slug)
    except ObjectDoesNotExist:
        sport = None
    return sport

def get_country(slug):
    from .models import Country
    try:
        country = Country.objects.get(slug=slug)
    except ObjectDoesNotExist:
        country = None
    return country

def get_league(sport, country, slug):
    from .models import League
    try:
        league = League.objects.get(sport=sport,country=country,slug=slug)
    except ObjectDoesNotExist:
        league = None
    return league

def get_team(sport, country, slug):
    from .models import Team
    try:
        team = Team.objects.get(sport=sport,country=country,slug=slug)
    except ObjectDoesNotExist:
        team = None
    return team

