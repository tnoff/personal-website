import logging

from django.db.models import Q
from django.http import Http404
from django.shortcuts import render
from django_otp.decorators import otp_required

from basketball.models import Game, Team, TeamSeason

logger = logging.getLogger(__name__)


@otp_required
def standings(request, year=2020):
    '''
    Show Current Standings
    '''
    team_seasons = TeamSeason.objects.filter(team__year=year).order_by('-point_differential')
    for (count, team) in enumerate(team_seasons):
        team.standing = count + 1
        team.point_differential_per_game = (team.point_differential * 1.0) / (team.wins + team.losses)
        team.point_differential_per_game = '%.2f' % team.point_differential_per_game
        team.point_differential_last_eight = '%.2f' % team.point_differential_last_eight
    view_data = {
        'team_data': team_seasons,
    }
    return render(request, 'basketball/standings.html', view_data)

@otp_required
def team_show(request, year, short_name):
    '''
    Get team information
    '''
    team = Team.objects.filter(year=year, short_name=short_name).first()
    if not team:
        raise Http404(f'Unable to locate team')

    team_data = TeamSeason.objects.filter(team=team).first()
    if not team_data:
        raise Http404(f'Unable to locate team season data')

    team_data.point_differential_per_game = (team_data.point_differential * 1.0) / \
        (team_data.wins + team_data.losses)
    team_data.point_differential_per_game = '%.2f' % team_data.point_differential_per_game
    team_data.point_differential_last_eight = '%.2f' % team_data.point_differential_last_eight

    team_game_list = []
    for game in Game.objects.filter(Q(away_team=team) | Q(home_team=team)):
        if game.away_team == team:
            if game.away_score > game.home_score:
                game.result = "Win"
            else:
                game.result = "Loss"
            game.diff = game.away_score - game.home_score
        if game.home_team == team:
            if game.away_score > game.home_score:
                game.result = "Loss"
            else:
                game.result = "Win"
            game.diff = game.home_score - game.away_score
        team_game_list.append(game)
        # Make sure game diff is absolute value
        game.diff = abs(game.diff)

    view_data = {
        'games': team_game_list,
        'team_data': team_data,
    }

    return render(request, 'basketball/team.html', view_data)
