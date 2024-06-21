import numpy as np
import random
import json
import time

CubeWidth = 3
FaceFront = "F"
FaceTop = "T"
FaceRight = "R"
FaceDown = "D"
FaceLeft = "L"
FaceBack = "B"
Faces = [FaceFront, FaceTop, FaceRight, FaceDown, FaceLeft, FaceBack]

database_filename = './database_edgesB2.json'

PositionsCorners = [[0,0,0], [0,0,2], [0,2,0], [0,2,2], [2,0,0], [2,0,2], [2,2,0], [2,2,2]]
PositionsEdgeGroup1 = [[1,0,0], [0,1,0], [0,0,1], [1,0,2], [1,2,0], [2,1,0]]
PositionsEdgeGroup2 = [[1,2,2], [2,1,2], [2,2,1], [0,1,2], [0,2,1], [2,0,1]]
PositionsAll = PositionsCorners + PositionsEdgeGroup1 + PositionsEdgeGroup2

MoveCountCorners = {}
MoveCountEdgeGroup1 = {}
MoveCountEdgeGroup2 = {}

# Counts the number of 1s in the position array of a cubie
# Used to determine which type of cubie it is
def center_count(indexes):
    count = 0
    for index in indexes:
        if index == 1:
            count += 1
    return count

class Cubie:
    def __init__(self):
        self.ID = 0
        self.Rotation = [0, 0, 0]
        self.IsCorner = False

class CubeGrid:
    def __init__(self):
        self.grid = np.empty((3, 3, 3), dtype=object)
    
    def __getitem__(self, index):
        return self.grid[index]
    
    def __setitem__(self, index, value):
        self.grid[index] = value
        
# Create a new cube in its solved, initial state    
def new_cube():
    grid = new_cube_grid()
    return Cube(grid)

# Clone a cube, keeping the state of the cubie grid intact
def clone_cube(cube):
    return Cube(clone_cube_grid(cube.Grid))

# Create a grid for the cubie
# Grid holds the positions of the cubies
def new_cube_grid():
    cubeGrid = CubeGrid()
    cubieID = 0
    for zIndex in range(CubeWidth):
        #plane = cubeGrid[planeIndex]
        for yIndex in range(CubeWidth):
            for xIndex in range(CubeWidth):
                cubie = Cubie()
                cubie.ID = cubieID
                cubie.Rotation = [0, 0, 0]
                centerCount = center_count([zIndex, yIndex, xIndex])
                if centerCount > 1:
                    continue
                if centerCount == 0:
                    cubie.IsCorner = True
                cubeGrid[zIndex][yIndex][xIndex] = cubie
                cubieID += 1
    return cubeGrid

# Clone a cube grid, for use when cloning a cube
def clone_cube_grid(cubeGrid):
    nextCubeGrid = CubeGrid()
    for zIndex in range(CubeWidth):
        #plane = cubeGrid[planeIndex]
        for yIndex in range(CubeWidth):
            for xIndex in range(CubeWidth):
                cubie = cubeGrid[zIndex][yIndex][xIndex]
                if cubie is None:
                    continue
                nextCubie = Cubie()
                nextCubie.ID = cubie.ID
                nextCubie.Rotation = cubie.Rotation.copy()
                nextCubie.IsCorner = cubie.IsCorner
                nextCubeGrid[zIndex][yIndex][xIndex] = nextCubie
    return nextCubeGrid

# Class for the cube itself
# Has a grid of cubies, and functions to rotate them
# Additionally has function to encode its state
class Cube:
    def __init__(self, grid):
        if grid is None:
            self.Grid = new_cube_grid()
        else:
            self.Grid = grid
    
    # Turn the selected face clockwise
    def rotate(self, face):
        plane = np.empty((3, 3), dtype=object)
        rotatedPlane = np.empty((3, 3), dtype=object)
        if face == FaceFront:
            for xIndex in range(CubeWidth):
                for yIndex in range(CubeWidth):
                    plane[yIndex][xIndex] = self.Grid[0][yIndex][xIndex]
            rotatedPlane = rotate_plane(plane, 2, True)
            for xIndex in range(CubeWidth):
                for yIndex in range(CubeWidth):
                    self.Grid[0][yIndex][xIndex] = rotatedPlane[yIndex][xIndex]
        elif face == FaceBack:
            for xIndex in range(CubeWidth):
                for yIndex in range(CubeWidth):
                    plane[yIndex][xIndex] = self.Grid[2][yIndex][xIndex]
            rotatedPlane = rotate_plane(plane, 2, False)
            for xIndex in range(CubeWidth):
                for yIndex in range(CubeWidth):
                    self.Grid[2][yIndex][xIndex] = rotatedPlane[yIndex][xIndex]
        elif face == FaceTop:
            for xIndex in range(CubeWidth):
                for zIndex in range(CubeWidth):
                    plane[zIndex][xIndex] = self.Grid[zIndex][0][xIndex]
            rotatedPlane = rotate_plane(plane, 1, False)
            for xIndex in range(CubeWidth):
                for zIndex in range(CubeWidth):
                    self.Grid[zIndex][0][xIndex] = rotatedPlane[zIndex][xIndex]
        elif face == FaceDown:
            for xIndex in range(CubeWidth):
                for zIndex in range(CubeWidth):
                    plane[zIndex][xIndex] = self.Grid[zIndex][2][xIndex]
            rotatedPlane = rotate_plane(plane, 1, True)
            for xIndex in range(CubeWidth):
                for zIndex in range(CubeWidth):
                    self.Grid[zIndex][2][xIndex] = rotatedPlane[zIndex][xIndex]
        elif face == FaceLeft:
            for yIndex in range(CubeWidth):
                for zIndex in range(CubeWidth):
                    plane[zIndex][yIndex] = self.Grid[zIndex][yIndex][0]
            rotatedPlane = rotate_plane(plane, 0, True)
            for yIndex in range(CubeWidth):
                for zIndex in range(CubeWidth):
                    self.Grid[zIndex][yIndex][0] = rotatedPlane[zIndex][yIndex]
        elif face == FaceRight:
            for yIndex in range(CubeWidth):
                for zIndex in range(CubeWidth):
                    plane[zIndex][yIndex] = self.Grid[zIndex][yIndex][2]
            rotatedPlane = rotate_plane(plane, 0, False)
            for yIndex in range(CubeWidth):
                for zIndex in range(CubeWidth):
                    self.Grid[zIndex][yIndex][2] = rotatedPlane[zIndex][yIndex]
    
    # Shuffle the cube, making a random move X times
    def shuffle(self, shuffles=10):
        movestring = ''
        for x in range(shuffles):
            move = random.randint(0,5)
            if (move == 0):
                movestring += 'F'
            elif (move == 1):
                movestring += 'T'
            elif (move == 2):
                movestring += 'R'
            elif (move == 3):
                movestring += 'D'
            elif (move == 4):
                movestring += 'L'
            else:
                movestring += 'B'
        
        # Once the string is built, execute the random moves
        perform_moves(self, movestring)
        
    # Returns an list of encoded strings for the chosen position group
    # Position groups are: Corners, EdgeA and EdgeB
    def encode_state(self, positions = PositionsAll, rotations = True):
        # Represents the positions of the grid
        state = ''
        
        # For each cubie in the chosen position group, build a string representing its state, and append it to state
        for position in positions:
            cubie = self.Grid[position[0], position[1], position[2]]
            if rotations:
                state += f'{cubie.ID:02d}{int(cubie.Rotation[0] / 90)}{int(cubie.Rotation[1] / 90)}{int(cubie.Rotation[2] / 90)}'
            else:
                state += f'{cubie.ID:02d}'
        
        # Return the concatenated encoding
        return state
    
    # Print information about the cube's state
    # Displays in the form:
    # Back Face
    # Middle Layer
    # Front Face
    def string(self):
        workingString = "\n"

        for planeIndex in range(2, -1, -1):
            plane = self.Grid[planeIndex]
            
            for rowIndex, row in enumerate(plane):
                for cellIndex, cubie in enumerate(row):
                    if cubie is None:
                        workingString += " ______ "
    
                        if cellIndex == 2:
                            workingString += "\n"
                        
                        continue
    
                    workingString += f" {cubie.ID:02d}.{int(cubie.Rotation[0] / 90)}{int(cubie.Rotation[1] / 90)}{int(cubie.Rotation[2] / 90)} "
    
                    if cellIndex == 2:
                        workingString += "\n"
    
                if rowIndex == 2:
                    workingString += "\n"
    
        return workingString

# Handles the 90 degree rotations that occur to faces when they get rotated
def rotate_plane(plane, axis, clockwise):
    nextPlane = np.empty((3, 3), dtype=object)
    for rowIndex in range(CubeWidth):
        row = plane[rowIndex]
        row = row[::-1]
        for columnIndex in range(CubeWidth):
            cubie = row[columnIndex]
            if cubie is None:
                continue
            nextCubie = Cubie()
            nextCubie.ID = cubie.ID
            nextCubie.Rotation = cubie.Rotation
            nextCubie.Rotation[axis] = (nextCubie.Rotation[axis] + 90) %360
            if clockwise:
                nextPlane[(CubeWidth-1)-columnIndex][(CubeWidth-1)-rowIndex] = nextCubie
            else:
                nextPlane[columnIndex][rowIndex] = nextCubie
    
    return nextPlane

# Performs a series of rotations by string input
# Valid characters to move are: FTRDLB
def perform_moves(cube, movement_string, clockwise = True):
    for x in range(len(movement_string)):
        Face = movement_string[x]
        if clockwise == True:
            cube.rotate(Face)
        else:
            cube.rotate(Face)  
            cube.rotate(Face)  
            cube.rotate(Face)  

# Builds our database json files, for use during our search function
def build_heuristic_db(max_depth, filename, positions):
    heuristic = {}
    max_depth -= 1
        
    moves_list = ['']
    
    # Iterate through the ever-growing list, recording move counts
    for move in moves_list:
        if (len(move) > max_depth):
            break
        
        print("move:", move, len(move))
        # We make a new cube each time, and perform the moves to see what state we get
        cube = new_cube()
        perform_moves(cube, move)
        
        # Encode the state for more efficient DB storage
        encoding = cube.encode_state(positions)
        
        # Add result to dict
        if (encoding not in heuristic or (heuristic[encoding] > len(move))):
            heuristic[encoding] = len(move)  
        
        # Only add more entries if max depth hasn't been reached
        if (len(move) <= max_depth):
            for movetype in Faces:
                moves_list.append(move + movetype)    
    
    # Write to the heuristic db file
    with open(filename, 'w') as file:
        json.dump(heuristic, file, indent=2)

# Our backup heuristic, to bridge the gap to the database heuristic
# We reward the postion group for having more members in the correct spot,
# and also for having better rotations (closer to optimal)    
def get_heuristic(encode_string, correct_list):
    h = 12
    
    # Record list of current states
    compare_list = []
    rotations = []
    for x in range(0,len(correct_list)*5,5):
        compare_list.append(encode_string[x:x+2])
        rotations.append(encode_string[x+2:x+5])
        
    # Adds to heuristic depending on how perfect current rotations are
    # Perfect rotations are 000, worst are 111
    rot_total = 0
    for rot in rotations:
        for c in rot:
            c = int(c)
            if c == 0:
                c = 4
            rot_total += c
        
            
    h += 1-(rot_total/12)
        
    # Compare the current positions to the correct positions
    # For each non-correct, add 1 to heuristic
    for index in range(len(correct_list)):
        if compare_list[index] != correct_list[index]:
            h += 1
                        
    return(h)

# Depth-First search using our heuristic database + backup heuristic
def search(cube, movestring, depth, moveslist):
    depth -= 1
    
    # if not at max depth, search one move deeper
    if (depth > 0):
        for movetype in Faces:
            search(cube, movestring + movetype, depth, moveslist)

    # Make a copy of the cube that we can manipulate
    copied = clone_cube(cube)
    # Input the constructed string movement
    perform_moves(copied, movestring, clockwise = False)
        
    # Get encodings
    enc_corners = copied.encode_state(PositionsCorners)
    enc_edge1 = copied.encode_state(PositionsEdgeGroup1)
    enc_edge2 = copied.encode_state(PositionsEdgeGroup2)
    
    # Our combined heuristic value
    heuristic, heuristica, heuristicb, heuristicc = 0,0,0,0
        
    # For each position group, try to look up the database entry
    # If no database entry exists, use our backup heuristic
    if enc_corners in MoveCountCorners:
        heuristica = MoveCountCorners[enc_corners]  
    else:
        heuristica = get_heuristic(enc_corners, ['00', '02', '05', '07', '12', '14', '17', '19'])
    
    if enc_edge1 in MoveCountEdgeGroup1:
        heuristicb = MoveCountEdgeGroup1[enc_edge1]
    else:
        heuristicb = get_heuristic(enc_edge1, ['08', '03', '01', '09', '10', '15'])
        
    if enc_edge2 in MoveCountEdgeGroup2:
        heuristicc = MoveCountEdgeGroup2[enc_edge2]
    else:
        heuristicc = get_heuristic(enc_edge2, ['11', '16', '18', '04', '06', '13'])
    
    # Add up the position heuristics
    heuristic = heuristica + heuristicb + heuristicc              
    
    # Prunes out 4x repeats, removing them from the moveslist
    if (len(movestring) >= 4 and (movestring[0] == movestring[1] == movestring[2] == movestring[3])):
        movestring = movestring[4:]
    
    # Refuse to add empty moves to the moveslist, never letting the cube stay still
    if movestring != '': 
        moveslist.append((movestring, heuristic, (heuristica, heuristicb, heuristicc)))

# Key function for sorting during solve()
def sort_thing(move):
    return move[1]
    
def solve(cube):
    # Path is the path the cube takes during solving
    path = ''
    # The options the cube has when it decides to make a move
    moveslist = []
    # The last four moves, to prevent repeats
    lastmoves = ['', '', '', '']
    global MoveCountCorners
    global MoveCountEdgeGroup1
    global MoveCountEdgeGroup2
    
    # Load in our databases
    file = 'database_corners.json'
    with open(file, 'r') as file:
        MoveCountCorners = json.load(file)
    file = 'database_edgesA.json'
    with open(file, 'r') as file:
        MoveCountEdgeGroup1 = json.load(file)    
    file = 'database_edgesB.json'
    with open(file, 'r') as file:
        MoveCountEdgeGroup2 = json.load(file)
        
    # Min_val holds the current heuristic minimizing choice
    # Its a tuple: (Move, Heuristic)
    min_val = ('', 1000)    
    
    # Loop until heuristic is 0, representing a solved state
    while(min_val[1] > 0):
        min_val = ('', 1000)  

        # Call our search function for each possible move
        search(cube, '', 2, moveslist)
        
        #print("moveslist:", moveslist)
        
        moveslist.sort(key = sort_thing)
        min_val = moveslist[0]
                
        # Add move to lastmoves        
        lastmoves.pop(0)
        lastmoves.append(min_val[0])
        # If the last four moves are the same, make the 2nd best move
        if (lastmoves[0] == lastmoves[1] == lastmoves[2] == lastmoves[3]):
            min_val = moveslist[1]
            lastmoves.pop(0)
            lastmoves.append(min_val[0])
     
        # Perform the select move on our cube
        perform_moves(cube, min_val[0], clockwise = False)
        path += min_val[0]
        
        print("Last 4 moves:", lastmoves)
        print("Chosen move:", min_val[0])
        print("Current heuristic:", min_val[1])
        print()
        print(cube.string())
        
        # Delete the moveslist between each step
        moveslist = []
        time.sleep(0.5)
        
    return path




cube = new_cube()
perform_moves(cube, 'FTRLFLDBL')

print(cube.string())

'''cube.shuffle()
print(cube.string())

answer = solve(cube)
print(answer)
print(cube.string())'''









