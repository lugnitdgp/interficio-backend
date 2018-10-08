from rest_framework import serializers
from django.contrib.auth.models import User
from backend.models import Player, Level, Location

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email')

class PlayerSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField('get_username')

    def get_username(self, obj):
        return obj.user.username

    class Meta:
        model = Player
        fields = ('username','name','email','score','rank','current_level')

class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = ('level_no','title','ques')
