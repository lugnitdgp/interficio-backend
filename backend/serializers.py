from rest_framework import serializers
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from backend.models import Player, Level, Location


class CreateUserSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(write_only=True)
    name = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ('username', 'password', 'email', 'name')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(validated_data['username'],
                                        None,
                                        validated_data['password'])

        player = Player.objects.create(user=user,
                                       name=validated_data['name'],
                                       email=validated_data['email'])
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


class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField()
    new_password = serializers.CharField(write_only=True)

    def validate(self, instance, data):
        print("IM VADILATING")
        user = instance
        if user.check_password(data['old_passowrd']):
            return data
        else:
            raise serializers.ValidationError("Old password validation error.")

    def update(self, instance, validated_data):
        instance.set_password(validated_data['new_password'])
        instance.save()
        return instance


class PlayerSerializer(serializers.ModelSerializer):
    user_name = serializers.SerializerMethodField('get_username')

    def get_username(self, obj):
        return obj.user.username

    class Meta:
        model = Player
        fields = ('user_name', 'name', 'email', 'coins', 'rank', 'current_level')


class LevelSerializer(serializers.ModelSerializer):
    pause_bool = serializers.SerializerMethodField('check_pause')
    # map_hint = serializers.SerializerMethodField('_hint')

    def check_pause(self, obj):
        if obj.paused == True:
            obj.ques = "PAUSE"
            obj.title = None
            # obj.map_bool = None
            return True

        elif obj.paused == False:
            return False

    # Hack for giving hints on Maps
    # def _hint(self, obj):
    #     if obj.map_bool == True:
    #         obj.ques = obj.map_hint
    #         return True
    #     else:
    #         return False

    class Meta:
        model = Level
        fields = ('pause_bool', 'level_no', 'title', 'ques')
