from rest_framework import serializers
from django.contrib.auth.models import User
from backend.models import Player, Level, Location

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email')

class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = ('level_no','title','ques')
