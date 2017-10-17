'''forms.py - Creates the SignUpForm and SettingsForm classes so users can
sign up and change their settings.'''
from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User
import pytz

class SignUpForm(UserCreationForm):
    '''SignUpForm consists of a timezone (choice field between all timezones
    listed in pytz, latitude (float field), and longitude (float field).
    It then creates a User with a username, email, password, timezone, and
    latitude and longitude.'''
    timezones = pytz.all_timezones
    tz_tuple_list = []
    for tz in timezones:
        tz_tuple_list.append((tz, tz))
    timezone = forms.ChoiceField(choices=tz_tuple_list, help_text='Required. Choose your timezone.')
    lat = forms.FloatField(max_value=90, min_value=-90, help_text='Required. Allow location services or input your latitude.', label='Latitude')
    lng = forms.FloatField(max_value=180, min_value=-180, help_text='Required. Allow location services or input your longitude.', label='Longitude')

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2', 'timezone','lat', 'lng')

class SettingsForm(forms.Form):
    '''SettingsForm enables a user to change their settings. They can change
    their timezone, latitude, longitude, city, country, or temperature unit.'''
    timezones = pytz.all_timezones
    tz_tuple_list = []
    for tz in timezones:
        tz_tuple_list.append((tz, tz))
    timezone = forms.ChoiceField(choices=tz_tuple_list, help_text='Change your timezone.')
    lat = forms.FloatField(max_value=90, min_value=-90, help_text='Change your latitude.', label='Latitude')
    lng = forms.FloatField(max_value=180, min_value=-180, help_text='Change your longitude.', label='Longitude')
    city = forms.CharField(help_text='Change your city.')
    country = forms.CharField(help_text=' Change your city.')
    unit_list = [
        ('K', 'Kelvin'),
        ('C', 'Celsius'),
        ('F', 'Fahrenheit'),
    ]
    temp_unit = forms.ChoiceField(choices=unit_list, help_text='Change your temperature unit.', label='Temperature Unit')

    class Meta:
        model = User
        fields = ('timezone', 'lat', 'lng', 'temp_unit', 'city', 'country')