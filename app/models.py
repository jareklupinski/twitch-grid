from django.db import models


class Streamer(models.Model):
    viewer_count = models.IntegerField()
    url = models.TextField()


class Game(models.Model):
    id = models.CharField(max_length=255, primary_key=True)
    name = models.CharField(max_length=255)
    streamers = models.ManyToManyField(Streamer)
