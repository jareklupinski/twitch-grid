# Generated by Django 3.2.3 on 2021-05-18 05:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='game',
            name='box_art_url',
            field=models.CharField(max_length=1024),
        ),
        migrations.AlterField(
            model_name='game',
            name='name',
            field=models.CharField(max_length=1024),
        ),
    ]
