from django.contrib import admin

from basketball.forms import GameForm, TeamForm
from basketball.models import Game, Team

class GameAdmin(admin.ModelAdmin):
    form = GameForm

class TeamAdmin(admin.ModelAdmin):
    form = TeamForm

admin.site.register(Game, GameAdmin)
admin.site.register(Team, TeamAdmin)
