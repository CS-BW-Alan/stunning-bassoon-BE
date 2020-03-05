from django.conf.urls import url
from . import api

urlpatterns = [
    url('start', api.start_game),
    url('init', api.initialize),
    url('move', api.move),
    url('say', api.say),
    url('details', api.details),
]