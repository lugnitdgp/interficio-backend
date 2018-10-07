from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from backend.models import Player, Level, Location
from django.contrib.auth.models import User
from django.core import serializers as ds
from rest_framework import serializers, viewsets
import json

#DRF viewset and serializers
class UserSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = User
        fields = ('url', 'username', 'email')

# ViewSets define the view behavior.
class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer

class LevelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Level
        fields = ('level_no','title','ques')

class LevelViewSet(viewsets.ModelViewSet):
    queryset = Level.objects.all()
    serializer_class = LevelSerializer



def index(req):
    data = {"page":"backend"}
    return JsonResponse(json.dumps(data), safe=False)

def leaderboard(req):
    data = Player.objects.all().order_by('-score')
    data = json.loads(ds.serialize("json", data))
    api_data = []
    for i in data:
        api_data.append(i.get('fields'))

    data = json.dumps(api_data)
    data = '{"standings" : '+data+'}'
    return HttpResponse(data, content_type='application/json')