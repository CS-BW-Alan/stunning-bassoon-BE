from adventure.models import Room

# 0's represent obstacles, 1's represent freely traversable rooms
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

world_map = [
    [None, None, None, None, None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None, None, None, None, None],
    [None, None, None, None, None, None, None, None, None, None, None, None],
]

class World:
    def __init__(self, blueprint):
        self.blueprint = blueprint # blueprint must be a list of lists. Sublists must have same length
        self.width = len(blueprint[0]) # width is equal to the # of items in a sublist
        self.height = len(blueprint) # height is equal to the number of lists
    def create_rooms():
        # clear out any rooms in the database
        Room.objects.all().delete()

        # Loop over the grid, create rooms, record coordinates
        room_id = 1
        for i in range(0, len(blueprint) - 1):
            for j in range(0, len(blueprint[0]) - 1):
                if blueprint[i][j] == 1:
                    world_map[i][j] = Room(room_id=room_id, x_coord=j, y_coord=i)
                    room_id =+ 1
        
        # Loop over the grid again, create room connections, record coordinates
        for i in range(0, len(blueprint) - 1):
            for j in range(0, len(blueprint[0]) - 1):
                # go from room to room and check if adjacent room in world_map is not None
                # if not None, add an appropriate directional connection
                # lots of edge cases to riddle through