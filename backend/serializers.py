from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from backend.models import Player, Level, Location

class CreateUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email', 'password')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(validated_data['username'],
                                        validated_data['email'],
                                        validated_data['password'])
        return user

class LoginUserSerializer(serializers.Serializer):
    username = serializers.CharField()
    password = serializers.CharField()

    def validate(self, data):
        user = authenticate(**data)
        if user and user.is_active:
            return user
        raise serializers.ValidationError("Unable to log in with provided credentials.")

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('username', 'email')

class PlayerSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField('get_username')

    def get_username(self, obj):
        return obj.user.username

    class Meta:
        model = Player
        fields = ('user_name','name','email','score','rank','current_level')

class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = ('level_no','title','ques','map_bool')
