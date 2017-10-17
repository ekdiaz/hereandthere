# admin.py - Registers the User, Message, and Image models for the admin site.
from django.contrib import admin
from distance.models import User, Message, Image

# Register your models here.
admin.site.register(User)
admin.site.register(Message)
admin.site.register(Image)