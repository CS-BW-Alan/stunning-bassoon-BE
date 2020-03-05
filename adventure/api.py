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
from django.db import models
'''
Flow of game initialization:
PLAN A:
1) Someone hits `/start` endpoint and creates world map from blueprint
2) Anyone hits `/get_game` endpoint and get a copy of the blueprint
3) Anyone hits `/join_game` endpoint and associates their user with a new player who is dropped in starting room

PLAN B:
1) User joins, but doesn't have a player yet ??? and there is no game baord ??? maybe in chatroom
2) once all users join, game board and players are all created and placed in starting rooms

'''
# instantiate pusher
pusher = Pusher(app_id=config('PUSHER_APP_ID'), key=config('PUSHER_KEY'), secret=config('PUSHER_SECRET'), cluster=config('PUSHER_CLUSTER'))

# hard code blueprint to start game
blueprint = [
    [0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1],
    [0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1],
    [0, 1, 1, 0, 1, 1, 1, 1, 0, 0, 1, 1],
    [0, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1],
    [1, 1, 0, 1, 1, 0, 0, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1],
    [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1],
    [0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1],
    [0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1]
]

world_map = []

@csrf_exempt

@api_view(["GET"])
def startGame(request):
    global world_map 
    world_map = World.create_rooms(blueprint)
    return JsonResponse({'message': 'World creaated', 'blueprint':blueprint}, safe=True)

@api_view(["GET"])
def getGame(request):
    return JsonResponse({'message': 'Welcome to the game', 'blueprint':blueprint}, safe=True)

# deprecated 
# @api_view(["GET"])
# def initialize(request):
#     user = request.user
#     player = user.player
#     player_id = player.id
#     uuid = player.uuid
#     room = player.room()
#     players = room.playerNames(player_id)
#     return JsonResponse({'uuid': uuid, 'name':player.user.username, 'title':room.title, 'description':room.description, 'players':players, 'blueprint':blueprint}, safe=True)

@api_view(["GET"])
def joinGame(request):
    user = request.user
    try:
        oldPlayer = user.player
        user.player = None
        oldPlayer.delete()
    except Player.DoesNotExist:
        pass
    newPlayer = Player()
    #user.player = newPlayer <- this line seems to do the same as below
    newPlayer.user = user
    newPlayer.save()
    # add logic: player drops in room
    return JsonResponse({'Msg':"Join Successful"}, safe=True)

@api_view(["GET"])
def leaveGame(request):
    user = request.user
    try:
        oldPlayer = user.player
        user.player = None
        oldPlayer.delete()
    except Player.DoesNotExist:
        return JsonResponse({'error_msg':"Player has already left."}, safe=True)
    return JsonResponse({'Msg':"Leave Successful"}, safe=True)

import random
def rollDie():
    return random.randint(1,6)

@api_view(["GET"])
def roll(request):
    try:
        player = request.user.player
        player.moves = rollDie()
        player.save()
        return JsonResponse({'Roll':player.moves}, safe=True)
    except Player.DoesNotExist:
        return JsonResponse({'error_msg':"User needs to join game to roll."}, safe=True)

# @csrf_exempt
@api_view(["POST"])
def move(request):
    dirs={"w": "north", "s": "south", "d": "east", "a": "west"}
    reverse_dirs = {"n": "south", "s": "north", "e": "west", "w": "east"}
    player = request.user.player
    if player.moves > 0:
        player_id = player.id
        player_uuid = player.uuid
        data = json.loads(request.body)
        direction = data['direction']
        room = player.room()
        nextRoomID = None
        if direction == "w":
            nextRoomID = room.n_to
        elif direction == "s":
            nextRoomID = room.s_to
        elif direction == "d":
            nextRoomID = room.e_to
        elif direction == "a":
            nextRoomID = room.w_to
        if nextRoomID is not None and nextRoomID > 0:
            nextRoom = Room.objects.get(id=nextRoomID)
            player.currentRoom=nextRoomID
            player.moves -= 1
            if player.moves == 0:
                room = player.room()
                player.points += room.points
                room.points = 0
                room.save()
            player.save()
            players = nextRoom.playerNames(player_id)
            currentPlayerUUIDs = room.playerUUIDs(player_id)
            nextPlayerUUIDs = nextRoom.playerUUIDs(player_id)
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
            return JsonResponse({'name':player.user.username, 'player_points':player.points, 'title':nextRoom.title, 'description':nextRoom.description, 'players':players, 'error_msg':"", 'room_points':room.points}, safe=True)
        else:
            players = room.playerNames(player_id)
            return JsonResponse({'error_msg':"You cannot move that way."}, safe=True)
    else:
        return JsonResponse({'error_msg':"Player has no moves left."}, safe=True)

@api_view(["GET"])
def details(request):
    player = request.user.player
    player_id = player.id
    room = player.room()
    players = room.playerNames(player_id)
    return JsonResponse({'name':player.user.username, 'room_title':room.title, 'description':room.description, 'players':players, 'player_points':player.points, 'room_points':room.points, 'moves': player.moves}, safe=True)

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