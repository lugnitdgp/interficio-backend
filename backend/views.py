from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from backend.models import Player, Level, Location
from django.contrib.auth.models import User
from django.core import serializers as ds
from rest_framework import viewsets, generics
from rest_framework.response import Response
from rest_framework import authentication, permissions
from rest_framework.views import APIView

import json
from backend.serializers import UserSerializer, LevelSerializer, PlayerSerializer, CreateUserSerializer, LoginUserSerializer


#DRF viewset and serializers
class UserViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for listing or retrieving users.
    """
    def list(self, request):
        queryset = User.objects.all()
        serializer = UserSerializer(queryset, many=True)
        usernames = [{user.pk : user.username} for user in queryset]
        return Response(usernames)

    def retrieve(self, request, pk=None):
        queryset = User.objects.all()
        user = get_object_or_404(queryset, pk=pk)
        serializer = UserSerializer(user)
        return Response(serializer.data)

class RegistrationAPI(generics.GenericAPIView):
    serializer_class = CreateUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)
        })


class LoginAPI(generics.GenericAPIView):
    serializer_class = LoginUserSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)
        })

class PlayerDetail(APIView):
    """ A Player View """
    def get(self,request,pk=None):
        player = get_object_or_404(Player, pk=pk)
        serializer = PlayerSerializer(player)
        return Response(serializer.data)


class GetLevel(APIView):
    def get(self,request,format=None):
        user_id = request.user.pk
        player = Player.objects.get(user=request.user)
        current_level = player.current_level
        if (current_level >= 0 ):
            next_level = current_level + 1
        level = Level.objects.get(level_no=next_level)
        serializer = LevelSerializer(level)
        return Response(serializer.data)

class SubmitLevelAns(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        _ans = data.get("answer",None)
        _level = data.get("level_no",None)
        msg = {"success" : False}
        if ans and level_no:
            player = Player.objects.get(user=request.user)
            level = Level.objects.get(level_no=_level)
            if player and (_ans == level.ans ):
                msg = {"success" : True}
        return Response(msg)

def leaderboard(req):
    data = Player.objects.all().order_by('-score')
    data = json.loads(ds.serialize("json", data))
    api_data = []
    for i in data:
        api_data.append(i.get('fields'))

    data = json.dumps(api_data)
    data = '{"standings" : '+data+'}'
    return HttpResponse(data, content_type='application/json')