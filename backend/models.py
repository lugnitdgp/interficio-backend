from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name  = models.CharField(max_length=255)
    email = models.EmailField(null=True, blank=True)
    score = models.IntegerField(default=0)

    ##For internal user must not be on API
    rank = models.IntegerField(default=0)
    current_level = models.IntegerField(default=0)
    map_qs = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username

class Location(models.Model):
    name = models.CharField(max_length=255)
    lat = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    long = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    def __str__(self):
        return self.name

class Level(models.Model):
    level_no = models.PositiveSmallIntegerField(unique=True)
    title = models.CharField(max_length=255)
    ques = models.TextField()
    ans = models.CharField(max_length=255)
    points = models.IntegerField(default=0)
    map_bool = models.BooleanField(default=False)
    map_hint = models.TextField(null=True, blank=True)
    location = models.ForeignKey(Location, on_delete=models.CASCADE, blank=True, null=True)
    radius = models.DecimalField(max_digits=9,decimal_places=6,help_text="Put radius in KMs", null=True, blank=True)
    paused = models.BooleanField(default=False)

    def __str__(self):
        return str(self.level_no)
