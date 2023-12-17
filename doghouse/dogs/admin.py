from django.contrib import admin

from dogs.models import Dog, FavouriteDog

admin.site.register(Dog)
admin.site.register(FavouriteDog)