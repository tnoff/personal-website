from django.contrib import admin

from basketball.forms import GameForm, TeamForm
from basketball.models import Game, Team, Player, Lineup, GameLineupStats

class GameAdmin(admin.ModelAdmin):
    form = GameForm

class TeamAdmin(admin.ModelAdmin):
    form = TeamForm

class PlayerAdmin(admin.ModelAdmin):
    pass

class LineupAdmin(admin.ModelAdmin):
    pass

class GameLineupStatsAdmin(admin.ModelAdmin):
    pass

admin.site.register(Game, GameAdmin)
admin.site.register(Team, TeamAdmin)
admin.site.register(Lineup, LineupAdmin)
admin.site.register(Player, PlayerAdmin)
admin.site.register(GameLineupStats, GameLineupStatsAdmin) 
