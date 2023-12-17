# Generated by Django 5.0 on 2023-12-16 21:40

from django.conf import settings
from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('dogs', '0007_favouritedog_unique_favourites'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='favouritedog',
            name='unique-favourites',
        ),
        migrations.AlterUniqueTogether(
            name='favouritedog',
            unique_together={('user', 'dog')},
        ),
    ]
