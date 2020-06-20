from copy import deepcopy
from datetime import date
import logging
import re

from bs4 import BeautifulSoup
import requests

from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError

from basketball.models import Game, Team


logger = logging.getLogger(__name__)

BASE_URL = 'https://www.basketball-reference.com'
GAME_MONTHS = [
    'october',
    'november',
    'december',
    'january',
    'february',
    'march',
    'april',
    'may',
    'june',
]

TEAMS_HREF_REGEX = r'^/teams/(?P<short_name>[A-Z0-9]+)/(?P<year>[0-9]+).html'
BOX_SCORE_DATE_REGEX = r'^(?P<year>[0-9]{4})(?P<month>[0-9]{2})(?P<day>[0-9]{2}).*'


def box_scores(year, month):
    '''
    Get url for boxscores from month
    '''
    return f'{BASE_URL}/leagues/NBA_{year}_games-{month}.html'

def gather_box_scores(year):
    all_box_scores = []
    for month in GAME_MONTHS:
        logger.debug(f'Generating box scores for month {month}')
        url = box_scores(year, month)
        req = requests.get(url)
        if req.status_code != 200:
            logger.warning(f'Unable to generate information from url {url}')
            continue
        logger.info(f'Generating box scores from {url}')
        soup = BeautifulSoup(req.text, 'html.parser')
        schedule_table = soup.find('table', id='schedule')
        for box_score in schedule_table.find_all('td', {'data-stat': 'box_score_text'}):
            try:
                all_box_scores.append(f'{BASE_URL}{box_score.find("a").get("href")}')
            except AttributeError:
                pass
    return all_box_scores

def _get_team_metadata(soup):
    teams = soup.find_all('div', {'itemtype': 'https://schema.org/Organization'})
    if len(teams) != 2:
        raise StatProcessorException(f'Invalid number of teams {len(teams)}')
    away_team = None
    home_team = None

    for (count, team) in enumerate(teams):
        info = team.find('strong').find('a')
        processed_team_data = re.match(TEAMS_HREF_REGEX, info.get('href'))
        team_data = {
            'year': int(processed_team_data.group('year')),
            'short_name': processed_team_data.group('short_name'),
            'name': info.text,
        }

        if count == 0:
            away_team = deepcopy(team_data)
        else:
            home_team = deepcopy(team_data)

        team_id = None
        try:
            new_team = Team(**team_data)
            new_team.save()
            logger.info(f'Adding new team {team_data}, id {new_team.id}')
        except IntegrityError:
            logger.debug(f'Unable to add new team {team_data}, team likely already exists')
            new_team = [i for i in Team.objects.filter(year=team_data['year'], short_name=team_data['short_name'])][0]

        if count == 0:
            away_team = new_team
        else:
            home_team = new_team

    scores = soup.find_all('div', {'class': 'score'})
    for (count, score) in enumerate(scores):
        if count == 0:
            away_team.score = int(score.text)
        else:
            home_team.score  = int(score.text)
    return away_team, home_team

def process_box_score(box_score_url):
    '''
    Process data from box scores
    box_score_url   :   Box Score URL
    '''
    date_info = re.match(BOX_SCORE_DATE_REGEX, box_score_url.split('/')[-1])
    game_date = date(year=int(date_info.group('year')),
                     month=int(date_info.group('month')),
                     day=int(date_info.group('day')))
    req = requests.get(box_score_url)
    if req.status_code != 200:
        logger.warning(f'Unable to process box score url {box_score_url}')
        return
    soup = BeautifulSoup(req.text, 'html.parser')

    away_team, home_team = _get_team_metadata(soup)

    try:
        game_data = {
            'date': game_date,
            'away_team': away_team,
            'away_score': away_team.score,
            'home_team': home_team,
            'home_score': home_team.score,
        }
        new_game = Game(**game_data)
        new_game.save()
        logger.info(f'Adding new game {game_data}, id {new_game.id}')
    except IntegrityError:
        logger.debug(f'Unable to add new game {game_data}, assuming it already exists')
        pass 

class Command(BaseCommand):
    help = 'Gather box scores for year'

    def add_arguments(self, parser):
        parser.add_argument('year', type=int)

    def handle(self, *args, **options):
        logger.info(f'Scrapping data for basketball from year {options["year"]}')

        box_scores = gather_box_scores(options['year'])
        for box_score in box_scores:
            logger.debug(f'Processing new box score {box_score}')
            process_box_score(box_score)
