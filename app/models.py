from django.db import models


class Process(models.Model):
    name = models.CharField(max_length=255, primary_key=True)
    updated_at = models.TimeField()


class Game(models.Model):
    id = models.BigIntegerField(primary_key=True)
    name = models.CharField(max_length=1024)
    box_art_url = models.CharField(max_length=1024)
    streamers = models.JSONField()
    total_viewers = models.IntegerField()
    magic_number = models.IntegerField()

    def __str__(self):
        return self.name
