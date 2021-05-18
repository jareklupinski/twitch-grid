from django.shortcuts import render

from app.models import Game


def index(request):
    print("got request")
    game_list = Game.objects.all()
    print("got games")
    context = {'game_list': game_list}
    print("got context")
    return render(request, 'index.html', context)