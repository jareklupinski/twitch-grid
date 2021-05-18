from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Game',
            fields=[
                ('id', models.BigIntegerField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=1024)),
                ('box_art_url', models.CharField(max_length=1024)),
                ('streamers', models.JSONField()),
                ('total_viewers', models.IntegerField()),
            ],
        ),
        migrations.CreateModel(
            name='Process',
            fields=[
                ('name', models.CharField(max_length=255, primary_key=True, serialize=False)),
                ('updated_at', models.TimeField()),
            ],
        ),
    ]
