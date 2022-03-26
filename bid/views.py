from django.shortcuts import render, redirect
from django.contrib.auth.mixins import LoginRequiredMixin
from bid.models import Game, Game_Result, UserProfile
from django.views.generic import View
import datetime
from pytz import timezone
from django.urls import reverse
# Create your views here.

class GameDetailView(LoginRequiredMixin, View):
    model = Game
    template_name = 'bid/game_detail.html'
    def get(self, request, *args, **kwargs):
        game = Game.objects.get(pk=kwargs['pk'])
        users = UserProfile.objects.all()
        listObj = []
        for user in users:
            game_result = Game_Result.objects.filter(user=user, game=game)
            print(game_result)
            if game_result:
                listObj.append({
                    'user': user,
                    'game_result': game_result[0],
                    'name': f"{user.user.first_name.capitalize()} {user.user.last_name.capitalize()}",
                    'amount': game_result[0].bid_amount,
                    'won': game_result[0].won,
                    'team': game_result[0].team,
                })
            else:
               listObj.append({
                    'user': user,
                    'game_result': None,
                    'name': f"{user.user.first_name.capitalize()} {user.user.last_name.capitalize()}",
                    'amount': 'N/A',
                    'won': None,
                    'team': 'N/A',
               })
        print(users)
        return render(request, self.template_name, {
            'listObj': listObj,
            'game': game
        })
class GamesView(LoginRequiredMixin, View):
    model = Game
    template_name = 'bid/games.html'
    context_object_name = 'games'
    def get(self, request):
        completed_games = []
        ongoing_games = []
        upcoming_games = []
        today_date = datetime.datetime.now(timezone('Asia/Kolkata'))
        games = Game.objects.all()
        for game in games:
            found = False
            res = None
            for result in game.Game_Results.all():
                if result.user.user == request.user:
                    found = True
                    res = result
                    break
            if found:
                game.isBid = True
                game.bid_result = res
            else:
                game.isBid = False
            if game.date.date() < today_date.date():
                completed_games.append(game)
            if game.date.date() == today_date.date():
                ongoing_games.append(game)
            if game.date.date() > today_date.date():
                upcoming_games.append(game)
        completed_games.sort(key=lambda x: x.date, reverse=True)
        ongoing_games.sort(key=lambda x: x.date, reverse=False)
        upcoming_games.sort(key=lambda x: x.date, reverse=False)
        return render(self.request, self.template_name, {'completed_games': completed_games, "ongoing_games": ongoing_games, "upcoming_games": upcoming_games, "date": datetime.datetime.now()})

    def post(self, request):
        print(request.POST)
        game = Game.objects.get(id=request.POST['gameId'])
        today_date = datetime.datetime.now(timezone('Asia/Kolkata')) + datetime.timedelta(minutes=5)
        if today_date < game.date and (game.date - today_date).days <=1 and int(request.POST['amount']) >= 100 and int(request.POST['amount']) <= 3000:
            if request.POST['method'] == 'create':
                game_result = Game_Result.objects.create(user=request.user.userprofile, game=game, bid_amount=request.POST['amount'], team=request.POST['team'])
            else:
                game_result = Game_Result.objects.get(id=request.POST['pk'])
                print('before', game_result.team)
                game_result.bid_amount = request.POST['amount']
                game_result.team = request.POST['team']
                print('after', game_result.team)
                game_result.save()
        return redirect(reverse('bid:games'))