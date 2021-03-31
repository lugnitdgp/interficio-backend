from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from backend.models import Player, Level, Location, Clue, FinalQuestion
from django.contrib.auth.models import User
from django.core import serializers as ds
from rest_framework import viewsets, generics
from rest_framework.response import Response
from rest_framework import authentication, permissions
from rest_framework.views import APIView
from knox.models import AuthToken

import json
import math
import datetime
from decimal import Decimal
from backend.serializers import UserSerializer, LevelSerializer, PlayerSerializer, CreateUserSerializer, LoginUserSerializer, ChangePasswordSerializer


def checkRadius(lat, long, level):
    earth_r = 6371
    l_lat = level.location.lat
    l_long = level.location.long
    r = level.radius
    dlat = math.radians(l_lat-lat)  # distange
    dlong = math.radians(l_long-long)  # distance

    a = math.sin(dlat/2)*math.sin(dlat/2) + math.cos(math.radians(lat)) * \
        math.cos(math.radians(l_lat))*math.sin(dlong/2)*math.sin(dlong/2)
    c = 2 * math.asin(math.sqrt(a))
    d = earth_r*c
    if(d < r):
        return True
    else:
        return False


def updateRank():
    data = Player.objects.all().order_by('-score', 'last_solve')
    for i, player in enumerate(data):
        player.rank = i+1
        player.save()

# DRF viewset and serializers


class UserViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for listing or retrieving users.
    """

    def list(self, request):
        queryset = User.objects.all()
        serializer = UserSerializer(queryset, many=True)
        usernames = [{user.pk: user.username} for user in queryset]
        return Response(usernames)

    def retrieve(self, request, pk=None):
        queryset = User.objects.all()
        user = get_object_or_404(queryset, pk=pk)
        serializer = UserSerializer(user)
        return Response(serializer.data)


class RegistrationAPI(generics.GenericAPIView):
    serializer_class = CreateUserSerializer
    permission_classes = [permissions.AllowAny, ]

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
    permission_classes = [permissions.AllowAny, ]

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)
        })


class ChangePasswordAPI(generics.GenericAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated, ]

    def post(self, request, *args, **kwargs):
        user_instance = request.user
        serializer = self.get_serializer(instance=user_instance, data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.update(instance=user_instance, validated_data=serializer.validated_data)
        return Response({
            "user": UserSerializer(user, context=self.get_serializer_context()).data,
            "token": AuthToken.objects.create(user)
        })


class PlayerDetail(APIView):
    """ A Player View """
    permission_classes = [permissions.IsAuthenticated, ]

    def get(self, request, format=None):
        player = get_object_or_404(Player, user=request.user)
        serializer = PlayerSerializer(player)
        return Response(serializer.data)


class GetLevel(APIView):

    permission_classes = [permissions.IsAuthenticated, ]

    def get(self, request, format=None):
        user_id = request.user.pk
        try:
            player = Player.objects.get(user=request.user)
            current_level = player.current_level
            if (current_level >= 0):
                next_level = current_level + 1
            level = Level.objects.get(level_no=next_level)
            # # HackFor map_bool fix(now map_bool will reset to player)
            # level.map_bool = player.map_qs
            level.save()
            serializer = LevelSerializer(level)
            return Response(serializer.data)
        except Player.DoesNotExist:
            return Response({"data": None})
        except Level.DoesNotExist:
            if player.current_level == len(Level.objects.all()):
                return Response({"level": "ALLDONE"})
            return Response({"data": None})

class GetLevelClues(APIView):
    permission_classes = [permissions.IsAuthenticated, ]
    
    def get(self, request, format=None):
        try:
            level_no = request.query_params.get("level_no", None)
            if not level_no:
                return Response({"data": None, "msg": "Level not provided"})
            level_no = int(level_no)
            
            player = Player.objects.get(user=request.user)
            current_level = player.current_level
            if (current_level+1 < level_no):
                return Response({"data": None, "msg": "Level not unlocked"})

            level = Level.objects.get(level_no=level_no)
            clues = Clue.objects.filter(level=level) # get clues for the level
            rclues = [] # response clues
            for c in clues:
                if c in player.unlocked_clues.all():
                    if not c.image:
                        rclues.append([c.clue_no, c.title, c.text, "U", None]) # L or U is state Locked or Unlocked
                    else:
                        rclues.append([c.clue_no, c.title, c.text, "U", c.image.url]) # L or U is state Locked or Unlocked
                else:
                    if not c.image:
                        rclues.append([c.clue_no, c.title, None, "L", None]) # L or U is state Locked or Unlocked
                    else:
                        rclues.append([c.clue_no, c.title, None, "L", c.image.url]) # L or U is state Locked or Unlocked
            return Response({"data" : rclues})
        
        except ValueError:
            return Response({"data": None, "msg": "Level must be an integer"})
        except Player.DoesNotExist:
            return Response({"data": None, "msg": "Player does not exist"})
        except Level.DoesNotExist:
            if player.current_level == len(Level.objects.all()):
                return Response({"level": "ALLDONE"})
            return Response({"data": None})


class GetClues(APIView):
    """Get all clues upto the unlocked level"""

    permission_classes = [permissions.IsAuthenticated, ]

    def get(self, request, format=None):
        try:
            player = Player.objects.get(user=request.user)
            current_level = player.current_level
           
            rclues = []  # response clues
            for l_no in range(0,current_level+2):
                lvl = Level.objects.filter(level_no=l_no).first()
                if lvl:
                    clu = Clue.objects.filter(level=lvl)
                    for c in clu:
                        if c in player.unlocked_clues.all():
                            if not c.image:
                                rclues.append([c.clue_no, c.title, c.text, "U", None])  # L or U is state Locked or Unlocked
                            else: 
                                rclues.append([c.clue_no, c.title, c.text, "U", c.image.url])  # L or U is state Locked or Unlocked
                        else:
                            if not c.image:
                                rclues.append([c.clue_no, c.title, None, "L", None])  # L or U is state Locked or Unlocked
                            else: 
                                rclues.append([c.clue_no, c.title, None, "L", c.image.url])  # L or U is state Locked or Unlocked
            return Response({"data": rclues})

        except ValueError:
            return Response({"data": None, "msg": "Level must be an integer"})
        except Player.DoesNotExist:
            return Response({"data": None, "msg": "Player does not exist"})
        except Level.DoesNotExist:
            if player.current_level == len(Level.objects.all()):
                return Response({"level": "ALLDONE"})
            return Response({"data": None})


class UnlockClue(APIView):
    permission_classes = [permissions.IsAuthenticated, ]

    def get(self, request, format=None):
        try:
            level_no = request.query_params.get("level_no", None)
            clue_no = request.query_params.get("clue_no", None)
            if not (level_no and clue_no):
                return Response({"data": None, "msg": "Level or Clue not provided"})
            
            level_no = int(level_no)
            clue_no = int(clue_no)

            player = Player.objects.get(user=request.user)
            current_level = player.current_level
            if (current_level+1 < level_no):
                return Response({"data": None, "msg": "Level not unlocked"})

            level = Level.objects.get(level_no=level_no)
            clue = Clue.objects.filter(level=level, clue_no=clue_no).first()  # get clues for the level
            if clue:
                player.unlocked_clues.add(clue)
                player.coins -= clue.unlock_price
                player.save()
                return Response({"data": "True"})
            else:
                return Response({"data": None, "msg": "Requested Clue dosen't exist for this Level"})

        except ValueError:
            return Response({"data": None, "msg": "Level and Clue must be an integer"})
        except Player.DoesNotExist:
            return Response({"data": None})
        except Level.DoesNotExist:
            if player.current_level == len(Level.objects.all()):
                return Response({"level": "ALLDONE"})
            return Response({"data": None})


class SubmitLevelAns(APIView):
    permission_classes = [permissions.IsAuthenticated, ]

    def post(self, request, *args, **kwargs):
        data = request.data
        _ans = data.get("answer", None)
        _level = data.get("level_no", None)
        msg = {"success": False}
        if _ans and _level:
            try:
                player = Player.objects.get(user=request.user)
                level = Level.objects.get(level_no=player.current_level+1)
            except (Player.DoesNotExist, Level.DoesNotExist):
                player, level = None, None
            if player and (_ans == level.ans) and (player.current_level == level.level_no-1):
                player.map_qs = True
                level.save()
                player.save()
                msg = {"success": True}

        return Response(msg)


class SubmitLocation(APIView):
    permission_classes = [permissions.IsAuthenticated, ]

    def post(self, request, *args, **kwargs):
        data = request.data
        try:
            _lat = Decimal(data.get("lat", None))
            _long = Decimal(data.get("long", None))
            _level = data.get("level_no", None)
        except Exception as e:
            print(e)
            _lat, _long = None, None

        msg = {"success": False}
        if _lat and _long:
            try:
                player = Player.objects.get(user=request.user)
                level = Level.objects.get(level_no=player.current_level+1)
            except (Player.DoesNotExist, Level.DoesNotExist):
                player, level = None, None
            # if player.map_qs:
            if checkRadius(_lat, _long, level):
                player.current_level += 1
                # player.map_qs = False
                # player.score += level.points
                player.last_solve = datetime.datetime.now()
                level.save()
                player.save()
                # updateRank()
                msg = {"success": True}
        return Response(msg)

class FinalText(APIView):
    permission_classes = [permissions.IsAuthenticated, ]

    def get(self, request, format=None):
        player = Player.objects.filter(user=request.user).first()
        ftext = FinalQuestion.objects.all().first()
        if player and ftext:
            return Response({"data": ftext.text})
        else:
            return Response({"data": None})

    def post(self, request, *args, **kwargs):
        data = request.data
        ans = data.get("ans", None)
        msg = {"success": False}
        if ans:
            player = Player.objects.get(user=request.user)
            if (player.current_level == len(Level.objects.all())) and (player.final_ans == ""):
                player.final_ans = ans
                player.save()
                return Response({"success": True})
        return Response(msg)


def leaderboard(req):
    data = Player.objects.all().order_by('-current_level', 'last_solve')
    data = PlayerSerializer(data)
    data = json.loads(ds.serialize("json", data))
    api_data = []
    for i in data:
        api_data.append(i.get('fields'))

    data = json.dumps(api_data)
    return HttpResponse(data, content_type='application/json')
