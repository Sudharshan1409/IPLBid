import datetime
import os

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.mail import send_mail
from django.core.paginator import Paginator
from django.shortcuts import redirect, render
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.generic import CreateView, View
from pytz import timezone

from bid.decorators import super_user_or_not
from bid.models import (
    ActiveYear,
    Dream11Matches,
    Dream11Scores,
    Game,
    Game_Result,
    UserProfile,
)
from iplBid.settings import ALL_TEAMS
from iplBid.settings import DREAM11_PLAYERS as players
from iplBid.settings import EMAIL_HOST_USER
from iplBid.settings import IPL_TEAMS as teams
from iplBid.settings import (
    MAXIMUM_BID_VALUE,
    MINIMUM_BID_VALUE,
    PLAYOFFS_MAXIMUM_BID_VALUE,
    PLAYOFFS_MINIMUM_BID_VALUE,
)

# Create your views here.


def remainder():
    users = UserProfile.objects.filter(year=int(os.environ["CURRENT_YEAR"]))
    today_date_start = datetime.datetime.now(timezone("Asia/Kolkata"))
    today_date_end = today_date_start + datetime.timedelta(hours=2)
    game = (
        Game.objects.filter(date__gt=today_date_start, date__lt=today_date_end)
        .order_by("date")
        .first()
    )
    if not game:
        print("No game found")
        return
    game_date = game.date.astimezone(timezone("Asia/Kolkata"))
    game_date = game_date - datetime.timedelta(minutes=1)
    for user in users:
        game_result = Game_Result.objects.filter(user=user, game=game)
        if not game_result:
            if not user.remainder:
                continue
            email = user.user.email
            print("email", email)
            send_mail(
                "Remainder for the upcoming match",
                f"""
                Hi {user.user.first_name},
                You have not placed a bid for the upcoming match between {game.team1} and {game.team2}.
                Please place a bid before {game_date.hour}:{game_date.minute}.
                Thank You""",
                EMAIL_HOST_USER,
                [email],
                fail_silently=False,
            )


@method_decorator(super_user_or_not, name="dispatch")
class AddPlayerView(CreateView):
    template_name = "bid/add_player.html"
    model = Dream11Scores
    fields = ["name"]
    success_url = "/dream11/add_player/"
    context_object_name = "form"


@method_decorator(super_user_or_not, name="dispatch")
class AddMatchView(View):
    template_name = "bid/add_match.html"

    def get(self, request):
        try:
            latestMatch = Dream11Matches.objects.latest("date")
            # get Games from the date of the latest match
            game = Game.objects.filter(date__gt=latestMatch.date).first()
        except Dream11Matches.DoesNotExist:
            latestMatch = None
            game = None
        return render(
            request,
            self.template_name,
            {"teams": teams, "players": players, "game": game},
        )

    def post(self, request):
        print(request.POST)
        if request.POST.get("cancelled") == "on":
            game = Game.objects.get(id=request.POST.get("gameId"))
            Dream11Matches.objects.create(game=game, isCancelled=True)
            return redirect(reverse("scores"))
        first = request.POST.get("first")
        second = request.POST.get("second")
        third = request.POST.get("third")
        fourth = request.POST.get("fourth")
        if request.POST.get("firstCheck") == "on":
            first = request.POST.get("firstText")
        if request.POST.get("secondCheck") == "on":
            second = request.POST.get("secondText")
        if request.POST.get("thirdCheck") == "on":
            third = request.POST.get("thirdText")
        if request.POST.get("fourthCheck") == "on":
            fourth = request.POST.get("fourthText")

        game = Game.objects.get(id=request.POST.get("gameId"))
        Dream11Matches.objects.create(
            game=game, first=first, second=second, third=third
        )
        return redirect(reverse("scores"))


@method_decorator(super_user_or_not, name="dispatch")
class ScoresView(View):
    template_name = "bid/scores.html"

    def get(self, request):
        scores = list(Dream11Scores.objects.all())
        scores.sort(key=lambda x: x.profit, reverse=True)
        # scores[0]['rgb'] = 'rgb(255, 215, 0)'
        # scores[1]['rgb'] = 'rgb(192, 192, 192)'
        # scores[2]['rgb'] = 'rgb(205, 127, 50)'
        matches = Dream11Matches.objects.all().order_by("-date")
        matches_paginator = Paginator(list(matches), 10)
        matches_games_page = matches_paginator.get_page(request.GET.get("page", 1))
        return render(
            request,
            self.template_name,
            {"scores": scores, "matches": matches_games_page},
        )


@method_decorator(super_user_or_not, name="dispatch")
class CreateGameView(View):
    template_name = "bid/create_game.html"

    def get(self, request):
        latestGameDate = Game.objects.latest("date").date
        latestGameDate = latestGameDate.astimezone(timezone("Asia/Kolkata"))
        print(latestGameDate.date(), latestGameDate.hour)
        if latestGameDate.hour == 19:
            latestGameDate = latestGameDate + datetime.timedelta(days=1)
            latestGameTime = "15:00:00"
        else:
            latestGameTime = "19:00:00"
        return render(
            request,
            self.template_name,
            {
                "teams": teams,
                "latestGameDate": latestGameDate.day,
                "latestGameMonth": latestGameDate.month,
                "latestGameTime": latestGameTime,
            },
        )

    def post(self, request):
        print(request.POST)
        if "isPlayOffs" in request.POST:
            isPlayOffs = True
        else:
            isPlayOffs = False
        date = f"{int(os.environ['CURRENT_YEAR'])}-{request.POST['month']}-{request.POST['date']}T{request.POST['time']}+05:30"
        Game.objects.create(
            date=date,
            team1=request.POST["team1"],
            team2=request.POST["team2"],
            isPlayOffs=isPlayOffs,
        )
        messages.success(request, "Game Created Successfully")
        if "add" in request.POST:
            return redirect(reverse("bid:create_game"))
        else:
            return redirect(reverse("bid:games") + "#upcoming")


@method_decorator(super_user_or_not, name="dispatch")
class UpdateGameWinnerView(View):
    template_name = "bid/update_game.html"

    def get(self, request):
        games = Game.objects.filter(completed=False).filter(
            date__lte=datetime.datetime.now(timezone("Asia/Kolkata"))
        )
        return render(request, self.template_name, {"games": games})

    def post(self, request):
        print(request.POST)
        game = Game.objects.get(id=request.POST["gameId"])
        if request.POST["team"] == "None":
            game.isCancelled = True
        game.winner = request.POST["team"]
        game.save()
        return redirect(reverse("bid:update_game_winner"))


class UserDetailView(LoginRequiredMixin, View):
    model = UserProfile
    template_name = "bid/user_detail.html"

    def get(self, request, *args, **kwargs):
        print(request.GET)
        status = request.GET.get("status")
        team = request.GET.get("team")
        if not status:
            status = "no"
        if not team:
            team = "no"

        current_year = str(request.user.active_year.year)
        user = UserProfile.objects.get(pk=kwargs["pk"])
        game_results = Game_Result.objects.filter(user=user, year=int(current_year))
        if status != "no":
            if status == "won":
                game_results = game_results.filter(won=True, completed=True)
            elif status == "lost":
                game_results = game_results.filter(
                    won=False, completed=True, cancelled=False
                )
            elif status == "cancelled":
                game_results = game_results.filter(cancelled=True)
            elif status == "not_completed":
                game_results = game_results.filter(completed=False)
            else:
                pass
        if team != "no":
            if team in ALL_TEAMS:
                game_results = game_results.filter(
                    game__team1=team
                ) | game_results.filter(game__team2=team)
            else:
                pass
        results_array = []
        for game_result in game_results:
            results_array.append(game_result)
        results_array.sort(key=lambda x: x.game.date, reverse=True)
        results_paginator = Paginator(list(results_array), 10)
        results_games_page = results_paginator.get_page(request.GET.get("page", 1))
        return render(
            request,
            self.template_name,
            {
                "results": results_games_page,
                "result_user": user,
                "teams": teams,
                "all_teams": ALL_TEAMS,
                "status": status,
                "team": team,
                "profile_pk": user.pk,
            },
        )


class ChangeActiveYearView(LoginRequiredMixin, View):
    model = ActiveYear

    def post(self, request):
        activeYear = ActiveYear.objects.get(user=request.user)
        activeYear.year = int(request.POST["year"])
        print("year", request.POST["year"])
        activeYear.save()
        print("path", request.POST["path"])
        if request.POST["path"] == "/bid/games/":
            return redirect(reverse("bid:games") + "#ongoing")
        if "/bid/user" in request.POST["path"]:
            return redirect(
                "/bid/user/"
                + str(
                    request.user.profiles.filter(year=int(activeYear.year)).first().id
                )
                + "?status=no&team=no"
            )
        return redirect(request.POST["path"])


class ChangeRemainderView(LoginRequiredMixin, View):
    model = UserProfile

    def post(self, request):
        userProfile = UserProfile.objects.filter(
            user=request.user.id, year=int(os.environ["CURRENT_YEAR"])
        ).first()
        remainder = request.POST.get("remainder")
        if remainder == "on":
            userProfile.remainder = True
            messages.success(
                request,
                "Remainder is enabled, you will receive a mail 1 hour before the match",
            )
        else:
            userProfile.remainder = False
            messages.success(request, "Remainder is disabled")
        userProfile.save()
        return redirect(request.POST["path"])


class GameDetailView(LoginRequiredMixin, View):
    model = Game
    template_name = "bid/game_detail.html"

    def get(self, request, *args, **kwargs):
        current_year = str(request.user.active_year.year)
        game = Game.objects.get(pk=kwargs["pk"])
        users = UserProfile.objects.filter(year=int(current_year))
        listObj = []
        for user in users:
            game_result = Game_Result.objects.filter(user=user, game=game)
            if game_result:
                print("game result: ", game_result[0].bid_amount)
                listObj.append(
                    {
                        "user": user,
                        "game_result": game_result[0],
                        "name": f"{user.user.first_name.upper()} {user.user.last_name.upper()}",
                        "amount": game_result[0].bid_amount,
                        "won": game_result[0].won,
                        "team": game_result[0].team,
                        "did_not_bid": game_result[0].did_not_bid,
                        "isCancelled": game.isCancelled,
                    }
                )
            else:
                listObj.append(
                    {
                        "user": user,
                        "game_result": None,
                        "name": f"{user.user.first_name.upper()} {user.user.last_name.upper()}",
                        "amount": None,
                        "won": None,
                        "team": "N/A",
                        "did_not_bid": True,
                        "isCancelled": game.isCancelled,
                    }
                )
        print(users)
        return render(
            request,
            self.template_name,
            {
                "listObj": listObj,
                "game": game,
                "min_bid": MINIMUM_BID_VALUE,
                "max_bid": MAXIMUM_BID_VALUE,
                "playoffs_min_bid": PLAYOFFS_MINIMUM_BID_VALUE,
                "playoffs_max_bid": PLAYOFFS_MAXIMUM_BID_VALUE,
            },
        )


class GamesView(LoginRequiredMixin, View):
    model = Game
    template_name = "bid/games.html"
    context_object_name = "games"

    def get(self, request):
        current_year = str(request.user.active_year.year)
        completed_games = []
        ongoing_games = []
        upcoming_games = []
        today_date = datetime.datetime.now(timezone("Asia/Kolkata"))
        profile = request.user.profiles.filter(year=int(current_year)).first()
        games = Game.objects.filter(year=int(current_year))
        for game in games:
            res = Game_Result.objects.filter(user=profile, game=game).first()
            if res:
                game.isBid = True
                game.bid_result = res
            else:
                game.isBid = False

            if (
                game.date.astimezone(timezone("Asia/Kolkata")).date()
                < today_date.date()
            ):
                completed_games.append(game)
            if (
                game.date.astimezone(timezone("Asia/Kolkata")).date()
                == today_date.date()
            ):
                ongoing_games.append(game)
            if (
                game.date.astimezone(timezone("Asia/Kolkata")).date()
                > today_date.date()
            ):
                upcoming_games.append(game)
        completed_games.sort(key=lambda x: x.date, reverse=True)
        completed_games_paginator = Paginator(list(completed_games), 10)
        upcoming_games_paginator = Paginator(list(upcoming_games), 10)
        completed_games_page = completed_games_paginator.get_page(
            request.GET.get("page", 1)
        )
        upcoming_games_page = upcoming_games_paginator.get_page(
            request.GET.get("page", 1)
        )
        ongoing_games.sort(key=lambda x: x.date, reverse=False)
        upcoming_games.sort(key=lambda x: x.date, reverse=False)
        return render(
            self.request,
            self.template_name,
            {
                "completed_games_page": completed_games_page,
                "upcoming_games_page": upcoming_games_page,
                "completed_games": completed_games,
                "ongoing_games": ongoing_games,
                "upcoming_games": upcoming_games,
                "date": datetime.datetime.now(),
                "min_bid": MINIMUM_BID_VALUE,
                "max_bid": MAXIMUM_BID_VALUE,
                "playoffs_min_bid": PLAYOFFS_MINIMUM_BID_VALUE,
                "playoffs_max_bid": PLAYOFFS_MAXIMUM_BID_VALUE,
            },
        )

    def post(self, request):
        current_year = str(request.user.active_year.year)
        print("user", request.user)
        print("bid", request.POST)
        if not request.user.profiles.filter(year=int(current_year)):
            messages.warning(
                request,
                "You are not registered for this year. Please contact the admin.",
            )
            return redirect(reverse("bid:games"))
        game = Game.objects.get(id=request.POST["gameId"])
        game_date = game.date.astimezone(timezone("Asia/Kolkata"))
        today_date = datetime.datetime.now(timezone("Asia/Kolkata"))
        if game.isPlayOffs:
            min_bid_amount = PLAYOFFS_MINIMUM_BID_VALUE
            max_bid_amount = PLAYOFFS_MAXIMUM_BID_VALUE
        else:
            min_bid_amount = MINIMUM_BID_VALUE
            max_bid_amount = MAXIMUM_BID_VALUE
        if (
            today_date < game_date
            and (game_date - today_date).days <= 1
            and int(request.POST["amount"]) >= min_bid_amount
            and int(request.POST["amount"]) <= max_bid_amount
        ):
            if request.POST["method"] == "create":
                game_results = Game_Result.objects.filter(
                    user=request.user.profiles.filter(year=int(current_year))[0],
                    game=game,
                )
                if not game_results:
                    game_result = Game_Result.objects.create(
                        user=request.user.profiles.filter(year=int(current_year))[0],
                        game=game,
                        bid_amount=request.POST["amount"],
                        team=request.POST["team"],
                    )
                    messages.success(request, "Bid Created Successfully")
                else:
                    messages.warning(request, "Bid Already Exist")
            elif request.POST["method"] == "update":
                game_result = Game_Result.objects.get(id=request.POST["pk"])
                print("before", game_result.team)
                game_result.bid_amount = request.POST["amount"]
                game_result.team = request.POST["team"]
                print("after", game_result.team)
                game_result.save()
                messages.success(request, "Bid Updated Successfully")
        else:
            if not (today_date < game_date and (game_date - today_date).days <= 1):
                messages.warning(request, "Bid Time Expired or not Started Yet")
            else:
                messages.warning(
                    request,
                    f"Bid Amount is not in Range of { min_bid_amount } to { max_bid_amount }",
                )
        if request.POST["method"] == "other_create":
            user = UserProfile.objects.get(id=request.POST["user_pk"])
            game_results = Game_Result.objects.filter(user=user, game=game)
            if not game_results:
                game_result = Game_Result.objects.create(
                    user=user,
                    game=game,
                    bid_amount=request.POST["amount"],
                    team=request.POST["team"],
                )
                messages.success(request, "Bid Created Successfully")
            else:
                messages.warning(request, "Bid Already Exist")
        elif request.POST["method"] == "other_update":
            user = UserProfile.objects.get(id=request.POST["user_pk"])
            game_results = Game_Result.objects.filter(user=user, game=game)
            game_result = game_results[0]
            game_result.bid_amount = request.POST["amount"]
            game_result.team = request.POST["team"]
            game_result.save()
            messages.success(request, "Bid Updated Successfully")
        else:
            pass

        return redirect(reverse("bid:games"))
