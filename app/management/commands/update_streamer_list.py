import json
import os
import requests
import time

import aiohttp
from aiohttp import ClientTimeout
import asyncio
from asgiref.sync import sync_to_async
from django.core.management.base import BaseCommand
from django.utils import timezone

from app.models import Game, Process


# add these to your Heroku -> Setting -> Config Vars using the same keys
# https://dev.twitch.tv/console/apps/create
TWITCH_CLIENT_ID = os.environ.get("TWITCH_CLIENT_ID")
TWITCH_APP_ACCESS_TOKEN = os.environ.get("TWITCH_APP_ACCESS_TOKEN")


def get_twitch_api_oauth_token():
    url = "https://id.twitch.tv/oauth2/token"
    params = {
        "client_id": TWITCH_CLIENT_ID,
        "client_secret": TWITCH_APP_ACCESS_TOKEN,
        "grant_type": "client_credentials"
    }
    response = requests.post(url=url, params=params)
    response_data = json.loads(response.text)
    access_token = response_data.get("access_token")
    return access_token


async def async_get_twitch_api_data(url: str, token: str, session, game_id="", paginate=False, cursor=""):
    data = []
    headers = {
        "Authorization": f"Bearer {token}",
        "Client-Id": TWITCH_CLIENT_ID
    }
    while True:
        # The two API calls used here, Get Top Games and Get Streams, use these parameters without colliding
        params = {
            "first": 100,
            "after": cursor,
            "game_id": game_id
        }
        async with session.get(url=url, headers=headers, params=params, timeout=0) as response:
            response_data = await response.json()
            rate_limit_remaining_string = response.headers.get("Ratelimit-Remaining")
            if rate_limit_remaining_string is not None:
                rate_limit_remaining = int(rate_limit_remaining_string)
                if rate_limit_remaining < 799:
                    print(f"--------Rate limit falling: {rate_limit_remaining}")
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


async def async_get_streamer_list(game, session, twitch_oauth_token):
    game_id = game.get("id")
    game_name = game.get("name")
    game_box_art_url = game.get("box_art_url")
    streamers = []
    total_viewers = 0
    # Get the streamers viewer count and url for each stream for this game
    # Set paginate to True to get more than 100 streamers per game if they exist
    streamers_data = await async_get_twitch_api_data(
        url="https://api.twitch.tv/helix/streams",
        game_id=game_id,
        token=twitch_oauth_token,
        paginate=False,
        session=session
    )
    for streamer in streamers_data:
        user_name = streamer.get("user_name")
        viewer_count = streamer.get("viewer_count")
        thumbnail_url = streamer.get("thumbnail_url")
        new_streamer = {
            "url": f"https://www.twitch.tv/{user_name}",
            "viewer_count": viewer_count,
            "thumbnail_url": thumbnail_url
        }
        streamers.append(new_streamer)
        total_viewers += viewer_count

    new_game, _ = await sync_to_async(Game.objects.update_or_create)(
        id=game_id,
        defaults={
            "name": game_name,
            "box_art_url": game_box_art_url,
            "streamers": streamers,
            "total_viewers": total_viewers
        }
    )
    print(f"Got {game_name} Streams, {total_viewers} total viewers")


async def get_games_list():
    conn = aiohttp.TCPConnector(limit=1)
    session = aiohttp.ClientSession(connector=conn, timeout=0.0)
    print("Getting OAuth Token")
    twitch_oauth_token = get_twitch_api_oauth_token()
    print("Getting Top Twitch Games")
    twitch_games = await async_get_twitch_api_data(
        url="https://api.twitch.tv/helix/games/top",
        paginate=True,
        token=twitch_oauth_token,
        session=session
    )
    print("Getting Streamers for Top Games")
    await asyncio.gather(
        *[async_get_streamer_list(game, session, twitch_oauth_token) for game in twitch_games]
    )
    print("Deleting Old Games")
    game_ids = [game.get("id") for game in twitch_games]
    await sync_to_async(Game.objects.delete.exclude)(id__in=game_ids)
    print("Setting timestamp")
    await sync_to_async(Process.objects.update_or_create)(
        name="game_list_update",
        defaults={
            "updated_at": timezone.now()
        }
    )


class Command(BaseCommand):
    help = 'Updates all Games and Streamers in the database'

    def handle(self, *args, **options):
        print("Starting Command")
        t0 = time.process_time()
        print("Getting Games List")
        asyncio.run(get_games_list())
        print("Finished Getting Games List")
        t1 = (time.process_time() - t0) / 60
        # is this java
        self.stdout.write(self.style.SUCCESS(f"Successfully got all Games and Streamers, took {t1} minutes"))
        return
