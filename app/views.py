from django.core.paginator import Paginator
from django.shortcuts import render

from app.models import Game


def index(request):
    games = Game.objects.all()
    paginator = Paginator(games, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'game_total': len(games),
        'page_obj': page_obj
    }
    return render(request, 'app/index.html', context)
