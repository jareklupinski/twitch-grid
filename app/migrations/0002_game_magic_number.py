# Generated by Django 3.2.3 on 2021-05-22 00:34

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='game',
            name='magic_number',
            field=models.IntegerField(default=0),
            preserve_default=False,
        ),
    ]