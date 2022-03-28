from django.contrib import admin
from .models import UserProfile, Game, Game_Result
# Register your models here.

class GameAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'winner', 'completed', 'team1', 'team2')

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'amount')

class Game_ResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'game', 'bid_amount', 'won', 'completed', 'team', 'did_not_bid')

admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Game, GameAdmin)
admin.site.register(Game_Result, Game_ResultAdmin)
