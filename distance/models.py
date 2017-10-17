'''models.py - Creates the models User, Message, and Image.'''
from django.db import models

from django.contrib.auth.models import AbstractUser
import pytz

from django.conf import settings

class User(AbstractUser):
    '''A User has a timezone, connections (users that they are friends with),
    latitude, longitude, temperature unit, city, and country, on top of the
    attributes username, email, and password in AbstractUser.'''
    timezones = pytz.all_timezones
    tz_tuple_list = []
    for tz in timezones:
        tz_tuple_list.append((tz, tz))
    timezone = models.CharField(max_length=100, choices=tz_tuple_list)
    connections = models.ManyToManyField(settings.AUTH_USER_MODEL, null=True, blank=True)
    lat = models.FloatField(default=0)
    lng = models.FloatField(default=0)
    unit_list = [
        ('K', 'Kelvin'),
        ('C', 'Celsius'),
        ('F', 'Fahrenheit'),
    ]
    temp_unit = models.CharField(max_length=100, choices=unit_list, default='K')
    city = models.CharField(max_length=100, default="Chicago")
    country = models.CharField(max_length=100, default="United States of America")

class Message(models.Model):
    '''A Message has a sender, a receiver, content, a created_at DateTimeField,
    and a message type (either friend request or normal message).'''
    sender = models.ForeignKey(User, related_name="sender")
    receiver = models.ForeignKey(User, related_name="receiver")
    msg_content = models.TextField()
    created_at = models.DateTimeField()
    FRIEND_REQUEST = 'FR'
    NORMAL_MESSAGE = 'NM'
    msg_type_list = [
        ('FR', 'Friend Request'),
        ('NM', 'Normal Message'),
    ]
    msg_type = models.CharField(max_length=100, choices = msg_type_list, default=NORMAL_MESSAGE)
    read = models.BooleanField(default=False)

class Image(models.Model):
    '''An Image has two users that have the Image as one of their background
    images as well as the url to the image.'''
    user1 = models.ForeignKey(User, related_name="user1")
    user2 = models.ForeignKey(User, related_name="user2")
    users = [user1, user2]
    image_url = models.URLField()
