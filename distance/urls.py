'''distance/urls.py - Consists of non-administrative urls (not related to log
in, log out, passwords, or the admin site)'''
from django.conf.urls import url

from . import views
# for favicon and menu, need RedirectView
from django.views.generic.base import RedirectView

app_name = 'distance'
urlpatterns = [
    url(r'^home/$', views.index, name='index'),

    url(r'^signup/$', views.signup, name='signup'),

    # Adding friends
    url(r'^search_friends/$', views.search_friends, name='search_friends'),
    url(r'^add_friend/$', views.add_friend, name='add_friend'),

    # Viewing messages
    url(r'^messages/$', views.view_messages, name='view_messages'),

    # Accepting friend request
    url(r'^accept/$', views.accept, name='accept'),

    # View list of friends
    url(r'^friends/$', views.friends, name='friends'),

    # View homepage with a given friend
    url(r'^friends/(?P<friend_id>[0-9]+)/$', views.friend_view, name='friend_view'),

    # Add images to a given friend's homepage background
    url(r'^friends/(?P<friend_id>[0-9]+)/add_images/$', views.add_images, name='add_images'),
    url(r'^friends/(?P<friend_id>[0-9]+)/image_confirm/$', views.image_confirm, name='image_confirm'),

    # Send a message
    url(r'^send_msg/$', views.send_msg, name="send_msg"),
    url(r'^friends/(?P<friend_id>[0-9]+)/send_msg/$', views.send_msg, name='send_msg_f'),

    # Delete an image from a given friend's homepage background
    url(r'^friends/(?P<friend_id>[0-9]+)/del_img/$', views.del_img, name='del_img'),

    # Delete a friend.
    url(r'^del_friend/$', views.del_friend, name='del_friend'),

    # Settings
    url(r'^settings_view/$', views.settings_view, name='settings_view'),
    url(r'^settings_set/$', views.settings_set, name='settings_set'),

    # Images on the site
    url(r'^background\.jpg', RedirectView.as_view(url='static/distance/foto_no_exif.jpg'), name='background'),
    url(r'^compose\.png', RedirectView.as_view(url='static/distance/oie_transparent.png'), name='compose'),
    url(r'^logo\.png', RedirectView.as_view(url='static/distance/Logo.png'), name='logo'),
    url(r'^favicon\.png', RedirectView.as_view(url='static/distance/favicon.png'), name='favicon'),
    url(r'^favicon_apple\.png', RedirectView.as_view(url='static/distance/favicon_apple.png'), name='favicon_apple'),
    url(r'^menu\.png', RedirectView.as_view(url='static/distance/Menu.png'), name='menu'),
]