from django.conf.urls import url
from . import api

urlpatterns = [
    url('start', api.startGame),
    url('get_game', api.getGame),
    # url('init', api.initialize),
    url('move', api.move),
    url('say', api.say),
    url('details', api.details),
    url('join', api.joinGame),
    url('leave', api.leaveGame),
    url('roll', api.roll),
]