from django.urls import path
import json
from . import views
app_name = 'bid'

urlpatterns = [
    path('games/', views.GamesView.as_view(), name='games'),
    path('game/<int:pk>/', views.GameDetailView.as_view(), name='game_detail'),
    path('user/<int:pk>/', views.UserDetailView.as_view(), name='user'),
]
