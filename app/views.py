from django.core.paginator import Paginator
from django.shortcuts import render

from app.models import Game, Process


def index(request):
    games = Game.objects.all()
    process = Process.objects.get(name="game_list_update")
    paginator = Paginator(games, 100)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'update_time': process.updated_at,
        'game_total': len(games),
        'page_obj': page_obj
    }
    return render(request, 'app/index.html', context)
