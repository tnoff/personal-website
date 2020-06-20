import logging

from django.db.models import Q
from django.http import Http404
from django.shortcuts import render
from django_otp.decorators import otp_required

from basketball.models import Game, Team

logger = logging.getLogger(__name__)

def _generate_team_dict(team):
    return {
        'short_name': team.short_name,
        'name': team.name,
        'year': team.year,
        'wins': 0,
        'losses': 0,
        'point_differential': 0,
        'wins_last_eight': 0,
        'losses_last_eight': 0,
        'point_differential_last_eight': 0,
    }

def _generate_team_data(year=None, team=None):
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
    return team_data_list, games

@otp_required
def standings(request, year=2020):
    '''
    Show Current Standings
    '''
    team_data, _games = _generate_team_data(year=year)
    team_data = sorted(team_data, key=lambda k: k['point_differential_per_game'], reverse=True)
    for (count, team) in enumerate(team_data):
        team['standing'] = count + 1
        team['point_differential_per_game'] = '%.2f' % team['point_differential_per_game']
        team['point_differential_last_eight'] = '%.2f' % team['point_differential_last_eight']
    view_data = {
        'team_data': team_data,
    }
    return render(request, 'basketball/standings.html', view_data)

@otp_required
def team_show(request, year, short_name):
    '''
    Get team information
    '''
    try:
        team = [i for i in Team.objects.filter(year=year, short_name=short_name)][0]
    except IndexError:
        raise Http404(f'Unable to locate team')

    team_data, games = _generate_team_data(team=team)
    this_team = None

    for team_obj in team_data:
        if not team_obj['id'] == team.id:
            continue
        team_obj['point_differential_per_game'] = '%.2f' % team_obj['point_differential_per_game']
        team_obj['point_differential_last_eight'] = '%.2f' % team_obj['point_differential_last_eight']
        this_team = team_obj

    # Generate results per game
    team_game_list = []
    for game in reversed(games):
        if game.away_team.id == this_team['id']:
            if game.away_score > game.home_score:
                game.result = "Win"
            else:
                game.result = "Loss"
            game.diff = game.away_score - game.home_score
        if game.home_team.id == this_team['id']:
            if game.away_score > game.home_score:
                game.result = "Loss"
            else:
                game.result = "Win"
            game.diff = game.home_score - game.away_score
        team_game_list.append(game)

    view_data = {
        'all_team_data': team_data,
        'games': team_game_list,
        'team': team,
        'team_data': this_team,
    }

    return render(request, 'basketball/team.html', view_data)
