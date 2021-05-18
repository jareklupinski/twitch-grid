# Generated by Django 3.2.3 on 2021-05-18 01:53

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Streamer',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('url', models.URLField()),
                ('viewer_count', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=255)),
                ('streamers', models.ManyToManyField(related_name='games', to='app.Streamer')),
            ],
        ),
    ]
