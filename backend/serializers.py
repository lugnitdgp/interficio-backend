from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from backend.models import Player, Level, Location

class CreateUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)
    name = serializers.CharField(write_only=True)
    class Meta:
        model = User
        fields = ('username', 'password','email','name')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(validated_data['username'],
                                        None,
                                        validated_data['password'])

        player = Player.objects.create(user = user,
                                        name = validated_data['name'],
                                        email = validated_data['email'])
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
        fields = ('username',)

class PlayerSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField('get_username')

    def get_username(self, obj):
        return obj.user.username

    class Meta:
        model = Player
        fields = ('user_name','name','email','score','rank','current_level')

    # def create(self, validated_data):
    #     user = Player.objects.create_player(validated_data['username'],
    #                                     None,
    #                                     validated_data['password'])
    #     return user

class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = ('level_no','title','ques','map_bool')
