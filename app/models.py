from django.db import models


class Streamer(models.Model):
    url = models.URLField(primary_key=True)
    viewer_count = models.IntegerField()


class Game(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    streamers = models.ManyToManyField('Streamer', related_name='games')
