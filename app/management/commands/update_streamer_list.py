import json
import os
import requests
import time

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


def get_twitch_api_data(url: str, token: str, game_id=None, paginate=False, cursor=None):
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
        response = requests.get(url=url, headers=headers, params=params)
        response_data = json.loads(response.text)
        rate_limit_remaining_string = response.headers.get("Ratelimit-Remaining")
        if rate_limit_remaining_string is not None:
            rate_limit_remaining = int(rate_limit_remaining_string)
            if rate_limit_remaining < 799:
                print(f"--------Rate limit falling: f{rate_limit_remaining}")
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


def get_games_list():
    twitch_oauth_token = get_twitch_api_oauth_token()
    # Get top games currently streaming on Twitch
    twitch_games = get_twitch_api_data(
        url="https://api.twitch.tv/helix/games/top",
        paginate=True,
        token=twitch_oauth_token
    )
    game_ids = []
    for game in twitch_games:
        game_id = game.get("id")
        game_ids.append(game_id)
        game_name = game.get("name")
        game_box_art_url = game.get("box_art_url")
        streamers = []
        total_viewers = 0
        # Get the streamers viewer count and url for each stream for this game
        streamers_data = get_twitch_api_data(
            url="https://api.twitch.tv/helix/streams",
            game_id=game_id,
            token=twitch_oauth_token
        )
        for streamer in streamers_data:
            user_name = streamer.get("user_name")
            viewer_count = streamer.get("viewer_count")
            thumbnail_url = streamer.get("thumbnail_url")
            # user_id = streamer.get("user_id")
            # new_streamer, _ = Streamer.objects.update_or_create(
            #     id=user_id,
            #     defaults={
            #         "url": f"https://www.twitch.tv/{user_name}",
            #         "viewer_count": viewer_count,
            #         "thumbnail_url": thumbnail_url
            #     }
            # )
            new_streamer = {
                "url": f"https://www.twitch.tv/{user_name}",
                "viewer_count": viewer_count,
                "thumbnail_url": thumbnail_url
            }
            streamers.append(new_streamer)
            total_viewers += viewer_count
        new_game, _ = Game.objects.get_or_create(
            id=game_id,
            defaults={
                "name": game_name,
                "box_art_url": game_box_art_url,
                "streamers": streamers,
                "total_viewers": total_viewers
            }
        )
        # new_game.streamers.set(streamers)
        # new_game.save()
        print(new_game.name)
    # Remove Games no longer listed
    print("Deleting Old Games")
    old_games = Game.objects.exclude(id__in=game_ids)
    for game in old_games:
        game.delete()
    # Set updated_at timestamp for process
    print("Setting timestamp")
    Process.objects.update_or_create(
        name="game_list_update",
        defaults={
            "updated_at": timezone.now()
        }
    )


class Command(BaseCommand):
    help = 'Updates all Games and Streamers in the database'

    def handle(self, *args, **options):
        t0 = time.process_time()
        get_games_list()
        t1 = (time.process_time() - t0) / 60
        # is this java
        self.stdout.write(self.style.SUCCESS(f"Successfully got all Games and Streamers, took {t1} minutes"))
        return
