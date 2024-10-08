# Generated by Django 4.2.15 on 2024-09-06 10:55

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('users', '0012_remove_profile_want_to_watch_count_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='listname',
            name='likes',
            field=models.IntegerField(default=0),
        ),
        migrations.CreateModel(
            name='LikedList',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('like_date', models.DateTimeField(default=django.utils.timezone.now)),
                ('list_name', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='users.listname')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
