from django.urls import path, re_path

from basketball import views

basketball_urls = [
    re_path('294be434-0c6c-4118-a286-d4a3dfd3032e/?$', views.standings),
    re_path('294be434-0c6c-4118-a286-d4a3dfd3032e/(?P<year>\d+)/?$', views.standings),
    re_path('294be434-0c6c-4118-a286-d4a3dfd3032e/team/(?P<year>\d+)/(?P<short_name>\w+)/?$', views.team_show),
    re_path('294be434-0c6c-4118-a286-d4a3dfd3032e/game/(?P<game>\d+)/?$', views.game_show),
]

