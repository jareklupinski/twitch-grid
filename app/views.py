import json

from django.shortcuts import render

from app.models import Game


def index(request):
    game_list = []
    games = Game.objects.all()
    for game in games:
        game_list.append({
            "name": game.name,
            "streamers": game.streamers
        })
    context = {'game_list': game_list}
    return render(request, 'app/index.html', context)
