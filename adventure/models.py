from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
from rest_framework.authtoken.models import Token
import uuid
import random


def randomint():
    return random.randint(1,10) * 10

class Room(models.Model):
    title = models.CharField(max_length=50, default="An open space")
    description = models.CharField(max_length=500, default="You can travel freely through this space")
    room_id = models.IntegerField(default=0)
    x_coord = models.IntegerField(default=0)
    y_coord = models.IntegerField(default=0)
    n_to = models.IntegerField(default=0)
    s_to = models.IntegerField(default=0)
    e_to = models.IntegerField(default=0)
    w_to = models.IntegerField(default=0)
    points = models.IntegerField(default=randomint)
    game = models.OneToOneField(Game, on_delete=models.CASCADE)

    def connectRooms(self, destinationRoom, direction):
        destinationRoomID = destinationRoom.id
        try:
            destinationRoom = Room.objects.get(id=destinationRoomID)
        except Room.DoesNotExist:
            print("That room does not exist")
        else:
            if direction == "n":
                self.n_to = destinationRoomID
            elif direction == "s":
                self.s_to = destinationRoomID
            elif direction == "e":
                self.e_to = destinationRoomID
            elif direction == "w":
                self.w_to = destinationRoomID
            else:
                print("Invalid direction")
                return
            self.save()
    def playerNames(self, currentPlayerID):
        return [p.user.username for p in Player.objects.filter(currentRoom=self.id) if p.id != int(currentPlayerID)]
    def playerUUIDs(self, currentPlayerID):
        return [p.uuid for p in Player.objects.filter(currentRoom=self.id) if p.id != int(currentPlayerID)]


class Player(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    currentRoom = models.IntegerField(default=0)
    uuid = models.UUIDField(default=uuid.uuid4, unique=True)
    moves = models.IntegerField(default=0)
    points = models.IntegerField(default=0)
    game = models.OneToOneField(Game, on_delete=models.CASCADE)
    queueNumber = models.IntegerField(default=0)

    def initialize(self):
        if self.currentRoom == 0:
            self.currentRoom = Room.objects.first().id
            self.save()
    def room(self):
        try:
            return Room.objects.get(id=self.currentRoom)
        except Room.DoesNotExist:
            self.initialize()
            return self.room()

class Queue(models.Model):
    game = models.OneToOneField(Game, on_delete=models.CASCADE)
    player = models.OneToOneField(Player, on_delete=models.CASCADE)
    number = models.IntegerField(default=0)

    def get(self):
        next_player = Queue.objects.filter(game=self.game).filter(number=0)
        # next_player.number = 


class Game(models.Model):
    pointsRemaining = models.IntegerField(default=0)
    inSession = models.BooleanField(default=False)

    # TODO:
    # - Add game to Room, along with everywhere room is instatiated (eg map_generator.py)
    # - Make multiple pusher channels: universal, and individiual game

    def initialize(self):
        self.inSession = True

    def join(self, player):
        player.game = self.id
        queue = Queue.objects.filter(game=self.id)
        queue.put(player)

    def getPoints(self, player, room):
        points = room.points
        room.points = 0
        player.points += points
        self.pointsRemaining -= points
        
        # Check for endgame:
        if self.pointsRemaining == 0:
            pusher = Pusher(app_id=config('PUSHER_APP_ID'), key=config('PUSHER_KEY'), secret=config('PUSHER_SECRET'), cluster=config('PUSHER_CLUSTER'))
            self.inSession = False
            pusher.trigger('game-channel', 'endgame', {'winner': player})
    
    def runGame(self):
        # queue = Queue()
        winner = None

        # Add players to queue
        for player in Player.objects.filter(game=self.id):
            # queue.put(player)
        
        # Main loop
        while winner == None:




@receiver(post_save, sender=User)
def create_user_player(sender, instance, created, **kwargs):
    if created:
        Player.objects.create(user=instance)
        Token.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_user_player(sender, instance, **kwargs):
    instance.player.save()





