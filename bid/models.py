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
choices = [
    ('DC', 'DC'),
    ('PBKS', 'PBKS'),
    ('KKR', 'KKR'),
    ('LSG', 'LSG'),
    ('SRH', 'SRH'),
    ('RR', 'RR'),
    ('GT', 'GT'),
    ('CSK', 'CSK'),
    ('RCB', 'RCB'),
    ('MI', 'MI'),
]
class Game(models.Model):
    name = models.CharField(max_length=200, null=True, blank=True)
    date = models.DateTimeField()
    completed = models.BooleanField(default=False)
    winner = models.CharField(max_length=200, null=True, blank=True, choices=choices)
    team1 = models.CharField(max_length=200, choices=choices)
    team2 = models.CharField(max_length=200, choices=choices)

    def __str__(self):
        return f"{self.name}"
    
    def save(self, *args, **kwargs):
        if not self.name:
            self.name = f"{self.team1} vs {self.team2}"
        else:
            self.name = f"{self.name.split(' ')[0]} {self.team1} vs {self.team2}"
        super().save(*args, **kwargs)

class Game_Result(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name="Game_Results_profile")
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name="Game_Results")
    bid_amount = models.IntegerField()
    won = models.BooleanField(default=False)
    team = models.CharField(max_length=200, null=True, blank=True, choices=choices)
    completed = models.BooleanField(default=False)
    did_not_bid = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.game.name} Result"

    class Meta:
        unique_together = ('user', 'game',)

@receiver(post_save, sender=User)
def create_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user = instance)
        print('profile created')

@receiver(post_save, sender=Game)
def update_game(sender, instance, created, **kwargs):
    if not created and not instance.completed and instance.winner:
        users = UserProfile.objects.all()
        for user in users:
            game_result = Game_Result.objects.filter(user=user, game=instance)
            print(game_result)
            if game_result:
                if instance.winner == game_result[0].team:
                    game_result[0].won = True
                    game_result[0].completed = True
                    user.amount += game_result[0].bid_amount
                else:
                    game_result[0].won = False
                    game_result[0].completed = True
                    user.amount -= game_result[0].bid_amount
                game_result[0].save()
            else:
                user.amount -= 1000
                Game_Result.objects.create(user=user, game=instance, bid_amount=0, won=False, completed=True, did_not_bid=True)

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

