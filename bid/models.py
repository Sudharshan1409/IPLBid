from django.db import models
from django.contrib.auth.models import User
from django.dispatch import receiver
from django.db.models.signals import post_save

# Create your models here.

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    amount = models.IntegerField(default=10000)

    def __str__(self):
        return f"{self.user.username.capitalize()} Profile"

class Game(models.Model):
    name = models.CharField(max_length=200)
    date = models.DateTimeField()
    completed = models.BooleanField(default=False)
    winner = models.CharField(max_length=200, null=True, blank=True)
    team1 = models.CharField(max_length=200)
    team2 = models.CharField(max_length=200)
    def __str__(self):
        return f"{self.name}"

class Game_Result(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="Game_Results_profile")
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="Game_Results")
    bid_amount = models.IntegerField()
    won = models.BooleanField(default=False)
    team = models.CharField(max_length=200, null=True, blank=True)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.game.name} Result"

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user = instance)
        print('profile created')

@receiver(post_save, sender=Game)
def update_game(sender, instance, created, **kwargs):
    if not created and not instance.completed and instance.winner:
        for result in instance.Game_Results.all():
            print(result.user.user)
            user = UserProfile.objects.get(id=result.user.pk)
            print(user)
            if instance.winner == result.team:
                result.won = True
                result.completed = True
                user.amount += result.bid_amount
            else:
                result.won = False
                result.completed = True
                user.amount -= result.bid_amount
            result.save()
            user.save()
        instance.completed = True
        instance.save()
@receiver(post_save,sender=User)
def update_profile(sender,instance,created, **kwargs):
    if not created:
        instance.userprofile.save()
        print('profile updated')
    


    def __str__(self):
        return f"{self.user.username.capitalize()} Profile"

