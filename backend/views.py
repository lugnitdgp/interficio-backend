from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from backend.models import Player, Level, Location
from django.contrib.auth.models import User
from django.core import serializers as ds
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework import authentication, permissions
from rest_framework.views import APIView

import json

from backend.serializers import UserSerializer, LevelSerializer, PlayerSerializer
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

class PlayerDetail(APIView):
    """ A Player View """
    def get(self,request,pk=None):
        player = get_object_or_404(Player, pk=pk)
        serializer = PlayerSerializer(player)
        return Response(serializer.data)


        


class LevelViewSet(viewsets.ViewSet):
    queryset = Level.objects.all()


def leaderboard(req):
    data = Player.objects.all().order_by('-score')
    data = json.loads(ds.serialize("json", data))
    api_data = []
    for i in data:
        api_data.append(i.get('fields'))

    data = json.dumps(api_data)
    data = '{"standings" : '+data+'}'
    return HttpResponse(data, content_type='application/json')