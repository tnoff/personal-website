from django.db import models

class Team(models.Model):
    class Meta:
        unique_together = ('year', 'short_name')

    year = models.IntegerField(blank=False, null=False)
    name = models.CharField(max_length=128)
    short_name = models.CharField(max_length=8)

    def __str__(self):
        return f'{self.year}-{self.short_name}'

class Game(models.Model):
    class Meta:
        unique_together = ('date', 'away_team', 'home_team')

    date = models.DateField(blank=False, null=False)
    away_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='away_team')
    home_team = models.ForeignKey(Team, on_delete=models.CASCADE, related_name='home_team')
    away_score = models.IntegerField(blank=False, null=False)
    home_score = models.IntegerField(blank=False, null=False)

    def __str__(self):
        return f'{self.date} - {self.away_team} vs {self.home_team}'

class TeamSeason(models.Model):
    team = models.OneToOneField(Team, on_delete=models.CASCADE, related_name='team_season')
    wins = models.IntegerField(blank=False, null=False)
    losses = models.IntegerField(blank=False, null=False)
    point_differential = models.FloatField(blank=False, null=False)
    wins_last_eight = models.IntegerField(blank=False, null=False)
    losses_last_eight = models.IntegerField(blank=False, null=False)
    point_differential_last_eight = models.FloatField(blank=False, null=False)

    def __str__(self):
        return f'{self.team} - {self.wins}-{self.losses}'

class Player(models.Model):
    tag = models.CharField(max_length=16, primary_key=True)
    name = models.CharField(max_length=255)

class GameRoster(models.Model):
    class Meta:
        unique_together = ('team', 'game')

    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)

class GameRosterMembership(models.Model):
    class Meta:
        unique_together = ('roster', 'player')
    roster = models.ForeignKey(GameRoster, on_delete=models.CASCADE)
    player = models.ForeignKey(Player, on_delete=models.CASCADE)
    starter = models.BooleanField(default=False)

class Lineup(models.Model):
    team = models.ForeignKey(Team, on_delete=models.CASCADE)
    players = models.ManyToManyField(Player)

class GameLineupStats(models.Model):
    lineup = models.ForeignKey(Lineup, on_delete=models.CASCADE)
    game = models.ForeignKey(Game, on_delete=models.CASCADE)
    seconds_played = models.IntegerField(blank=False, null=False)
    point_differential = models.IntegerField(blank=False, null=False) 
