#region VEXcode Generated Robot Configuration
import math
import random
from vexcode_vr import *

brain=Brain()
drivetrain = Drivetrain("drivetrain", 0)
pen = Pen("pen", 8)
pen.set_pen_width(THIN)
left_bumper = Bumper("leftBumper", 2)
right_bumper = Bumper("rightBumper", 3)
front_eye = EyeSensor("frontEye", 4)
down_eye = EyeSensor("downEye", 5)
front_distance = Distance("frontdistance", 6)
distance = front_distance
magnet = Electromagnet("magnet", 7)
location = Location("location", 9)
#endregion VEXcode Generated Robot Configuration

# Global variables to track robot's position and maze data
x, y, h = 0, 0, 0  # x and y coordinates, h is heading (0=North, 90=East, etc.)
visited = set()  # keeps track of all positions we've been to
graph = {}  # stores connections between positions - this is our maze map
exit_pos = None  # will store the exit coordinates once we find it

def bfs(start, goal):
    # Breadth-First Search - finds the shortest path between two points
    # This is what calculates our optimal route after exploring
    queue, seen = [[start]], {start}
    while queue:
        path = queue.pop(0)
        if path[-1] == goal:
            return path
        for nb in graph.get(path[-1], []):
            if nb not in seen:
                seen.add(nb)
                queue.append(path + [nb])
    return [start]

def turn(target):
    # Turns the robot to face a specific direction
    # Calculates the shortest turn needed instead of always turning the same way
    global h
    d = (target - h) % 360
    if d == 90:
        drivetrain.turn_for(RIGHT, 90, DEGREES)
    elif d == 180:
        drivetrain.turn_for(RIGHT, 180, DEGREES)
    elif d == 270:
        drivetrain.turn_for(LEFT, 90, DEGREES)  # turning left once is faster than right three times!
    if d:
        wait(10, MSEC)
    h = target

def move():
    # Moves forward one grid cell and records it in our graph
    global x, y
    prev = (x, y)
    drivetrain.drive_for(FORWARD, 250, MM)  # 250mm is exactly one grid cell
    wait(10, MSEC)
    
    # Update our position based on which way we're facing
    if h == 0:
        y += 1
    elif h == 90:
        x += 1
    elif h == 180:
        y -= 1
    else:
        x -= 1
    
    cur = (x, y)
    visited.add(cur)
    
    # Add this connection to the graph in both directions
    # This lets us navigate either way between connected cells
    graph.setdefault(prev, []).append(cur)
    graph.setdefault(cur, []).append(prev)

def backtrack():
    # Same as move() but doesn't record anything - used for retracing steps
    global x, y
    drivetrain.drive_for(FORWARD, 250, MM)
    wait(10, MSEC)
    if h == 0:
        y += 1
    elif h == 90:
        x += 1
    elif h == 180:
        y -= 1
    else:
        x -= 1

def explore():
    # Main exploration function - uses DFS to map the entire maze
    global exit_pos, x, y
    stack = [(0, 0)]
    visited.add((0, 0))
    
    while stack:
        # Check if we're on the exit tile
        if down_eye.detect(RED) and not exit_pos:
            exit_pos = (x, y)
        
        found = False
        # Try all four directions: North, East, South, West
        for hd in [0, 90, 180, 270]:
            # Don't go south from start position - there's an edge there!
            if x == 0 and y == 0 and hd == 180:
                continue
            
            turn(hd)
            # Calculate where we'd end up if we moved in this direction
            nx = x + (1 if hd == 90 else -1 if hd == 270 else 0)
            ny = y + (1 if hd == 0 else -1 if hd == 180 else 0)
            
            # Check if the path is clear and we haven't been there yet
            # 240mm threshold to match our 250mm grid cells
            if front_distance.get_distance(MM) > 240 and not down_eye.detect(RED) and (nx, ny) not in visited:
                move()
                stack.append((x, y))
                found = True
                break
        
        # If no new directions available, backtrack to previous position
        if not found:
            if len(stack) > 1:
                stack.pop()
                target = stack[-1]
                dx, dy = target[0] - x, target[1] - y
                
                # If target is just one step away, go there directly
                if abs(dx) + abs(dy) == 1:
                    turn(0 if dy == 1 else 90 if dx == 1 else 180 if dy == -1 else 270)
                    backtrack()
                else:
                    # If target is further away, use BFS to find the shortest path back
                    back_path = bfs((x, y), target)
                    for pos in back_path[1:]:
                        dx, dy = pos[0] - x, pos[1] - y
                        turn(0 if dy == 1 else 90 if dx == 1 else 180 if dy == -1 else 270)
                        backtrack()
            else:
                break  # we've explored everything!

def nav_to_start():
    # Navigate back to the starting position using our map
    global x, y
    if x == 0 and y == 0:
        return  # already there
    
    path_home = bfs((x, y), (0, 0))
    for pos in path_home[1:]:
        dx, dy = pos[0] - x, pos[1] - y
        turn(0 if dy == 1 else 90 if dx == 1 else 180 if dy == -1 else 270)
        backtrack()

def nav(path):
    # Follow any given path - used for the blue line shortest path
    global x, y
    for pos in path[1:]:
        dx, dy = pos[0] - x, pos[1] - y
        turn(0 if dy == 1 else 90 if dx == 1 else 180 if dy == -1 else 270)
        backtrack()

def draw_map(path):
    # Draws an ASCII representation of the maze in the console
    # S = start, E = exit, * = shortest path, . = explored area
    all_pos = list(graph.keys())
    min_x, max_x = min(p[0] for p in all_pos), max(p[0] for p in all_pos)
    min_y, max_y = min(p[1] for p in all_pos), max(p[1] for p in all_pos)
    pset = set(path)
    
    brain.print("Maze Map")
    brain.new_line()
    for yy in range(max_y, min_y - 1, -1):
        line = ""
        for xx in range(min_x, max_x + 1):
            if (xx, yy) == (0, 0):
                line += "S"
            elif (xx, yy) == exit_pos:
                line += "E"
            elif (xx, yy) in pset:
                line += "*"
            elif (xx, yy) in all_pos:
                line += "."
            else:
                line += " "
        brain.print(line)
        brain.new_line()

def start():
    # Main program - runs everything in sequence
    global x, y, h, visited, graph, exit_pos
    
    # Set robot to max speed
    drivetrain.set_drive_velocity(100, PERCENT)
    drivetrain.set_turn_velocity(100, PERCENT)
    
    # Reset all tracking variables
    x, y, h = 0, 0, 0
    visited, graph, exit_pos = set(), {}, None
    
    # Phase 1: Explore entire maze with black pen
    pen.move(DOWN)
    pen.set_pen_color(BLACK)
    brain.print("PHASE 1: EXPLORING")
    brain.new_line()
    explore()
    pen.move(UP)
    drivetrain.stop()
    
    brain.print("Explored: {}".format(len(visited)))
    brain.new_line()
    
    if exit_pos:
        # Calculate shortest path from start to exit
        path = bfs((0, 0), exit_pos)
        brain.print("Shortest: {}".format(len(path)))
        brain.new_line()
        
        # Go back to start before drawing the optimal path
        brain.print("RETURNING TO START")
        brain.new_line()
        nav_to_start()
        
        # Phase 2: Navigate shortest path with blue pen
        pen.set_pen_color(BLUE)
        pen.move(DOWN)
        brain.print("PHASE 2: SHORTEST PATH")
        brain.new_line()
        nav(path)
        pen.move(UP)
        
        # Print the maze map to console
        draw_map(path)

vr_thread(start)
