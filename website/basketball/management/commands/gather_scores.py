from copy import deepcopy
from datetime import date
import json
import logging
import re

from bs4 import BeautifulSoup
import requests

from django.core.management.base import BaseCommand
from basketball.management.urls import BASE_URL, box_scores

logger = logging.getLogger(__name__)

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
    'july',
    'august',
    'september',
]

def gather_box_scores(year, months=[]):
    # Either take given month or default months
    months = months or GAME_MONTHS
    all_box_scores = []
    for month in months:
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

class Command(BaseCommand):
    help = 'Gather box scores for year'

    def add_arguments(self, parser):
        parser.add_argument('year', type=int)
        parser.add_argument('--months', nargs='+')

    def handle(self, *args, **options):
        logger.info(f'Scrapping data for basketball from year {options["year"]}, month {options["months"]}')
        box_scores = gather_box_scores(options['year'], months=options['months'])
        print(json.dumps(box_scores, indent=4))
