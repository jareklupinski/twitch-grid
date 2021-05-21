from django.core.paginator import Paginator
from django.shortcuts import render
from django.views.decorators.cache import cache_page

from app.models import Game, Process

timeout = 300


@cache_page(timeout)
def index(request):
    games = Game.objects.all().order_by("-total_viewers")
    process = Process.objects.get(name="game_list_update")
    paginator = Paginator(games, 200)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    context = {
        'update_time': process.updated_at,
        'game_total': len(games),
        'page_obj': page_obj
    }
    return render(request, 'app/index.html', context)
