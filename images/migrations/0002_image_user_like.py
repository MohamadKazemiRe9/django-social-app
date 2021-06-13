# Generated by Django 3.2 on 2021-05-22 12:15

from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('images', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='image',
            name='user_like',
            field=models.ManyToManyField(blank=True, related_name='images_liked', to=settings.AUTH_USER_MODEL),
        ),
    ]
