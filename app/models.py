from django.db import models

# too expensive to keep these per row in Heroku
# class Streamer(models.Model):
#     id = models.BigIntegerField(primary_key=True)
#     url = models.URLField()
#     viewer_count = models.IntegerField()


class Process(models.Model):
    name = models.CharField(max_length=255, primary_key=True)
    updated_at = models.TimeField()


class Game(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=1024)
    box_art_url = models.CharField(max_length=1024)
    streamers = models.JSONField()
    total_viewers = models.IntegerField()
    # streamers = models.ManyToManyField('Streamer', related_name='games')

    def __str__(self):
        return self.name
