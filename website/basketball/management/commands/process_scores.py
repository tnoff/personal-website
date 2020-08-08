from copy import deepcopy
from datetime import date
import logging
import re

from bs4 import BeautifulSoup
import requests
from selenium import webdriver
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from unidecode import unidecode

from django.core.management.base import BaseCommand, CommandError
from django.db.models import Q
from django.db.utils import IntegrityError

from basketball.models import Game, GameRoster, GameRosterMembership, Lineup, GameLineupStats, Team, Player
from basketball.management.urls import BASE_URL, espn_date_scores, espn_game_play_by_play


logger = logging.getLogger(__name__)

TEAMS_HREF_REGEX = r'^/teams/(?P<short_name>[A-Z0-9]+)/(?P<year>[0-9]+).html'
BOX_SCORE_DATE_REGEX = r'^(?P<year>[0-9]{4})(?P<month>[0-9]{2})(?P<day>[0-9]{2}).*'
BOXSCORE_URL = f'{BASE_URL}/boxscores/(?P<suffix>.*)'
PLAYER_HREF_REGEX = r'^/players/[a-z]/?(?P<player_tag>.*).html'

ESPN_GAMEID_REGEX = r'.*gameId=(?P<game_id>[0-9]+)/?$'
ESPN_TEAM_REGEX = r'^/nba/team/_/name/([a-z]+)/(?P<long_name>.*)'
ESPN_SUB_REGEX = r'^(?P<new_player>.*) enters the game for (?P<old_player>.*)'

ESPN_GAME_CACHE = {}

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

    return game


def _process_action(column):
    children = []
    for child in column:
        if child == '\xa0':
            return children
        if isinstance(child, str):
            children.append(child.strip())
        # Else assume player
        else:
            matcher = re.match(PLAYER_HREF_REGEX, child.get('href'))
            player = Player.objects.get(tag=matcher.group('player_tag'))
            children.append(player)
    return children

def _espn_guess_team(team_column, game):
    first_href = team_column.find('a')
    short_name_matcher = re.match(ESPN_TEAM_REGEX, first_href.get('href'))
    if not short_name_matcher:
        raise Exception(f'Invalid team name {first_href.get("href")}')
    # Get long name here since short names aren't consistent ( thanks ESPN )
    long_name = short_name_matcher.group('long_name')
    long_name = ' '.join(i.capitalize() for i in long_name.split('-'))
    team_year = game.date.year
    # If october of later, assume season ends next year
    if game.date.month > 9:
        team_year += 1
    return Team.objects.filter(name=long_name, year=team_year).first()

def _apply_quarter_subs(quarter_sub, away_roster, home_roster, away_players, home_players):
    sub_match = re.match(ESPN_SUB_REGEX, quarter_sub)
    old_player_name = sub_match.group('old_player')
    new_player_name = sub_match.group('new_player')

    old_player = None
    new_player = None

    for roster_member in GameRosterMembership.objects.filter(Q(roster=away_roster) | Q(roster=home_roster)):
        # ESPN doesnt have characters on players names so keep that in mind when comparing here
        # On most lineups basketball reference gives you the name with the Jr, Sr, III, etc.. suffixes
        # They keep this on the main page, but that isnt where were getting that data
        # Add a check here for if the player name in the ESPN string, as this will catch these cases
        if old_player and new_player:
            break
        if not old_player:
            if unidecode(roster_member.player.name).replace('.', '') in old_player_name.replace('.', ''):
                old_player = roster_member.player
        if not new_player:
            if unidecode(roster_member.player.name).replace('.', '') in new_player_name.replace('.', ''):
                new_player = roster_member.player

    if old_player is None or new_player is None:
        raise Exception(f'Unable to find player for sub match {sub_match}')

    team = 0
    if old_player in home_players:
        team = 1
    return team, old_player, new_player

def _get_time_seconds(quarter, time):
    '''
    Time since tip-off
    '''
    time_split = time.split(':')
    return ((int(quarter) - 1) * 12 * 60) + (12 * 60 - ((int(time_split[0]) * 60) + float(time_split[1])))

def _ensure_lineup(players, team, game):
    lineup = Lineup.objects.filter(team=team)
    for player in players:
        lineup = lineup.filter(players=player)
    lineup = lineup.first()

    if not lineup:
        lineup = Lineup(team=team)
        lineup.save()
        for player in players:
            lineup.players.add(player)
        lineup.save()

    game_lineup = GameLineupStats.objects.filter(lineup=lineup, game=game).first()
    if not game_lineup:
        game_lineup = GameLineupStats(lineup=lineup, game=game,
                                      seconds_played=0,
                                      point_differential=0)
        game_lineup.save()
    return game_lineup

def _replace_players(team, players, old_player, new_player, game):
    players.remove(old_player)
    players.append(new_player)
    lineup = _ensure_lineup(players, team, game)
    return players, lineup

def _get_score(score_text):
    score_split = score_text.split('-')
    away = int(score_split[0])
    home = int(score_split[1])
    return away, home

def _calculate_lineup_results(lineup, seconds, lineup_enter_time, lineup_enter_score_diff, current_diff):
    lineup.seconds_played += (seconds - lineup_enter_time)
    lineup.point_differential += (current_diff - lineup_enter_score_diff)
    lineup.save()
    return seconds, current_diff

def process_play_by_play(driver, play_by_play_url, game):
    '''
    Get play by play info from url
    '''
    req = requests.get(play_by_play_url)
    if req.status_code != 200:
        logger.warning(f'Unable to process box score url {play_by_play_url}')
        return
    soup = BeautifulSoup(req.text, 'html.parser')

    play_by_play_div = soup.find('div', {'id': 'all_pbp'})
    play_by_play_table = play_by_play_div.find('table')

    # Reset all game lineup stats back to zero
    for game_stats in GameLineupStats.objects.filter(game=game):
        game_stats.seconds_played = 0
        game_stats.point_differential = 0
        game_stats.save()    

    # Before going through play by play, get starters for game
    # Set these as the lineups
    away_team = game.away_team
    home_team = game.home_team
    away_roster = GameRoster.objects.filter(game=game, team=away_team).first()
    home_roster = GameRoster.objects.filter(game=game, team=home_team).first()
    away_players = [member.player for member in GameRosterMembership.objects.filter(roster=away_roster, starter=True)]
    home_players = [member.player for member in GameRosterMembership.objects.filter(roster=home_roster, starter=True)]

    away_lineup = _ensure_lineup(away_players, away_team, game)
    home_lineup = _ensure_lineup(home_players, home_team, game)

    # Keep track of time when lineup entered game
    away_lineup_enter_time = 0
    home_lineup_enter_time = 0
    # Score diff when lineup entered game
    away_lineup_enter_score_diff = 0
    home_lineup_enter_score_diff = 0 

    # Basketball Reference is amazing but it does one fucking stupid ass thing that breaks this whole code
    # It does not tell you if someone was subbed in at the start of a quarter
    # Why? I dont fucking know, its fucking stupid
    # Ok so how do you get around this? One straight-forward-ish way
    # ESPN play by play sucks but does at least have this info

    # First get the game date
    espn_url = espn_date_scores(game.date)
    driver.get(espn_url)
    espn_soup = BeautifulSoup(driver.page_source, 'html.parser')

    events_div = espn_soup.find('div', {'id': 'events'})
    correct_game_id = None
    for article in events_div.find_all('article'):
        if 'basketball' not in article.get('class'):
            continue
        game_id = article.get('id')
        try:
            cached_data = ESPN_GAME_CACHE[game.date.strftime('%Y-%m-%d')][game_id]
            espn_away_team = Team.objects.get(pk=cached_data['away_team'])
            espn_home_team = Team.objects.get(pk=cached_data['home_team'])
        except KeyError:
            teams = article.find('tbody', {'id': 'teams'})
            away = teams.find('td', {'class': 'away'})
            # These can possibly be none, team has not been processed yet
            espn_away_team = _espn_guess_team(teams.find('td', {'class': 'away'}), game)
            espn_home_team = _espn_guess_team(teams.find('td', {'class': 'home'}), game)
            if espn_away_team is not None and espn_home_team is not None:
                ESPN_GAME_CACHE.setdefault(game.date.strftime('%Y-%m-%d'), {})
                ESPN_GAME_CACHE[game.date.strftime('%Y-%m-%d')][game_id] = {
                    'away_team' : espn_away_team.id,
                    'home_team' : espn_home_team.id,
                }
        if espn_away_team == away_team and espn_home_team == home_team:
            correct_game_id = game_id

    if not correct_game_id:
        raise Exception('Unable to find game')

    # From ESPN, grab list of substituions at beginning of quarter
    espn_url = espn_game_play_by_play(correct_game_id)
    driver.get(espn_url)
    espn_soup = BeautifulSoup(driver.page_source, 'html.parser')
    div_play_by_play = espn_soup.find('div', {'id':'gamepackage-play-by-play'})

    # Do while we still have valid quarters
    quarter = 2
    subs_at_start_of_quarter = [[]]
    while True:
        quarter_subs = []
        quarter_div = div_play_by_play.find('div', {'id': f'gp-quarter-{quarter}'})
        if not quarter_div:
            break
        # Grab substituion strings
        for details in quarter_div.find_all('td', {'class': 'game-details'}):
            if 'enters the game for' in details.text:
                quarter_subs.append(details.text)
                continue
            break
        quarter += 1
        subs_at_start_of_quarter.append(quarter_subs)

    # Ok time to actually go through basketball reference play by play now
    quarter = None
    for row in play_by_play_table.find_all('tr'):
        # Quarter/Overtime headers
        row_class = row.get('class')
        if row_class:
            row_class = row_class[0]
        row_id = row.get('id')
        # Set current quarter
        if row_class == 'thead':
            if row_id:
                quarter_result = re.match('^q(?P<quarter>[0-9]+)$', row_id)
                if not quarter_result:
                    raise Exception(f'Invalid quarter {row.get("class")}')
                quarter = int(quarter_result.group('quarter'))

                if quarter == 1:
                    continue

                if len(subs_at_start_of_quarter[quarter - 1]) > 0:
                    # Set lineup stats
                    seconds = (quarter - 1) * 12 * 60
                    away_lineup_enter_time, away_lineup_enter_score_diff = _calculate_lineup_results(away_lineup, seconds,
                                                                                                     away_lineup_enter_time, away_lineup_enter_score_diff,
                                                                                                     away_score - home_score)
                    home_lineup_enter_time, home_lineup_enter_score_diff = _calculate_lineup_results(home_lineup, seconds,
                                                                                                     home_lineup_enter_time, home_lineup_enter_score_diff,
                                                                                                     home_score - away_score)
                    # Handle start of quarter subs
                    for quarter_sub in subs_at_start_of_quarter[quarter - 1]:
                        team_flag , old_player, new_player = _apply_quarter_subs(quarter_sub,
                                                                                 away_roster, home_roster,
                                                                                 away_players, home_players)

                        if not team_flag:
                            away_players, away_lineup = _replace_players(away_team, away_players,
                                                                         old_player, new_player, game)
                        else:
                            home_players, home_lineup = _replace_players(home_team, home_players,
                                                                         old_player, new_player, game)
        # Else its just an ordinary play
        else:
            columns = row.find_all('td')
            if len(columns) < 3:
                # Assume end of quarter message
                continue
            # Basic metadata
            time = columns[0].text
            seconds = _get_time_seconds(quarter, time)
            away_team_score_delta = columns[2].text
            away_score, home_score = _get_score(columns[3].text)
            current_score = columns[3].text
            home_team_score_delta = columns[4].text

            # Text of what happened
            away_team_actions = _process_action(columns[1])
            home_team_actions = _process_action(columns[5])

            # TODO fix bug where someone checks in on a free throw

            # Handle substitutions
            if 'enters the game for' in away_team_actions:
                new_player = away_team_actions[0]
                old_player = away_team_actions[2]

                away_lineup_enter_time, away_lineup_enter_score_diff = _calculate_lineup_results(away_lineup, seconds,
                                                                                                 away_lineup_enter_time, away_lineup_enter_score_diff,
                                                                                                 away_score - home_score)
                away_players, away_lineup = _replace_players(away_team, away_players,
                                                             old_player, new_player, game)

            if 'enters the game for' in home_team_actions:
                new_player = home_team_actions[0]
                old_player = home_team_actions[2]

                home_lineup_enter_time, home_lineup_enter_score_diff = _calculate_lineup_results(home_lineup, seconds,
                                                                                                 home_lineup_enter_time, home_lineup_enter_score_diff,
                                                                                                 home_score - away_score)
                home_players, home_lineup = _replace_players(home_team, home_players,
                                                             old_player, new_player, game)


    # Make sure we update stats for end of game
    seconds = quarter * 12 * 60
    _calculate_lineup_results(away_lineup, seconds,
                              away_lineup_enter_time, away_lineup_enter_score_diff,
                              away_score - home_score)
    _calculate_lineup_results(home_lineup, seconds,
                              home_lineup_enter_time, home_lineup_enter_score_diff,
                              home_score - away_score)

class Command(BaseCommand):
    help = 'Process given box scores'

    def add_arguments(self, parser):
        parser.add_argument('box_scores', nargs='+')

    def handle(self, *args, **options):
        binary = '/usr/bin/firefox'
        firefox_options = Options()
        firefox_options.set_headless(headless=True)
        firefox_options.binary = binary
        cap = DesiredCapabilities().FIREFOX
        cap["marionette"] = True #optional
        driver = webdriver.Firefox(firefox_options=firefox_options, capabilities=cap, executable_path='/usr/local/bin/geckodriver')

        for box_score in options['box_scores']:
            logger.debug(f'Processing new box score {box_score}')
            game = process_box_score(box_score)

            match = re.match(BOXSCORE_URL, box_score)
            play_by_play_url = f'{BASE_URL}/boxscores/pbp/{match.group("suffix")}'
            process_play_by_play(driver, play_by_play_url, game)

        driver.quit()
