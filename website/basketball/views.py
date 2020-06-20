import logging

from django_otp.decorators import otp_required
from django.shortcuts import render

from basketball.models import Game, Team

logger = logging.getLogger(__name__)

def _generate_team_data():
    logger.debug('Gathering team metadata')
    team_data = {}
    for team in Team.objects.all():
        team_data[team.id] = {
            'short_name': team.short_name,
            'name': team.name,
            'wins': 0,
            'losses': 0,
            'point_differential': 0,
            'wins_last_eight': 0,
            'losses_last_eight': 0,
            'point_differential_last_eight': 0,
        }
    logger.info('Iterating through game data')
    # Iterate backwards to get last 8 games today
    for game in Game.objects.all().order_by('-date'):
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
        per_game = new_dict['point_differential'] * 1.0 / (new_dict['wins'] + new_dict['losses'])
        new_dict['point_differential_per_game'] = per_game
        per_game_eight = new_dict['point_differential_last_eight'] * 1.0 / (new_dict['wins_last_eight'] + new_dict['losses_last_eight'])
        new_dict['point_differential_last_eight'] = per_game_eight
        team_data_list.append(new_dict)
    return team_data_list

@otp_required
def standings(request):
    '''
    Show Current Standings
    '''
    team_data = _generate_team_data()
    team_data = sorted(team_data, key=lambda k: k['point_differential_per_game'], reverse=True)
    for (count, team) in enumerate(team_data):
        team['standing'] = count
        team['point_differential_per_game'] = '%.2f' % team['point_differential_per_game']
        team['point_differential_last_eight'] = '%.2f' % team['point_differential_last_eight']
    view_data = {
        'team_data': team_data,
    }
    return render(request, 'basketball/standings.html', view_data)
