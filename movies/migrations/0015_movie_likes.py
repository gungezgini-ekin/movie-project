# Generated by Django 4.2.15 on 2024-08-29 12:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0014_remove_movie_likes'),
    ]

    operations = [
        migrations.AddField(
            model_name='movie',
            name='likes',
            field=models.IntegerField(default=0),
        ),
    ]