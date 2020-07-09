from copy import deepcopy
from datetime import date
import logging
import re

from bs4 import BeautifulSoup
import requests

from django.core.management.base import BaseCommand, CommandError
from django.db.utils import IntegrityError

from basketball.models import Game, GameRoster, GameRosterMembership, Team, Player


logger = logging.getLogger(__name__)

TEAMS_HREF_REGEX = r'^/teams/(?P<short_name>[A-Z0-9]+)/(?P<year>[0-9]+).html'
BOX_SCORE_DATE_REGEX = r'^(?P<year>[0-9]{4})(?P<month>[0-9]{2})(?P<day>[0-9]{2}).*'

def _get_team_metadata(soup):
    '''
    Grab team info from top of page
    '''
    teams = soup.find_all('div', {'itemtype': 'https://schema.org/Organization'})
    if len(teams) != 2:
        raise Exception(f'Invalid number of teams {len(teams)}')
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

        try:
            team = Team(**team_data)
            team.save()
            logger.info(f'Adding new team {team_data}, id {team.id}')
        except IntegrityError:
            team = [i for i in Team.objects.filter(year=team_data['year'], short_name=team_data['short_name'])][0]

        if count == 0:
            away_team = team
        else:
            home_team = team

    scores = soup.find_all('div', {'class': 'score'})
    for (count, score) in enumerate(scores):
        if count == 0:
            away_team.score = int(score.text)
        else:
            home_team.score  = int(score.text)
    return away_team, home_team

def _add_game_roster(team, game):
    '''
    Either add new roster or get existing one
    '''
    try:
        team_roster = GameRoster(team=team, game=game)
        team_roster.save()
        logger.info(f'Adding game roster {team_roster.id}')
    except IntegrityError:
        team_roster = [i for i in GameRoster.objects.filter(team=team, game=game)][0]
    return team_roster

def _add_player(player_th):
    '''
    Either add new player or get existing one
    '''
    player_tag = player_th.get('data-append-csv')
    if not player_tag:
        return None
    player_name = player_th.find('a').text
    try:
        player = Player(tag=player_tag, name=player_name)
        player.save()
        logger.info(f'Adding a new player {player.tag}')
    except IntegrityError:
        player = Player.objects.get(key=player_tag)
    return player

def process_box_score(box_score_url):
    '''
    Process data from box scores
    box_score_url   :   Box Score URL
    '''

    # First grab date info
    date_info = re.match(BOX_SCORE_DATE_REGEX, box_score_url.split('/')[-1])
    game_date = date(year=int(date_info.group('year')),
                     month=int(date_info.group('month')),
                     day=int(date_info.group('day')))

    # Then get html result
    req = requests.get(box_score_url)
    if req.status_code != 200:
        logger.warning(f'Unable to process box score url {box_score_url}')
        return
    soup = BeautifulSoup(req.text, 'html.parser')

    # Get the team data first from the top
    away_team, home_team = _get_team_metadata(soup)

    # Add game data here first
    try:
        game_data = {
            'date': game_date,
            'away_team': away_team,
            'away_score': away_team.score,
            'home_team': home_team,
            'home_score': home_team.score,
        }
        game = Game(**game_data)
        game.save()
        logger.info(f'Adding new game {game_data}, id {game.id}')
    except IntegrityError:
        game = [i for i in Game.objects.filter(date=game_date, away_team=away_team, home_team=home_team)][0]

    # Get game rosters
    away_team_roster = _add_game_roster(away_team, game)
    home_team_roster = _add_game_roster(home_team, game)

    # How the tables get formatted here are a little weird
    # Basically the last first half of the tables are team one
    # Then the second half are team two
    stats_tables = soup.find_all('table', {'class': 'stats_table'})
    away_team_table = stats_tables[0]
    home_team_table = stats_tables[int(len(stats_tables)/2)]
    # For home and away team, get rosters
    # Assume here that the first 5 players are starters
    for (count, player_th) in enumerate(away_team_table.find_all('th', {'data-stat': 'player'})):
        player = _add_player(player_th)
        if not player:
            continue

        starter = False
        if count < 6:
            starter = True
        try:
            roster_membership = GameRosterMembership(roster=away_team_roster, player=player, starter=starter)
            roster_membership.save()
        except IntegrityError:
            pass

    for (count, player_th) in enumerate(home_team_table.find_all('th', {'data-stat': 'player'})):
        player = _add_player(player_th)
        if not player:
            continue

        starter = False
        if count < 6:
            starter = True
        try:
            roster_membership = GameRosterMembership(roster=home_team_roster, player=player, starter=starter)
            roster_membership.save()
        except IntegrityError:
            pass

class Command(BaseCommand):
    help = 'Process given box scores'

    def add_arguments(self, parser):
        parser.add_argument('box_scores', nargs='+')

    def handle(self, *args, **options):
        for box_score in options['box_scores']:
            logger.debug(f'Processing new box score {box_score}')
            process_box_score(box_score)
