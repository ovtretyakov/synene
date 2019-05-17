from django.core.exceptions import ObjectDoesNotExist

from .models import (
    Sport, 
    Country, 
    League, 
    Team, 
    )


def get_sport(slug):
    try:
        sport = Sport.objects.get(slug=slug)
    except ObjectDoesNotExist:
        sport = None
    return sport

def get_country(slug):
    try:
        country = Country.objects.get(slug=slug)
    except ObjectDoesNotExist:
        country = None
    return country

def get_league(sport, country, slug):
    try:
        league = League.objects.get(sport=sport,country=country,slug=slug)
    except ObjectDoesNotExist:
        league = None
    return league

def get_team(sport, country, slug):
    try:
        team = Team.objects.get(sport=sport,country=country,slug=slug)
    except ObjectDoesNotExist:
        team = None
    return team

