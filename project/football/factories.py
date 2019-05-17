from django.core.exceptions import ObjectDoesNotExist

from core.models import Sport
from .models import FootballTeam, FootballReferee


def get_football():
    try:
        sport = Sport.objects.get(slug=Sport.FOOTBALL)
    except ObjectDoesNotExist:
        sport = None
    return sport


def get_football_league(country, slug):
    try:
        league = FootballLeague.objects.get(country=country,slug=slug)
    except ObjectDoesNotExist:
        league = None
    return league


def get_football_team(country, slug):
    try:
        team = FootballTeam.objects.get(country=country,slug=slug)
    except ObjectDoesNotExist:
        team = None
    return team


def get_football_referee(country, slug):
    try:
        referee = FootballReferee.objects.get(country=country,slug=slug)
    except ObjectDoesNotExist:
        referee = None
    return referee
