import logging

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from django.db.utils import IntegrityError

from basketball.models import Game, Team, TeamSeason


logger = logging.getLogger(__name__)

def _generate_team_dict(team):
    return {
        'team': team,
        'wins': 0,
        'losses': 0,
        'point_differential': 0,
        'wins_last_eight': 0,
        'losses_last_eight': 0,
        'point_differential_last_eight': 0,
    }

def _generate_team_data(year, team=None):
    '''
    Generate team data

    team_id     :   If passed, only return for single team
    '''
    if not (team or year):
        raise Exception('Year or team needed to generate data')

    logger.debug('Gathering team metadata')
    team_data = {}

    if year:
        all_teams = Team.objects.filter(year=year)
    else:
        all_teams = Team.objects.filter(year=team.year)
    for team_obj in all_teams:
        team_data[team_obj.id] = _generate_team_dict(team_obj)
    
    # If team passed, only return games with those players
    if not team:
        games = Game.objects.filter(Q(away_team__year=year) & Q(home_team__year=year))
    else:
        games = Game.objects.filter(Q(away_team=team) | Q(home_team=team))

    # Iterate backwards to get last 8 games today
    logger.info('Iterating through game data')
    for game in games.order_by('-date'):
        logger.debug(f'Generating info from game {game.id}')
        away_team = team_data[game.away_team.id]
        home_team = team_data[game.home_team.id]

        if game.away_score > game.home_score:
            away_team['wins'] += 1
            home_team['losses'] += 1

            # Check if last 8 games
            if away_team['wins'] + away_team['losses'] <= 8:
                away_team['wins_last_eight'] += 1
            if home_team['wins'] + home_team['losses'] <= 8:
                home_team['losses_last_eight'] += 1

        else:
            away_team['losses'] += 1
            home_team['wins'] += 1

            # Check if last 8 games
            if away_team['wins'] + away_team['losses'] <= 8:
                away_team['losses_last_eight'] += 1
            if home_team['wins'] + home_team['losses'] <= 8:
                home_team['wins_last_eight'] += 1

        away_team['point_differential'] += game.away_score - game.home_score
        home_team['point_differential'] += game.home_score - game.away_score

        # Check if last 8 games
        if away_team['wins'] + away_team['losses'] <= 8:
            away_team['point_differential_last_eight'] += game.away_score - game.home_score
        if home_team['wins'] + home_team['losses'] <= 8:
            home_team['point_differential_last_eight'] += game.home_score - game.away_score

    # Transform team data into list for later use
    team_data_list = []
    for key, value in team_data.items():
        new_dict = value
        new_dict['id'] = key
        # Add points differntial per game
        try:
            per_game = new_dict['point_differential'] * 1.0 / (new_dict['wins'] + new_dict['losses'])
            new_dict['point_differential_per_game'] = per_game
        except ZeroDivisionError:
            new_dict['point_differential_per_game'] = 0.0
        try:
            per_game_eight = new_dict['point_differential_last_eight'] * 1.0 / (new_dict['wins_last_eight'] + new_dict['losses_last_eight'])
            new_dict['point_differential_last_eight'] = per_game_eight
        except ZeroDivisionError:
            new_dict['point_differential_last_eight'] = 0.0
        team_data_list.append(new_dict)
    return team_data_list

class Command(BaseCommand):
    help = 'Process stats for given year'

    def add_arguments(self, parser):
        parser.add_argument('year', type=int)

    def handle(self, *args, **options):
        team_data_list =  _generate_team_data(options['year'])
        for team_data in team_data_list:
            new_season = TeamSeason(
                team=team_data['team'],
                wins=team_data['wins'],
                losses=team_data['losses'],
                point_differential=team_data['point_differential'],
                wins_last_eight=team_data['wins_last_eight'],
                losses_last_eight=team_data['losses_last_eight'],
                point_differential_last_eight=team_data['point_differential_last_eight']
            )
            try:
                new_season.save()
            except IntegrityError:
                existing_season = TeamSeason.objects.filter(team=team_data['team']).first()
                if existing_season.wins != team_data['wins'] or \
                        existing_season.losses != team_data['losses']:
                    existing_season.wins = team_data['wins']
                    existing_season.losses = team_data['losses']
                    existing_season.point_differential = team_data['point_differential']
                    existing_season.wins_last_eight = team_data['wins_last_eight']
                    existing_season.losses_last_eight =  team_data['losses_last_eight']
                    existing_season.point_differential_last_eight = team_data['point_differential_last_eight']
                    existing_season.save()
