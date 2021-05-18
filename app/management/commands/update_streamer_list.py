import json
import os
import requests

from django.core.management.base import BaseCommand, CommandError

from app.models import Game, Streamer


TWITCH_CLIENT_ID = os.environ.get("TWITCH_CLIENT_ID")
TWITCH_APP_ACCESS_TOKEN = os.environ.get("TWITCH_APP_ACCESS_TOKEN")

twitch_oauth_token = ""


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


def get_twitch_api_data(url: str, game_id=None, paginate=False, cursor=None):
    data = []
    headers = {
        "Authorization": f"Bearer {twitch_oauth_token}",
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
        rate_limit_remaining = int(response.headers.get("Ratelimit-Remaining"))
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
    # Get top 3000 games currently streaming on Twitch
    games = get_twitch_api_data(
        url="https://api.twitch.tv/helix/games/top",
        paginate=True
    )
    for game in games:
        game_id = game.get("id")
        game_name = game.get("name")
        streamers = []
        # Get the streamers viewer count and url for each stream for this game
        streamers_data = get_twitch_api_data(
            url="https://api.twitch.tv/helix/streams",
            game_id=game_id
        )
        for streamer in streamers_data:
            user_name = streamer.get("user_name")
            viewer_count = streamer.get("viewer_count")
            new_streamer = Streamer.objects.update_or_create(
                url=f"https://www.twitch.tv/{user_name}",
                viewer_count=viewer_count
            )
            streamers.append(new_streamer)
        new_game = Game.objects.update_or_create(
            id=game_id,
            name=game_name,
            streamers=streamers
        )
        # Sanity check
        print(new_game.name)


class Command(BaseCommand):
    help = 'Updates all Games and Streamers in the database'

    def handle(self, *args, **options):
        get_games_list()
        # is this java
        self.stdout.write(self.style.SUCCESS('Successfully got all Games and Streamers'))
        return