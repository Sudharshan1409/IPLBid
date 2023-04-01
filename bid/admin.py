from django.contrib import admin
from .models import UserProfile, Game, Game_Result, ActiveYear
# Register your models here.

class GameAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'winner', 'completed', 'team1', 'team2', 'year')

class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'amount', 'win_percentage', 'year')

class Game_ResultAdmin(admin.ModelAdmin):
    list_display = ('user', 'game', 'bid_amount', 'won', 'completed', 'team', 'did_not_bid', 'year')

class ActiveYearAdmin(admin.ModelAdmin):
    list_display = ('user', 'year')

admin.site.register(UserProfile, UserProfileAdmin)
admin.site.register(Game, GameAdmin)
admin.site.register(Game_Result, Game_ResultAdmin)
admin.site.register(ActiveYear, ActiveYearAdmin)
