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

current_player = None
player_count = 0
playerNames = []
roomCount = None
colors = ['red', 'blue', 'green', 'yellow', 'purple', 'orange', 'black', 'white', 'gray', 'magenta', 'cyan', 'brown']
available_colors = list(reversed(colors))

def initRoomCount():
    global roomCount
    roomCount = len(Room.objects.all())

# @csrf_exempt
@api_view(["GET"])
def startGame(request):
    global current_player
    playerCount = len(Player.objects.all())
    if current_player == None and playerCount > 0:
        World.create_rooms(blueprint)
        initRoomCount()
        global playerNames
        playerNames = [p.user.username for p in Player.objects.all()]
        current_player = Player.objects.all()[0].user.username
        global player_count
        player_count = len(playerNames)

        player_dict = {
            "current_player": current_player,
            "players": [{
                # "player_id": p.id,
                # "username": p.user.username,
                # "score": p.points,
                # "current_room": p.currentRoom,
                "player_id": p.id,
                "username": p.user.username,
                "points": p.points,
                "current_room": p.currentRoom,
                "isTurn": p.user.username == current_player,
                "movePoints": p.moves
            } for p in Player.objects.all()]
        }

        board = [{
                    "room_id": r.id,
                    "x_coord": r.x_coord,
                    "y_coord": r.y_coord,
                    "players": [{'id': p.id, 'color': p.color} for p in Player.objects.filter(currentRoom=r.id)],
                    "point_value": r.points
                } for r in Room.objects.all()]

        pusher.trigger('player-channel', 'start-game', player_dict)
        pusher.trigger('board-channel', 'start-game', board)
        return JsonResponse({'message': 'World created', 'blueprint':blueprint}, safe=True)
    else:
        return JsonResponse({'message': 'Game was started by another player or no players have joined for a game to be started.'}, safe=True)

@api_view(["GET"])
def getGame(request):
    board = [{
                "room_id": r.id,
                "x_coord": r.x_coord,
                "y_coord": r.y_coord,
                "players": [{'id': p.id, 'color': p.color} for p in Player.objects.filter(currentRoom=r.id)],
                "point_value": r.points
            } for r in Room.objects.all()]
    players = [{
        "player_id": p.id,
        "username": p.user.username,
        "points": p.points,
        "current_room": p.currentRoom,
        "isTurn": p.user.username == current_player,
        "movePoints": p.moves
    } for p in Player.objects.all()]
    return JsonResponse({'message': 'Welcome to the game', 'blueprint':blueprint, 'board':board, 'players':players}, safe=True)

@api_view(["GET"])
def getPlayers(request):
    return JsonResponse({'message': 'Here are the players', 'players':[p.user.username for p in Player.objects.all()]}, safe=True)

@api_view(["GET"])
def endGame(request):
    global current_player
    global available_colors
    current_player = None
    players = Player.objects.all()
    rooms = Room.objects.all()
    for p in players:
        available_colors.append(p.color)
    if len(players) > 0:
        players.delete()
    if len(rooms) > 0:
        rooms.delete()
    return JsonResponse({'message': "All Rooms & Players Are Removed"}, safe=True)

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

    global available_colors
    if len(available_colors):
        newPlayer.color = available_colors.pop()
        newPlayer.save()
    else:
        return JsonResponse({'Msg':"Cannot join game. Maximum number of players."}, safe=True, status=500)


    # add logic: player drops in room

    # Pusher
    # Updated player list to pass through pusher
    players = [{
        # "player_id": p.id,
        # "username": p.user.username,
        # "score": p.points,
        # "current_room": p.currentRoom,
        "player_id": p.id,
        "username": p.user.username,
        "points": p.points,
        "current_room": p.currentRoom,
        "isTurn": p.user.username == current_player,
        "movePoints": p.moves,
        "color": p.color
    } for p in Player.objects.all()]
    # Trigger player-joined event and pass in updated players list
    pusher.trigger('player-channel', 'player-joined', {'message': f"{request.user.username} has joined the game", 'player': user.username, 'players': players})
    
    return JsonResponse({'Msg':"Join Successful", 'player_id': newPlayer.id, 'Name': user.username}, safe=True)

@api_view(["GET"])
def leaveGame(request):
    user = request.user
    global available_colors
    try:
        oldPlayer = user.player
        available_colors.append(oldPlayer.color)
        user.player = None
        oldPlayer.delete()
    except Player.DoesNotExist:
        return JsonResponse({'error_msg':"Player has already left."}, safe=True)

    

    # Pusher
    # Updated player list to pass through pusher
    players = [{
        # "player_id": p.id,
        # "username": p.user.username,
        # "score": p.points,
        # "current_room": p.currentRoom,
        "player_id": p.id,
        "username": p.user.username,
        "points": p.points,
        "current_room": p.currentRoom,
        "isTurn": p.user.username == current_player,
        "movePoints": p.moves,
        "color": p.color
    } for p in Player.objects.all()]
    # Trigger player-left event and pass in updated players list
    pusher.trigger('player-channel', 'player-left', {'message': f"{request.user.username} has left the game", 'player': user.username, 'players': players})

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
    #print(player.user.username)
    global current_player
    #print(current_player)
    global player_count
    global playerNames
    global roomCount
    if player.moves > 0 and player.user.username == current_player:
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
            pusher.trigger('player-channel', 'player-moves-update', player.moves)

            if room.points != 0:
                roomCount -= 1
            # Player will take points from each room moved to.
            room = player.room()
            player.points += room.points
            pusher.trigger('player-channel', 'player-points-update', player.points)
            room.points = 0
            room.save()
            # Logic to switch player turns
            if player.moves == 0:
                player_index = playerNames.index(current_player)
                player_index += 1
                if player_index >= player_count:
                    current_player = playerNames[0]
                else:
                    current_player = playerNames[player_index]
            player.save()
            playersNames = nextRoom.playerNames(player_id)
            currentPlayerUUIDs = room.playerUUIDs(player_id)
            nextPlayerUUIDs = nextRoom.playerUUIDs(player_id)
            # updated = {
            #     "current_player": current_player,
            #     "player": {
            #         "player_id": player.id,
            #         "username": player.user.username,
            #         "points": player.points,
            #         "current_room": player.currentRoom,
            #         "isTurn": player.user.username == current_player,
            #         "movePoints": player.moves
            #     },
            #     "oldRoom": {
            #         "room_id": room.id,
            #         "players": [p.id for p in Player.objects.filter(currentRoom=room.id)],
            #         "points": room.points
            #     },
            #     "newRoom": {
            #         "room_id": nextRoom.id,
            #         "players": [p.id for p in Player.objects.filter(currentRoom=nextRoom.id)],
            #         "points": nextRoom.points
            #     }
            # }

            player_updates = {
                "current_player": current_player,
                "player": {
                    "player_id": player.id,
                    "username": player.user.username,
                    "points": player.points,
                    "current_room": player.currentRoom,
                    "isTurn": player.user.username == current_player,
                    "movePoints": player.moves,
                    "color": player.color
                }
            }
            # board_updates = {
            #     "oldRoom": {
            #         "room_id": room.id,
            #         "players": [{'id': p.id, 'color': p.color} for p in Player.objects.filter(currentRoom=room.id)],
            #         "points": room.points
            #     },
            #     "newRoom": {
            #         "room_id": nextRoom.id,
            #         "players": [{'id': p.id, 'color': p.color} for p in Player.objects.filter(currentRoom=nextRoom.id)],
            #         "points": nextRoom.points
            #     }
            # }
            board = [{
                "room_id": r.id,
                "x_coord": r.x_coord,
                "y_coord": r.y_coord,
                "players": [{'id': p.id, 'color': p.color} for p in Player.objects.filter(currentRoom=r.id)],
                "point_value": r.points
            } for r in Room.objects.all()]

            # END GAME
            if roomCount <= 0:
                # Find Winner
                players = Player.objects.all()
                winner = players[0]
                for p in players[1:]:
                    if p.points > winner.points:
                        winner = p
                # Alert players of winner
                pusher.trigger('board-channel', 'end-game', {'winner': winner.user.username})
                # Give normal updates
                pusher.trigger('board-channel', 'update-world', board)
                pusher.trigger('player-channel', 'update-world', player_updates)
                # Delete players
                if len(players) > 0:
                    for p in players:
                        available_colors.append(players.color)
                    players.delete()
                Room.objects.all().delete()
                current_player = None
            # The game continues...
            else:                
                pusher.trigger('board-channel', 'update-world', board)
                pusher.trigger('player-channel', 'update-world', player_updates)



            # for p_uuid in currentPlayerUUIDs:
            #     pusher.trigger(f'p-channel-{p_uuid}', u'broadcast', {'message':f'{player.user.username} has walked {dirs[direction]}.'})
            # for p_uuid in nextPlayerUUIDs:
            #     pusher.trigger(f'p-channel-{p_uuid}', u'broadcast', {'message':f'{player.user.username} has entered from the {reverse_dirs[direction]}.'})
            return JsonResponse({'name':player.user.username, 'player_points':player.points, 'x_coord':nextRoom.x_coord, 'y_coord':nextRoom.y_coord, 'players':playersNames, 'error_msg':"", 'room_points':room.points}, safe=True)
        else:
            playersNames = room.playerNames(player_id)
            return JsonResponse({'error_msg':"You cannot move that way."}, safe=True)
    else:
        return JsonResponse({'error_msg':"Player has no moves left. It may not be your turn or you have not rolled yet."}, safe=True)

@api_view(["GET"])
def details(request):
    player = request.user.player
    player_id = player.id
    room = player.room()
    playersNames = room.playerNames(player_id)
    return JsonResponse({'name':player.user.username, 'room_title':room.title, 'description':room.description, 'players':playersNames, 'player_points':player.points, 'room_points':room.points, 'moves': player.moves}, safe=True)

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

    pusher.trigger('chat-channel', 'new-message', message)
    return JsonResponse({'message': "Message received"}, safe=True, status=201)