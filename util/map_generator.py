from adventure.models import Room, Player


class World:
    # def __init__(self, blueprint):
    #     self.blueprint = blueprint # blueprint must be a list of lists. Sublists must have same length
    #     self.width = len(blueprint[0]) # width is equal to the # of items in a sublist
    #     self.height = len(blueprint) # height is equal to the number of lists
    @staticmethod
    def create_rooms(blueprint):
        # clear out any rooms in the database
        Room.objects.all().delete()

        # 0's represent obstacles, 1's represent freely traversable rooms
        # below passed in as parameter instead of hardcoded
        # blueprint = [
        #     [0, 0, 0, 0, 1, 1, 0, 1, 0, 0, 1, 1],
        #     [0, 0, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1],
        #     [0, 1, 1, 0, 1, 1, 1, 1, 0, 0, 1, 1],
        #     [0, 1, 0, 0, 1, 1, 1, 1, 0, 0, 1, 1],
        #     [1, 1, 0, 1, 1, 0, 0, 1, 1, 1, 1, 1],
        #     [1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1],
        #     [1, 1, 1, 1, 0, 0, 0, 1, 1, 1, 1, 1],
        #     [1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1, 1],
        #     [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1],
        #     [1, 1, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1],
        #     [0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1],
        #     [0, 0, 1, 1, 1, 1, 1, 1, 0, 0, 1, 1]
        # ]

        world_map = [[None for j in range(len(blueprint[0]))] for i in range(len(blueprint))]


        # Loop over the grid, create rooms, record coordinates
        room_id = 1
        for i in range(0, len(blueprint)):
            for j in range(0, len(blueprint[0])):
                if blueprint[i][j] == 1:
                    world_map[i][j] = Room(x_coord=j, y_coord=i)
                    world_map[i][j].save()
                    room_id =+ 1
        #print("World generation complete")
        
        # Loop over the grid again, create room connections, record coordinates
        # go from room to room and check if adjacent room in world_map is != None
        # if != None, add an appropriate directional connection
        # lots of edge cases to riddle through

        # methods to uncomment and copy paste into generation loops
        # could probably reduce into function on second pass
        # north:
        if world_map[i - 1][j]:
            world_map[i][j].connectRooms(world_map[i - 1][j], "n")
            #print("north connect")

        # # south:
        # if world_map[i + 1][j]:
        #     world_map[i][j].connectRooms(world_map[i + 1][j], "s")
        #     print("south connect")

        # # east:
        # if world_map[i][j + 1]:
        #     world_map[i][j].connectRooms(world_map[i][j + 1], "e")
        #     print("east connect")

        # # west:
        # if world_map[i][j - 1]:
        #     world_map[i][j].connectRooms(world_map[i][j - 1], "w")
        #     print("west connect")

        for i in range(0, len(blueprint)):
            # Rules for first row (no north)
            if i == 0:
                for j in range(0, len(blueprint[0])):
                    # Rules for first column (no west)
                    if j == 0 and world_map[i][j] != None:
                        #print(f"room connect; i = {i}; j = {j}")
                        # Generate south and east connections
                        # south:
                        if world_map[i + 1][j]:
                            world_map[i][j].connectRooms(world_map[i + 1][j], "s")
                            #print("south connect")

                        # east:
                        if world_map[i][j + 1]:
                            world_map[i][j].connectRooms(world_map[i][j + 1], "e")
                            #print("east connect")
    
                    # Rules for middles columns (west and east)
                    elif j > 0 and j < len(blueprint) - 1 and world_map[i][j] != None: 
                        # Generate south, east, and west connections
                        #print(f"room connect; i = {i}; j = {j}")
                        # south:
                        if world_map[i + 1][j]:
                            world_map[i][j].connectRooms(world_map[i + 1][j], "s")
                            #print("south connect")

                        # east:
                        if world_map[i][j + 1]:
                            world_map[i][j].connectRooms(world_map[i][j + 1], "e")
                            #print("east connect")

                        # west:
                        if world_map[i][j - 1]:
                            world_map[i][j].connectRooms(world_map[i][j - 1], "w")
                            #print("west connect")

                    # Rules for last columns (no east)
                    elif j == len(blueprint) - 1 and world_map[i][j] != None: 
                        # Generate south and west connections
                        #print(f"room connect; i = {i}; j = {j}")
                        # south:
                        if world_map[i + 1][j]:
                            world_map[i][j].connectRooms(world_map[i + 1][j], "s")
                            #print("south connect")

                        # west:
                        if world_map[i][j - 1]:
                            world_map[i][j].connectRooms(world_map[i][j - 1], "w")
                            #print("west connect")

                    else:
                        #print(f"No room at; i = {i}; j = {j}")
                        pass

            # Rules for middle rows (north and south)
            elif i > 0 and i < len(blueprint) - 1:
                for j in range(0, len(blueprint[0])):
                    # Rules for first column (no west)
                    if j == 0 and world_map[i][j] != None:
                        # Generate north, south, and east connections
                        #print(f"room connect; i = {i}; j = {j}")
                        # north:
                        if world_map[i - 1][j]:
                            world_map[i][j].connectRooms(world_map[i - 1][j], "n")
                            #print("north connect")

                        # south:
                        if world_map[i + 1][j]:
                            world_map[i][j].connectRooms(world_map[i + 1][j], "s")
                            #print("south connect")

                        # east:
                        if world_map[i][j + 1]:
                            world_map[i][j].connectRooms(world_map[i][j + 1], "e")
                            #print("east connect")
                    

                    # Rules for middles columns (west and east)
                    elif j > 0 and j < len(blueprint) - 1 and world_map[i][j] != None: 
                        # Generate north, south, east, and west connections
                        #print(f"room connect; i = {i}; j = {j}")
                        # north:
                        if world_map[i - 1][j]:
                            world_map[i][j].connectRooms(world_map[i - 1][j], "n")
                            #print("north connect")

                        # south:
                        if world_map[i + 1][j]:
                            world_map[i][j].connectRooms(world_map[i + 1][j], "s")
                            #print("south connect")

                        # east:
                        if world_map[i][j + 1]:
                            world_map[i][j].connectRooms(world_map[i][j + 1], "e")
                            #print("east connect")

                        # west:
                        if world_map[i][j - 1]:
                            world_map[i][j].connectRooms(world_map[i][j - 1], "w")
                            #print("west connect")

                    
                    # Rules for last columns (no east)
                    elif j == len(blueprint) - 1 and world_map[i][j] != None: 
                        # Generate north, south, and west connections
                        #print(f"room connect; i = {i}; j = {j}")
                        # north:
                        if world_map[i - 1][j]:
                            world_map[i][j].connectRooms(world_map[i - 1][j], "n")
                            #print("north connect")

                        # south:
                        if world_map[i + 1][j]:
                            world_map[i][j].connectRooms(world_map[i + 1][j], "s")
                            #print("south connect")

                        # west:
                        if world_map[i][j - 1]:
                            world_map[i][j].connectRooms(world_map[i][j - 1], "w")
                            #print("west connect")

                    else:
                        pass
                        #print(f"No room at; i = {i}; j = {j}")

            # Rules for final row (no south)
            elif i == len(blueprint) - 1: 
                for j in range(0, len(blueprint[0])):
                    # Rules for first column (no west)
                    if j == 0 and world_map[i][j] != None:
                        # Generate north and east connections
                        #print(f"room connect; i = {i}; j = {j}")
                        # north:
                        if world_map[i - 1][j]:
                            world_map[i][j].connectRooms(world_map[i - 1][j], "n")
                            #print("north connect")

                        # east:
                        if world_map[i][j + 1]:
                            world_map[i][j].connectRooms(world_map[i][j + 1], "e")
                            #print("east connect")
                    
                    # Rules for middles columns (west and east)
                    elif j > 0 and j < len(blueprint) - 1 and world_map[i][j] != None: 
                        # Generate north, east, and west connections
                        #print(f"room connect; i = {i}; j = {j}")
                        # north:
                        if world_map[i - 1][j]:
                            world_map[i][j].connectRooms(world_map[i - 1][j], "n")
                            #print("north connect") 

                        # east:
                        if world_map[i][j + 1]:
                            world_map[i][j].connectRooms(world_map[i][j + 1], "e")
                            #print("east connect")

                        # west:
                        if world_map[i][j - 1]:
                            world_map[i][j].connectRooms(world_map[i][j - 1], "w")
                            #print("west connect")

                    
                    # Rules for last columns (no east)
                    elif j == len(blueprint) - 1 and world_map[i][j] != None: 
                        # Generate north and west connections
                        #print(f"room connect; i = {i}; j = {j}")
                        # north:
                        if world_map[i - 1][j]:
                            world_map[i][j].connectRooms(world_map[i - 1][j], "n")
                            #print("north connect")

                        # west:
                        if world_map[i][j - 1]:
                            world_map[i][j].connectRooms(world_map[i][j - 1], "w")
                            #print("west connect")

                    else:
                        #print(f"No room at; i = {i}; j = {j}")
                        pass
        print("World creation complete")
        players=Player.objects.all()
        rooms = Room.objects.all()
        interval = len(rooms)//len(players)
        counter = 0
        for p in players:
            p.currentRoom= rooms[counter].id
            counter += interval
            p.save()
        print("Players rooms set")