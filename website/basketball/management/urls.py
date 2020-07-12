BASE_URL = 'https://www.basketball-reference.com'
ESPN_URL = 'https://www.espn.com'

def box_scores(year, month):
    '''
    Get url for boxscores from month
    '''
    return f'{BASE_URL}/leagues/NBA_{year}_games-{month}.html'

def espn_date_scores(date):
    '''
    Get url for dates scores
    '''
    return f'{ESPN_URL}/nba/scoreboard/_/date/{date.strftime("%Y%m%d")}'

def espn_game_play_by_play(game_id):
    '''
    Get ESPN url for play by play
    '''
    return f'{ESPN_URL}/nba/playbyplay?gameId={game_id}'
