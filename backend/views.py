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

import json, math
from backend.serializers import UserSerializer, LevelSerializer, PlayerSerializer, CreateUserSerializer, LoginUserSerializer



def checkRadius(lat,long,level):
    earth_r = 6371
    l_lat = level.location.lat
    l_long = level.location.long
    r = level.radius
    dlat = math.radians(l_lat-lat) #distange 
    dlong = math.radians(l_long-long) #distance

    a = math.sin(dlat/2)*math.sin(dlat/2) + math.cos(math.radians(lat))*math.cos(math.radians(l_lat))*math.sin(dlong/2)*math.sin(dlong/2)
    c = 2 * math.asin(math.sqrt(a))
    d = earth_r*c

    if(d<r):
        return True
    else:
        return False

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
        try:
            player = Player.objects.get(user=request.user)
            current_level = player.current_level
            if (current_level >= 0 ):
                next_level = current_level + 1
            level = Level.objects.get(level_no=next_level)
            serializer = LevelSerializer(level)
            return Response(serializer.data)
        except (Player.DoesNotExist or Level.DoesNotExist):
            return Response({"data": None})

class SubmitLevelAns(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        _ans = data.get("answer",None)
        _level = data.get("level_no",None)
        msg = {"success" : False}
        if _ans and _level:
            try:
                player = Player.objects.get(user=request.user)
                level = Level.objects.get(level_no=player.current_level+1)
            except (Player.DoesNotExist or Level.DoesNotExist):
                player,level = None,None
            if player and (_ans == level.ans ) and (player.current_level == level.level_no-1):
                player.map_qs = True
                level.map_bool = True
                msg = {"success" : True}

        return Response(msg)

class SubmitLocation(APIView):
    def post(self, request, *args, **kwargs):
        data = request.data
        _lat = data.get("lat",None)
        _long = data.get("long",None)
        _level = data.get("level_no",None)
        msg = {"success" : False}
        if _lat and _long:
            try:
                player = Player.objects.get(user=request.user)
                level = Level.objects.get(level_no=player.current_level+1)
            except (Player.DoesNotExist or Level.DoesNotExist):
                player,level = None,None
            if player.map_qs and level.map_bool:
                if checkRadius(_lat, _long, level):
                    player.current_level += 1
                    player.map_qs = False
                    level.map_bool = False
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