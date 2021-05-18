from django.shortcuts import render

from app.models import Game

def index(request):
    game_list = Game.objects.all()
    context = {'game_list': game_list}
    return render(request, 'index.html', context)