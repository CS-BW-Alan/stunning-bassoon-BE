from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from pusher import Pusher
from django.http import JsonResponse
from decouple import config
from django.contrib.auth.models import User
from .models import *
from rest_framework.decorators import api_view
import json
from util.create_world import StartRooms
from adventure.models import Player, Room
from util.map_generator import World
from time import gmtime

# instantiate pusher
pusher = Pusher(app_id=config('PUSHER_APP_ID'), key=config('PUSHER_KEY'), secret=config('PUSHER_SECRET'), cluster=config('PUSHER_CLUSTER'))

@csrf_exempt
@api_view(["GET"])
def initialize(request):
    # StartRooms.create_rooms()
    World.create_rooms()
    
    user = request.user
    user.player = Player()
    user.player.save()
    user.save()
    player = user.player
    player_id = player.id
    uuid = player.uuid
    room = player.room()
    players = room.playerNames(player_id)
    return JsonResponse({'uuid': uuid, 'name':player.user.username, 'title':room.title, 'description':room.description, 'players':players}, safe=True)


# @csrf_exempt
@api_view(["POST"])
def move(request):
    dirs={"n": "north", "s": "south", "e": "east", "w": "west"}
    reverse_dirs = {"n": "south", "s": "north", "e": "west", "w": "east"}
    player = request.user.player
    player_id = player.id
    player_uuid = player.uuid
    data = json.loads(request.body)
    direction = data['direction']
    room = player.room()
    nextRoomID = None
    if direction == "n":
        nextRoomID = room.n_to
    elif direction == "s":
        nextRoomID = room.s_to
    elif direction == "e":
        nextRoomID = room.e_to
    elif direction == "w":
        nextRoomID = room.w_to
    if nextRoomID is not None and nextRoomID > 0:
        nextRoom = Room.objects.get(id=nextRoomID)
        player.currentRoom=nextRoomID
        player.save()
        players = nextRoom.playerNames(player_id)
        currentPlayerUUIDs = room.playerUUIDs(player_id)
        nextPlayerUUIDs = nextRoom.playerUUIDs(player_id)
        
        # Create dictionary for pusher
        # world_dict = { 
        #     "players": [{
        #         "player_id": p.id,
        #         "username": p.user.username,
        #         "points": p.points,
        #         "current_room": p.currentRoom
        #     } for p in Player.objects.all()],
        #     "rooms": [{
        #         "room_id": r.id,
        #         "players": [p.id for p in Player.objects.filter(currentRoom=r.id)],
        #         "points": r.points
        #     } for r in Room.objects.all()]
        # }

        updated = {
            "player": {
                "player_id": player.id,
                "username": player.user.username,
                "points": player.points,
                "current_room": player.currentRoom
            },
            "oldRoom": {
                "room_id": room.id,
                "players": [p.id for p in Player.objects.filter(currentRoom=room.id)],
                "points": room.points
            },
            "newRoom": {
                "room_id": nextRoom.id,
                "players": [p.id for p in Player.objects.filter(currentRoom=nextRoom.id)],
                "points": nextRoom.points
            }
        }


        pusher.trigger('game-channel', 'update-world', {'updates': updated})


        # for p_uuid in currentPlayerUUIDs:
        #     pusher.trigger(f'p-channel-{p_uuid}', u'broadcast', {'message':f'{player.user.username} has walked {dirs[direction]}.'})
        # for p_uuid in nextPlayerUUIDs:
        #     pusher.trigger(f'p-channel-{p_uuid}', u'broadcast', {'message':f'{player.user.username} has entered from the {reverse_dirs[direction]}.'})
        return JsonResponse({'name':player.user.username, 'title':nextRoom.title, 'description':nextRoom.description, 'players':players, 'error_msg':""}, safe=True)
    else:
        players = room.playerNames(player_id)
        return JsonResponse({'name':player.user.username, 'title':room.title, 'description':room.description, 'players':players, 'error_msg':"You cannot move that way."}, safe=True)

@api_view(["GET"])
def details(request):
    player = request.user.player
    player_id = player.id
    room = player.room()
    players = room.playerNames(player_id)
    return JsonResponse({'name':player.user.username, 'title':room.title, 'description':room.description, 'players':players, 'points':room.points}, safe=True)

@csrf_exempt
@api_view(["POST"])
def say(request):
    # IMPLEMENT
    data = json.loads(request.body)
    text = data['message']
    user = request.user.username
    print(f"Data:\n{request}")
    time = {
        'hours': gmtime().tm_hour,
        'mins': gmtime().tm_min,
        'secs': gmtime().tm_sec
    }

    message = {
        'user': user,
        'time': time,
        'message': text
    }

    pusher.trigger('game-channel', 'new-message', message)
    return JsonResponse({'message': "Message received"}, safe=True, status=201)