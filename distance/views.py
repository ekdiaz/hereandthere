'''views.py - Contains the various views for the site.'''

from django.contrib.auth import login, authenticate
from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.contrib import messages
from django.urls import reverse
from django.conf import settings

from django.db.models import Q

from .forms import SignUpForm, SettingsForm
from .models import User, Message, Image

import datetime
import pytz

from pyowm import OWM

from geopy.geocoders import Nominatim



def index(request):
    '''Displays the home page.'''
    if request.user.is_authenticated:
        friends_list = request.user.connections.all()
        num_msgs = Message.objects.filter(receiver=request.user, read=False).count()
        return render(request, 'distance/index.html', {'friends_list': friends_list, 'num_msgs': num_msgs})
    return HttpResponseRedirect(reverse('login'))

def signup(request):
    '''Signs up a user and locates their city and country based on their
    inputted latitude and longitude (users can always change it if it's incorrect).'''
    if not request.user.is_authenticated:
        if request.method == 'POST':
            form = SignUpForm(request.POST)
            if form.is_valid():
                form.save()
                username = form.cleaned_data.get('username')
                raw_password = form.cleaned_data.get('password1')
                user = authenticate(username=username, password=raw_password)
                login(request, user)
                # geopy uses an API that either declares a city name by
                # village, city, suburb, hamlet, or town based on the city
                # size. So we must try them all.
                try:
                    geolocator = Nominatim()
                    lat_lng = str(user.lat) + ', ' + str(user.lng)
                    location = geolocator.reverse(lat_lng)
                    user.city = location.raw['address']['village']
                except KeyError:
                    try:
                        user.city = location.raw['address']['city']
                    except KeyError:
                        try:
                            user.city = location.raw['address']['suburb']
                        except KeyError:
                            try:
                                user.city = location.raw['address']['hamlet']
                            except KeyError:
                                try:
                                    user.city = location.raw['address']['town']
                                except KeyError:
                                    user.city = 'Not Found'
                try:
                    user.country = location.raw['address']['country']
                except KeyError:
                    user.country = 'Not Found'
                user.save()
                return HttpResponseRedirect(reverse('distance:index'))
        else:
            form = SignUpForm()
        return render(request, 'registration/signup.html', {'form': form})
    messages.add_message(request, messages.INFO, 'You are already logged in. You must log out to create a new user.')
    return HttpResponseRedirect(reverse('distance:index'))

def search_friends(request):
    '''Searches for Users based on the username searched so that the user can
    add as a friend.'''
    if request.user.is_authenticated:
        if request.method == 'GET':
            search = request.GET.get('search_friends')
            # If that username exists
            if User.objects.filter(username=search).count() > 0:
                # Prevent the user from friending theirself
                if User.objects.filter(username=search)[0] != request.user:
                    # Check if they're already friends
                    if User.objects.filter(username=search)[0] in request.user.connections.all():
                        already_friends = True
                    else:
                        already_friends = False
                    # Check if the user has already sent the receiver a friend
                    # request.
                    if Message.objects.filter(sender=request.user,
                        receiver=User.objects.filter(username=search)[0],
                        msg_type=Message.FRIEND_REQUEST).count() > 0:
                        pending = True
                    else:
                        pending = False
                    friends_list = request.user.connections.all()
                    num_msgs = Message.objects.filter(receiver=request.user, read=False).count()
                    context = {
                        'search': search,
                        'already_friends': already_friends,
                        'pending': pending,
                        'friends_list': friends_list,
                        'num_msgs': num_msgs,
                    }
                    return render(request, 'distance/search_results.html', context)
                else:
                    messages.add_message(request, messages.INFO, 'That\'s your username!')
            else:
                messages.add_message(request, messages.INFO, 'That username does not exist.')
    else:
        messages.add_message(request, messages.INFO, 'You are not logged in.')
    return HttpResponseRedirect(reverse('distance:index'))

def add_friend(request):
    '''Sends the receiver a Friend Request message.'''
    if request.user.is_authenticated:
        if request.method == 'POST':
            username = request.POST.get('friend_result')
            user = User.objects.filter(username=username)[0]
            msg = request.user.username + ' has sent you a friend request.'
            dt = datetime.datetime.now()
            friend_request = Message(sender=request.user, receiver=user, msg_content=msg, created_at=dt, msg_type=Message.FRIEND_REQUEST)
            friend_request.save()
            messages.add_message(request, messages.INFO, 'You have sent ' + username + ' a friend request.')
    else:
        messages.add_message(request, messages.INFO, 'You are not logged in.')
    return HttpResponseRedirect(reverse('distance:index'))

def view_messages(request):
    '''Gets all the messages that the user is the receiver of.'''
    if request.user.is_authenticated:
        msg_list = Message.objects.filter(receiver=request.user)
        friends_list = request.user.connections.all()
        for msg in msg_list:
            msg.read = True
            msg.save()
        num_msgs = 0
        return render(request, 'distance/messages.html', {'msg_list': msg_list, 'friends_list': friends_list, 'num_msgs': num_msgs})
    else:
        messages.add_message(request, messages.INFO, 'You are not logged in.')
    return HttpResponseRedirect(reverse('distance:index'))

def accept(request):
    '''Accepts a friend request and makes the two users friends.'''
    if request.user.is_authenticated:
        if request.method == 'POST':
            for msg in Message.objects.filter(receiver=request.user):
                if request.POST.get(str(msg.id)) == 'Accept':
                    # add friend request sender to this user's friends
                    request.user.connections.add(msg.sender)
                    # add this user to friend request sender's friends
                    msg.sender.connections.add(request.user)
                    # save both
                    request.user.save()
                    msg.sender.save()
                    messages.add_message(request, messages.INFO, msg.sender.username + ' has been added as a friend.')
                    msg.delete()
                    return HttpResponseRedirect(reverse('distance:view_messages'))
                # delete message (reject friend request)
                elif request.POST.get(str(msg.id) + 'X') == 'X':
                    msg.delete()
                    return HttpResponseRedirect(reverse('distance:view_messages'))
    else:
        messages.add_message(request, messages.INFO, 'You are not logged in.')
    return HttpResponseRedirect(reverse('distance:index'))

def friends(request):
    '''Displays list of friends.'''
    if request.user.is_authenticated:
        friends_list = request.user.connections.all()
        num_msgs = Message.objects.filter(receiver=request.user, read=False).count()
        return render(request, 'distance/friends.html', {'friends_list': friends_list, 'num_msgs': num_msgs})
    else:
        messages.add_message(request, messages.INFO, 'You are not logged in.')
    return HttpResponseRedirect(reverse('distance:index'))

def friend_view(request, **kwargs):
    '''Displays homepage for a given friend.'''
    if request.user.is_authenticated:
        if 'friend_id' in kwargs:
            friend_id = kwargs['friend_id']
            # check to make sure that the user is actually friends with this user
            # (because otherwise they could put arbitrary
            # numbers at the end of the url to see other user pages).
            if request.user.connections.filter(id=friend_id).count() > 0:
                # get offsets for clocks
                friend = request.user.connections.filter(id=friend_id)[0]

                # get request.user's utc offset
                utc_offset1 = datetime.datetime.now(pytz.timezone(request.user.timezone)).strftime('%z')
                hr_offset1 = int(utc_offset1[:3])
                # check if utc offset is positive or negative
                if utc_offset1[:1] == '+':
                    min_offset1 = int(utc_offset1[3:])
                else:
                    min_offset1 = -1 * int(utc_offset1[3:])

                # get friend's utc offset
                utc_offset2 = datetime.datetime.now(pytz.timezone(friend.timezone)).strftime('%z')
                hr_offset2 = int(utc_offset2[:3])
                if utc_offset2[:1] == '+':
                    min_offset2 = int(utc_offset2[3:])
                else:
                    min_offset2 = -1 * int(utc_offset2[3:])

                # get temps and weather
                owm = OWM(settings.WEATHER_API_KEY)

                # get unit to display temperature in
                if request.user.temp_unit == 'K':
                    temp_unit = 'kelvin'
                    unit = 'K'
                elif request.user.temp_unit == 'C':
                    temp_unit = 'celsius'
                    unit = '°C'
                else:
                    temp_unit = 'fahrenheit'
                    unit = '°F'

                # get temp for user and temp for friend
                temp1 = str(int(round(owm.weather_at_coords(request.user.lat,
                    request.user.lng).get_weather().get_temperature(temp_unit)['temp']))) + unit
                temp2 = str(int(round(owm.weather_at_coords(friend.lat,
                    friend.lng).get_weather().get_temperature(temp_unit)['temp']))) + unit

                # get weather status for user and for friend
                status1 = owm.weather_at_coords(request.user.lat, request.user.lng).get_weather().get_detailed_status()
                status2 = owm.weather_at_coords(friend.lat, friend.lng).get_weather().get_detailed_status()

                # background images
                images = []
                for img in Image.objects.all():
                    if request.user == img.user1 and friend == img.user2 or request.user == img.user2 and friend == img.user1:
                        images.append(img.image_url)

                friends_list = request.user.connections.all()

                # Since messages can be viewed from the friend view, any message
                # from friend to user is read when friend view is open.
                msg_list = Message.objects.filter(receiver=request.user, sender=friend)
                for msg in msg_list:
                    msg.read = True
                    msg.save()
                num_msgs = Message.objects.filter(receiver=request.user, read=False).count()

                city1 = request.user.city
                country1 = request.user.country
                city2 = friend.city
                country2 = friend.country

                context = {
                    'friend': friend,
                    'hr_offset1': hr_offset1,
                    'hr_offset2': hr_offset2,
                    'min_offset1': min_offset1,
                    'min_offset2': min_offset2,
                    'temp1': temp1,
                    'temp2': temp2,
                    'status1': status1,
                    'status2': status2,
                    'images': images,
                    'friends_list': friends_list,
                    'num_msgs': num_msgs,
                    'msg_list': msg_list,
                    'city1': city1,
                    'country1': country1,
                    'city2': city2,
                    'country2': country2,
                }

                return render(request, 'distance/friend_view.html', context)
            else:
                messages.add_message(request, messages.INFO, 'You are not friends with this user.')
                return HttpResponseRedirect(reverse('distance:index'))
    else:
        messages.add_message(request, messages.INFO, 'You are not logged in.')
    return HttpResponseRedirect(reverse('distance:index'))

def add_images(request, **kwargs):
    '''Displays add images page for a given friend with all current
    images (able to delete) and a form to add more.'''
    if request.user.is_authenticated:
        if 'friend_id' in kwargs:
            friend_id = kwargs['friend_id']
            # check to make sure that the user is actually friends with this user
            # (because otherwise they could put arbitrary
            # numbers at the end of the url to see other user pages).
            if request.user.connections.filter(id=friend_id).count() > 0:
                friend = request.user.connections.filter(id=friend_id)[0]
                friends_list = request.user.connections.all()
                num_msgs = Message.objects.filter(receiver=request.user, read=False).count()
                # background images
                images = []
                for img in Image.objects.all():
                    if request.user == img.user1 and friend == img.user2 \
                        or request.user == img.user2 and friend == img.user1:
                        images.append(img.image_url)
                context = {'friend': friend,
                    'friends_list': friends_list,
                    'num_msgs': num_msgs,
                    'images': images}
                return render(request, 'distance/add_images.html', context)
            else:
                messages.add_message(request, messages.INFO, 'You are not friends with this user.')
    else:
        messages.add_message(request, messages.INFO, 'You are not logged in.')
    return HttpResponseRedirect(reverse('distance:index'))

def image_confirm(request, **kwargs):
    '''Adds a given image to the friend view.'''
    if request.user.is_authenticated:
        if request.method == 'POST':
            if 'friend_id' in kwargs:
                friend_id = kwargs['friend_id']
                # check to make sure that the user is actually friends with this user
                # (because otherwise they could put arbitrary
                # numbers at the end of the url to see other user pages.
                if request.user.connections.filter(id=friend_id).count() > 0:
                    friend = request.user.connections.filter(id=friend_id)[0]
                    image_url = request.POST.get('image_url')
                    image = Image(user1=request.user, user2=friend, image_url=image_url)
                    image.save()
                    messages.add_message(request, messages.INFO, 'You have successfully added an image.')
                    return HttpResponseRedirect(reverse('distance:friend_view', args=(friend.id,)))
                else:
                    messages.add_message(request, messages.INFO, 'You are not friends with this user.')
                    return HttpResponseRedirect(reverse('distance:index'))
    else:
        messages.add_message(request, messages.INFO, 'You are not logged in.')
    return HttpResponseRedirect(reverse('distance:index'))

def send_msg(request, **kwargs):
    '''Sends a message between a user and a friend.'''
    if request.user.is_authenticated:
        if request.method == 'POST':
            if 'friend_id' in kwargs:
                friend_id = kwargs['friend_id']
                # check to make sure that the user is actually friends with this user
                # (because otherwise they could put arbitrary
                # numbers at the end of the url to see other user pages).
                if request.user.connections.filter(id=friend_id).count() > 0:
                    friend = request.user.connections.filter(id=friend_id)[0]

                    # delete message from friend page
                    for msg in Message.objects.filter(receiver=request.user, sender=friend):
                        if request.POST.get(str(msg.id) + 'FX') == 'X':
                            msg.delete()
                            return HttpResponseRedirect(reverse('distance:friend_view', args=(msg.sender.id,)))

                    # send message from friend page
                    msg_content = request.POST.get('msg')
                    dt = datetime.datetime.now()
                    msg = Message(sender=request.user, receiver=friend, msg_content=msg_content, created_at=dt, msg_type=Message.NORMAL_MESSAGE)
                    msg.save()
                    messages.add_message(request, messages.INFO, 'You have sent ' + friend.username + ' a message.')
                    return HttpResponseRedirect(reverse('distance:friend_view', args=(friend.id,)))
                else:
                    messages.add_message(request, messages.INFO, 'You are not friends with this user.')

            else:
                # send message from messages page
                receiver = request.POST.get('receiver')
                if User.objects.filter(username=receiver).count() > 0:
                    if User.objects.filter(username=receiver)[0] in request.user.connections.all():
                        receiver_user = User.objects.filter(username=receiver)[0]
                        msg_content = request.POST.get('msg')
                        dt = datetime.datetime.now()
                        msg = Message(sender=request.user, receiver=receiver_user, msg_content=msg_content, created_at=dt, msg_type=Message.NORMAL_MESSAGE)
                        msg.save()
                        messages.add_message(request, messages.INFO, 'You have sent ' + receiver + ' a message.')
                    else:
                        messages.add_message(request, messages.INFO, 'You are not friends with this user.')
                else:
                    messages.add_message(request, messages.INFO, 'That username does not exist.')
        return HttpResponseRedirect(reverse('distance:view_messages'))
    else:
        messages.add_message(request, messages.INFO, 'You are not logged in.')
    return HttpResponseRedirect(reverse('distance:index'))

def del_img(request, **kwargs):
    '''Deletes images from a friend page.'''
    if request.user.is_authenticated:
        if request.method == 'POST':
            if 'friend_id' in kwargs:
                friend_id = kwargs['friend_id']
                # check to make sure that the user is actually friends with this
                # user (because otherwise they could put arbitrary
                # numbers at the end of the url to see other user pages).
                if request.user.connections.filter(id=friend_id).count() > 0:
                    friend = request.user.connections.filter(id=friend_id)[0]
                    img_list = Image.objects.filter(Q(user1=request.user, user2=friend) | Q(user1=friend, user2=request.user))
                    for img in img_list:
                        if request.POST.get(img.image_url) == 'X':
                            img.delete()
                            return HttpResponseRedirect(reverse('distance:friend_view', args=(friend.id,)))
                else:
                    messages.add_message(request, messages.INFO, 'You are not friends with this user.')
    else:
        messages.add_message(request, messages.INFO, 'You are not logged in.')
    return HttpResponseRedirect(reverse('distance:index'))

def del_friend(request):
    '''Deletes a friend.'''
    if request.user.is_authenticated:
        if request.method == 'POST':
            for friend in request.user.connections.all():
                if request.POST.get(str(friend.id)) == 'X':
                    request.user.connections.remove(friend)
                    messages.add_message(request, messages.INFO, 'You have unfriended ' + friend.username + '.')
                    return HttpResponseRedirect(reverse('distance:friends'))
            messages.add_message(request, messages.INFO, 'You are not friends with this user.')
            return HttpResponseRedirect(reverse('distance:friends'))
    else:
        messages.add_message(request, messages.INFO, 'You are not logged in.')
    return HttpResponseRedirect(reverse('distance:index'))

def settings_view(request):
    '''Views settings so user can change settings.'''
    if request.user.is_authenticated:
        timezone = request.user.timezone
        lat = request.user.lat
        lng = request.user.lng
        temp_unit = request.user.temp_unit
        city = request.user.city
        country = request.user.country

        friends_list = request.user.connections.all()
        num_msgs = Message.objects.filter(receiver=request.user, read=False).count()
        data = {
            'timezone': timezone,
            'lat': lat,
            'lng': lng,
            'temp_unit': temp_unit,
            'city': city,
            'country': country,
        }
        form = SettingsForm(initial=data)
        context = {
            'form': form,
            'friends_list': friends_list,
            'num_msgs': num_msgs,
        }
        return render(request, 'distance/settings_view.html', context)
    else:
        messages.add_message(request, messages.INFO, 'You are not logged in.')
    return HttpResponseRedirect(reverse('distance:index'))

def settings_set(request):
    '''Changes settings.'''
    if request.user.is_authenticated:
        if request.method == 'POST':
            tz = request.POST.get('timezone')
            lat = request.POST.get('lat')
            lng = request.POST.get('lng')
            unit = request.POST.get('temp_unit')
            city = request.POST.get('city')
            country = request.POST.get('country')
            request.user.timezone = tz
            request.user.lat = lat
            request.user.lng = lng
            request.user.temp_unit = unit
            request.user.city = city
            request.user.country = country
            request.user.save()
            messages.add_message(request, messages.INFO, 'You have changed your settings.')
            return HttpResponseRedirect(reverse('distance:settings_view'))
    else:
        messages.add_message(request, messages.INFO, 'You are not logged in.')
    return HttpResponseRedirect(reverse('distance:index'))