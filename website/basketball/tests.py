from io import StringIO
import json

import httpretty
import mock

from django.core.management import call_command
from django.test import TestCase

from basketball.management.urls import box_scores
from basketball.models import Game, Team
from basketball.test_data.box import DATA as box_data
from basketball.test_data.box_scores import DATA as box_score_data

EXPECTED_BOX_SCORES = '''[
    "https://www.basketball-reference.com/boxscores/201910220TOR.html",
    "https://www.basketball-reference.com/boxscores/201910220LAC.html"
]
'''

class GetBoxScoresTest(TestCase):

    @httpretty.activate
    def test_get_box_scores(self):
        with mock.patch('sys.stdout', new_callable=StringIO) as mock_print:
            box_score_url = box_scores('2020', 'october')
            httpretty.register_uri(httpretty.GET, box_score_url, body=box_score_data)
            call_command('gather_scores', '2020', '--months', 'october')
            output = mock_print.getvalue()
            self.assertEqual(output, EXPECTED_BOX_SCORES)

    @httpretty.activate
    def test_process_score(self):
        with mock.patch('sys.stdout', new_callable=StringIO) as mock_print:
            url = 'https://www.basketball-reference.com/boxscores/201910220TOR.html'
            httpretty.register_uri(httpretty.GET, url, body=box_data)
            call_command('process_scores', url)
            output = mock_print.getvalue()
            self.assertEqual(output, '')
        games = Game.objects.all()
        self.assertEqual(len(games), 1)
        teams = Team.objects.all()
        self.assertEqual(len(teams), 2)
