import os

from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver

from iplBid.settings import CURRENT_YEAR as current_year
from iplBid.settings import DREAM11_PLAYERS as players
from iplBid.settings import IPL_TEAMS as choices
from iplBid.settings import PRICE_VALUES as prices

# Create your models here.


class UserProfile(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="profiles")
    amount = models.IntegerField(default=10000)
    year = models.IntegerField(default=int(os.environ["CURRENT_YEAR"]))
    remainder = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username.capitalize()} {self.year} Profile"

    @property
    def win_percentage(self):
        game_results = self.results_user.filter(year=int(os.environ["CURRENT_YEAR"]))
        amount = 0
        total = 0
        for result in game_results:
            if result.completed:
                if result.bid_amount > 0:
                    if result.won:
                        amount += result.bid_amount
                    if not result.cancelled:
                        total += result.bid_amount
                else:
                    total += 1000
        if total == 0:
            return 0
        return round((amount / total) * 100, 2)

    @property
    def stats(self):
        game_results = self.results_user.filter(year=int(os.environ["CURRENT_YEAR"]))
        wins = 0
        lost = 0
        for result in game_results:
            if result.completed:
                if result.won:
                    wins += 1
                else:
                    lost += 1
        return (wins, lost)

    @property
    def chart(self):
        game_results = list(
            self.results_user.filter(year=int(self.user.active_year.year))
        )
        game_results.sort(key=lambda x: x.game.date, reverse=False)
        games = [
            "",
        ]
        amounts = [
            10000,
        ]
        for result in game_results:
            if result.completed:
                games.append(result.game.name)
                if result.won:
                    amounts.append(amounts[-1] + result.bid_amount)
                else:
                    amounts.append(amounts[-1] - result.bid_amount)
        return (games, amounts)

    class Meta:
        unique_together = (
            "user",
            "year",
        )
        indexes = [
            models.Index(
                fields=[
                    "year",
                ]
            )
        ]


class Game(models.Model):
    name = models.CharField(max_length=200, null=True, blank=True)
    date = models.DateTimeField()
    completed = models.BooleanField(default=False)
    winner = models.CharField(max_length=200, null=True, blank=True, choices=choices)
    team1 = models.CharField(max_length=200, choices=choices)
    team2 = models.CharField(max_length=200, choices=choices)
    year = models.IntegerField(default=int(os.environ["CURRENT_YEAR"]))
    isPlayOffs = models.BooleanField(default=False)
    isCancelled = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} {self.year}"

    def save(self, *args, **kwargs):
        self.name = f"{self.team1} vs {self.team2}"
        super().save(*args, **kwargs)

    class Meta:
        indexes = [
            models.Index(
                fields=[
                    "year",
                ]
            ),
            models.Index(
                fields=[
                    "completed",
                ]
            ),
            models.Index(
                fields=[
                    "date",
                ]
            ),
        ]


class ActiveYear(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="active_year"
    )
    year = models.IntegerField(default=int(os.environ["CURRENT_YEAR"]))


class Dream11Matches(models.Model):
    game = models.OneToOneField(
        Game, on_delete=models.CASCADE, related_name="match", null=True
    )
    first = models.CharField(max_length=400, null=True)
    second = models.CharField(max_length=400, null=True, blank=True)
    third = models.CharField(max_length=400, null=True, blank=True)
    fourth = models.CharField(max_length=400, null=True, blank=True)
    date = models.DateTimeField(null=True)
    isCancelled = models.BooleanField(default=False)

    def __str__(self):
        return self.game.name

    def save(self, *args, **kwargs):
        if not self.game.year == current_year:
            raise Exception("Game year does not match current year")
        self.date = self.game.date
        super().save(*args, **kwargs)

    class Meta:
        indexes = [
            models.Index(
                fields=[
                    "date",
                ]
            ),
        ]


class Dream11Scores(models.Model):
    name = models.CharField(max_length=200, choices=players, unique=True)
    score = models.FloatField(default=0)
    matchesPlayed = models.IntegerField(default=0)
    cancelledMatches = models.IntegerField(default=0)

    def addScore(self, score):
        self.score += score
        self.save()

    @property
    def profit(self):
        return self.score - self.amount_used

    @property
    def amount_used(self):
        return (self.matchesPlayed - self.cancelledMatches) * 10

    @property
    def percentage(self):
        if self.matchesPlayed == 0:
            return 0
        return round(
            (self.score / ((self.matchesPlayed - self.cancelledMatches) * 40)) * 100, 2
        )


class Game_Result(models.Model):
    user = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="results_user"
    )
    game = models.ForeignKey(
        Game, on_delete=models.CASCADE, related_name="results_game"
    )
    bid_amount = models.IntegerField()
    won = models.BooleanField(default=False)
    cancelled = models.BooleanField(default=False)
    team = models.CharField(max_length=200, null=True, blank=True, choices=choices)
    completed = models.BooleanField(default=False)
    did_not_bid = models.BooleanField(default=False)
    year = models.IntegerField(default=int(os.environ["CURRENT_YEAR"]))

    def __str__(self):
        return f"{self.game.name} Result"

    class Meta:
        unique_together = (
            "user",
            "game",
        )
        indexes = [
            models.Index(
                fields=[
                    "year",
                ]
            ),
            models.Index(
                fields=[
                    "completed",
                ]
            ),
            models.Index(fields=["user", "game"]),
        ]


@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)
        ActiveYear.objects.create(user=instance)
        print("profile created")


@receiver(post_save, sender=Dream11Matches)
def create_match(sender, instance, created, **kwargs):
    if created:
        if not instance.isCancelled:
            if "&" in instance.first or "&" in instance.second or "&" in instance.third:
                if len(instance.first.split("&")) == 2:
                    Dream11Scores.objects.filter(name=instance.first.split("&")[0])[
                        0
                    ].addScore((prices[1] + prices[2]) / 2)
                    Dream11Scores.objects.filter(name=instance.first.split("&")[1])[
                        0
                    ].addScore((prices[1] + prices[2]) / 2)
                    Dream11Scores.objects.filter(name=instance.third)[0].addScore(
                        prices[3]
                    )
                    # Dream11Scores.objects.filter(name=instance.fourth)[0].addScore(prices[4])
                    instance.second = None
                elif len(instance.second.split("&")) == 2:
                    Dream11Scores.objects.filter(name=instance.second.split("&")[0])[
                        0
                    ].addScore((prices[2] + prices[3]) / 2)
                    Dream11Scores.objects.filter(name=instance.second.split("&")[1])[
                        0
                    ].addScore((prices[2] + prices[3]) / 2)
                    Dream11Scores.objects.filter(name=instance.first)[0].addScore(
                        prices[1]
                    )
                    # Dream11Scores.objects.filter(name=instance.fourth)[0].addScore(prices[4])
                    instance.third = None
                elif len(instance.third.split("&")) == 2:
                    Dream11Scores.objects.filter(name=instance.third.split("&")[0])[
                        0
                    ].addScore((prices[3] + prices[4]) / 2)
                    Dream11Scores.objects.filter(name=instance.third.split("&")[1])[
                        0
                    ].addScore((prices[3] + prices[4]) / 2)
                    Dream11Scores.objects.filter(name=instance.first)[0].addScore(
                        prices[1]
                    )
                    Dream11Scores.objects.filter(name=instance.second)[0].addScore(
                        prices[2]
                    )
                    instance.fourth = None

                # elif len(instance.fourth.split('&')) == 2:
                #     Dream11Scores.objects.filter(name=instance.third.split('&')[0])[0].addScore(prices[4]/2)
                #     Dream11Scores.objects.filter(name=instance.third.split('&')[1])[0].addScore(prices[4]/2)
                #     Dream11Scores.objects.filter(name=instance.first)[0].addScore(prices[1])
                #     Dream11Scores.objects.filter(name=instance.second)[0].addScore(prices[2])
                #     Dream11Scores.objects.filter(name=instance.third)[0].addScore(prices[3])
            else:
                Dream11Scores.objects.filter(name=instance.first)[0].addScore(prices[1])
                Dream11Scores.objects.filter(name=instance.second)[0].addScore(
                    prices[2]
                )
                Dream11Scores.objects.filter(name=instance.third)[0].addScore(prices[3])
            for score in Dream11Scores.objects.all():
                score.matchesPlayed = score.matchesPlayed + 1
                score.save()
                # Dream11Scores.objects.filter(name=instance.fourth)[0].addScore(prices[4])
            instance.save()
        else:
            for score in Dream11Scores.objects.all():
                score.matchesPlayed = score.matchesPlayed + 1
                score.cancelledMatches = score.cancelledMatches + 1
                score.save()
            instance.save()


@receiver(post_save, sender=Game)
def update_game(sender, instance, created, **kwargs):
    if not created and not instance.completed and instance.winner:
        users = UserProfile.objects.filter(year=int(os.environ["CURRENT_YEAR"]))
        for user in users:
            game_result = Game_Result.objects.filter(user=user, game=instance)
            print(game_result)
            if game_result:
                if not instance.isCancelled:
                    if instance.winner == game_result[0].team:
                        game_result[0].won = True
                        game_result[0].completed = True
                        user.amount += game_result[0].bid_amount
                    else:
                        game_result[0].won = False
                        game_result[0].completed = True
                        user.amount -= game_result[0].bid_amount
                else:
                    game_result[0].cancelled = True
                    game_result[0].completed = True
                game_result[0].save()
            else:
                if not instance.isPlayOffs:
                    user.amount -= 1000
                    if not instance.isCancelled:
                        Game_Result.objects.create(
                            user=user,
                            game=instance,
                            bid_amount=1000,
                            won=False,
                            completed=True,
                            did_not_bid=True,
                        )
                    else:
                        Game_Result.objects.create(
                            user=user,
                            game=instance,
                            bid_amount=1000,
                            won=False,
                            completed=True,
                            did_not_bid=True,
                            cancelled=True,
                        )
                else:
                    user.amount -= 2500
                    if not instance.isCancelled:
                        Game_Result.objects.create(
                            user=user,
                            game=instance,
                            bid_amount=2500,
                            won=False,
                            completed=True,
                            did_not_bid=True,
                        )
                    else:
                        Game_Result.objects.create(
                            user=user,
                            game=instance,
                            bid_amount=2500,
                            won=False,
                            completed=True,
                            did_not_bid=True,
                            cancelled=True,
                        )
            user.save()
        instance.completed = True
        instance.save()
