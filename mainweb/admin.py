from django.contrib import admin

from .models import Rooms
from .models import Cache_dir
from .models import Room_user

admin.site.register(Rooms)
admin.site.register(Cache_dir)
admin.site.register(Room_user)