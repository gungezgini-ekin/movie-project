# Generated by Django 4.2.15 on 2024-08-23 07:40

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('movies', '0009_remove_movie_review_count'),
    ]

    operations = [
        migrations.AddField(
            model_name='review',
            name='review_date',
            field=models.DateField(default=django.utils.timezone.now),
        ),
    ]
