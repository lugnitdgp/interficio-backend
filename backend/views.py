from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from backend.models import Player
from django.core import serializers
import json

# Create your views here.
def index(req):
    data = {"page":"backend"}
    return JsonResponse(json.dumps(data), safe=False)

def leaderboard(req):
    data = Player.objects.all().order_by('-score')
    data = json.loads(serializers.serialize("json", data))
    api_data = []
    for i in data:
        api_data.append(i.get('fields'))

    data = json.dumps(api_data)
    data = '{"standings" : '+data+'}'
    return HttpResponse(data, content_type='application/json')