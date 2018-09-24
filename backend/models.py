from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name  = models.CharField(max_length=255)
    email = models.EmailField(null=True, blank=True)
    score = models.IntegerField(default=0)

    def __str__(self):
        return self.user.username


