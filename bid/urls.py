from django.urls import path
import json
from . import views
app_name = 'bid'

urlpatterns = [
    path('games/', views.GamesView.as_view(), name='games'),
    path('game/<int:pk>/', views.GameDetailView.as_view(), name='game_detail'),
    path('user/<int:pk>/', views.UserDetailView.as_view(), name='user'),
    path('game/create/', views.CreateGameView.as_view(), name='create_game'),
    path('game/update/', views.UpdateGameView.as_view(), name='update_game'),
    path('dream11/add_match/', views.AddMatchView.as_view(), name='add_match'),
    path('dream11/scores/', views.ScoresView.as_view(), name='scores'),
    path('dream11/matches/', views.MatchesView.as_view(), name='matches'),
    path('dream11/add_player/', views.AddPlayerView.as_view(), name='add_player'),
    path('change_active_year/', views.ChangeActiveYearView.as_view(), name='change_active_year'),
]
