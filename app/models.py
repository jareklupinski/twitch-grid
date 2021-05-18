from django.db import models

# too expensive to keep these per row in Heroku
# class Streamer(models.Model):
#     id = models.BigIntegerField(primary_key=True)
#     url = models.URLField()
#     viewer_count = models.IntegerField()


class Game(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    box_art_url = models.URLField()
    streamer = models.JSONField()
    # streamers = models.ManyToManyField('Streamer', related_name='games')
