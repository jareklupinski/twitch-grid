import os
import time
import requests

import aiohttp
import asyncio
from asgiref.sync import sync_to_async
from django.conf import settings
from django.core.cache import cache
from django.core.management.base import BaseCommand
from django.utils import timezone

from app.models import Game, Process


# add these to your Heroku -> Setting -> Config Vars using the keys from https://dev.twitch.tv/console/apps/create
TWITCH_CLIENT_ID = os.environ.get("TWITCH_CLIENT_ID")
TWITCH_APP_ACCESS_TOKEN = os.environ.get("TWITCH_APP_ACCESS_TOKEN")
# simultaneous connections to the Twitch API
_num_connections = 30

def get_twitch_api_oauth_token():
    url = "https://id.twitch.tv/oauth2/token"
    params = {
        "client_id": TWITCH_CLIENT_ID,
        "client_secret": TWITCH_APP_ACCESS_TOKEN,
        "grant_type": "client_credentials"
    }
    response = requests.post(url=url, params=params)
    response_data = response.json()
    access_token = response_data.get("access_token")
    return access_token


async def get_twitch_api_data(url: str, token: str, session, game_id="", paginate=False, cursor="", first=100):
    data = []
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": TWITCH_CLIENT_ID
    }
    while True:
        # The two API calls used here, Get Top Games and Get Streams, use these parameters without colliding
        params = {
            "first": first,
            "after": cursor,
            "game_id": game_id
        }
        async with session.get(url=url, headers=headers, params=params, timeout=0) as response:
            response_data = await response.json()
            rate_limit_remaining_string = response.headers.get("Ratelimit-Remaining")
            if rate_limit_remaining_string is not None:
                rate_limit_remaining = int(rate_limit_remaining_string)
                if rate_limit_remaining < (_num_connections + 10):
                    rate_limit_reset_string = response.headers.get("Ratelimit-Reset")
                    rate_limit_reset = int(rate_limit_reset_string)
                    epoch_now = int(time.time())
                    time_to_wait = rate_limit_reset - epoch_now
                    if time_to_wait > 0:
                        time_to_wait += 1
                        print(f"Rate limit hit: {rate_limit_remaining}, pausing for {time_to_wait}")
                        time.sleep(time_to_wait)
            json_data = response_data.get("data")
            for entry in json_data:
                data.append(entry)
            pagination = response_data.get("pagination")
            cursor = None
            if pagination is not None:
                cursor = pagination.get("cursor")
            if cursor is None or paginate is False:
                break
    return data


async def get_streamer_list(game, session, twitch_oauth_token):
    game_id = game.get("id")
    game_name = game.get("name")
    game_box_art_url = game.get("box_art_url")
    current_streamers = []
    total_viewers = 0
    magic_number_viewers = 0
    # Get the streamers viewer count and url for each stream for this game
    # Set paginate to True to get more than 100 streamers per game if they exist
    streamers = await get_twitch_api_data(
        url="https://api.twitch.tv/helix/streams",
        game_id=game_id,
        token=twitch_oauth_token,
        paginate=False,
        session=session
    )
    if len(streamers) == 0:
        return
    for streamer in streamers:
        user_login = streamer.get("user_login")
        viewer_count = streamer.get("viewer_count")
        thumbnail_url = streamer.get("thumbnail_url")
        new_streamer = {
            "url": f"https://www.twitch.tv/{user_login}",
            "viewer_count": viewer_count,
            "thumbnail_url": thumbnail_url
        }
        current_streamers.append(new_streamer)
        total_viewers += viewer_count
        magic_number_viewers += viewer_count ** 2

    # fiddling with the magic number calculation
    magic_number = (magic_number_viewers ** (1. / 2)) / len(streamers)

    new_game, _ = await sync_to_async(Game.objects.update_or_create)(
        id=game_id,
        defaults={
            "name": game_name,
            "box_art_url": game_box_art_url,
            "streamers": current_streamers,
            "total_viewers": total_viewers,
            "magic_number": magic_number,
        }
    )
    # print(f"{new_game.name}: {total_viewers} total viewers")


async def update_games_list(token):
    conn = aiohttp.TCPConnector(limit=_num_connections)  # raise this until Twitch's rate limiter starts complaining
    session = aiohttp.ClientSession(connector=conn, timeout=0.0)
    print("Getting Top Games")
    games = await get_twitch_api_data(
        url="https://api.twitch.tv/helix/games/top",
        paginate=True,
        token=token,
        session=session
    )
    print("Getting Streamers for Top Games")
    await asyncio.gather(*[get_streamer_list(game, session, token) for game in games])
    print("Deleting Old Games")
    game_ids = [game.get("id") for game in games]
    old_games = await sync_to_async(Game.objects.exclude)(id__in=game_ids)
    await sync_to_async(old_games.delete)()

    await session.close()
    await conn.close()


class Command(BaseCommand):
    help = 'Updates all Games and Streamers in the database'

    def handle(self, *args, **options):
        print("Starting Command")
        t0 = time.time()
        print("Getting OAuth Token")
        token = get_twitch_api_oauth_token()
        print("Updating Games List")
        asyncio.run(update_games_list(token))
        print("Setting Timestamp")
        Process.objects.update_or_create(name="game_list_update", defaults={"updated_at": timezone.now()})
        print("Invalidating Cache")
        cache.clear()
        if settings.URL is not None:
            print("Warming Cache")
            requests.get(settings.URL)
            requests.get(settings.URL + 'magic')
        t1 = (time.time() - t0) / 60
        # is this java
        self.stdout.write(self.style.SUCCESS(f"Successfully got all Games and Streamers, took {t1:.2f} minutes"))
        return
