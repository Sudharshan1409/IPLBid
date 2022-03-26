from django.urls import path
import json
from . import views
app_name = 'bid'

urlpatterns = [
    path('games/', views.GamesView.as_view(), name='games'),
]
