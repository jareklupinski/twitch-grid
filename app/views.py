from django.shortcuts import render

from app.models import Game


def index(request):
    game_list = Game.objects.all()[:10]
    context = {'game_list': game_list}
    return render(request, 'app/index.html', context)