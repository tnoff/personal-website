BASE_URL = 'https://www.basketball-reference.com'

def box_scores(year, month):
    '''
    Get url for boxscores from month
    '''
    return f'{BASE_URL}/leagues/NBA_{year}_games-{month}.html'

