from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from backend.models import Player, Level, Location
from django.contrib.auth.models import User
from django.core import serializers as ds
from rest_framework import viewsets
from rest_framework.response import Response
import json

from backend.serializers import UserSerializer, LevelSerializer

#DRF viewset and serializers
class UserViewSet(viewsets.ViewSet):
    """
    A simple ViewSet for listing or retrieving users.
    """
    def list(self, request):
        queryset = User.objects.all()
        serializer = UserSerializer(queryset, many=True)
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        queryset = User.objects.all()
        user = get_object_or_404(queryset, pk=pk)
        serializer = UserSerializer(user)
        return Response(serializer.data)


class LevelViewSet(viewsets.ModelViewSet):
    queryset = Level.objects.all()
    serializer_class = LevelSerializer



def leaderboard(req):
    data = Player.objects.all().order_by('-score')
    data = json.loads(ds.serialize("json", data))
    api_data = []
    for i in data:
        api_data.append(i.get('fields'))

    data = json.dumps(api_data)
    data = '{"standings" : '+data+'}'
    return HttpResponse(data, content_type='application/json')