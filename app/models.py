from django.db import models


class Streamer(models.Model):
    id = models.BigIntegerField(primary_key=True)
    url = models.URLField()
    viewer_count = models.IntegerField()


class Game(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=255)
    streamers = models.ManyToManyField('Streamer', related_name='games')
