# VEX Robotics Maze Solver

## Module Information
- **Module**: Robotics
- **Level**: 6
- **Assignment**: A Mouse in a Maze
- **Student**: Feras Dammag

## AI Transparency Statement

**Sheffield Hallam University – Artificial Intelligence Transparency Scale (AITS)**

I confirm that no AI tools were used in the preparation or completion of this assessment. This submission aligns with AITS 1 of the Artificial Intelligence Transparency Scale.

All code, documentation, and project work is my own original work completed without the assistance of generative AI tools.

---

## What This Project Does

I built a robot in VEX VR that can solve randomly generated mazes. It explores the entire maze using DFS (Depth-First Search), figures out the shortest path to the exit using BFS (Breadth-First Search), then goes back to the start and follows that optimal route.

## What I Implemented

### Basic Stuff (40%)
- Robot moves through corridors without crashing into walls
- Finds the exit successfully
- Takes the fastest route out

### Advanced Features (60%)
- Calculates the quickest route using BFS
- Maps out the entire maze, not just one path
- Returns home after reaching the exit

## How It Actually Works

The robot does everything in phases:

1. **Exploration Phase**: Uses DFS to systematically check every corridor. Draws a black line as it goes and builds a graph of all the connections.
2. **Calculating Phase**: Uses BFS on the graph to work out the shortest path from start to exit.
3. **Navigation Phase**: Goes back to the start, then follows the shortest path with a blue pen so you can see the optimal route.
4. **Visualization**: Prints an ASCII map in the console showing the whole maze with the shortest path marked.

## Technical Details

### Wall Detection
I'm using the `front_distance` sensor with a 240mm threshold. This works well because each grid cell is exactly 250mm, so anything less than 240mm away means there's a wall. I also check the `down_eye` sensor to detect the red exit tile and make sure the robot doesn't fall off edges.

### The Exploration Algorithm
The explore function checks all four directions (North, East, South, West) in a fixed order. When there's nowhere new to go, it backtracks using a stack to the last position that had unexplored options. The graph gets built in both directions as it goes, so I can navigate either way between connected positions later.

### The Pathfinding Algorithm
After exploring, BFS calculates the shortest path. uses a queue to check paths level by level until it finds the goal. This guarantees the shortest route.

### Position Tracking
I'm tracking position with simple x,y coordinates starting from (0,0). The heading is stored as degrees: 0 is North, 90 is East, 180 is South, 270 is West. After every 250mm move, the position updates based on which direction the robot was facing.

## Video Demo

You can watch it here: https://youtu.be/LkJAeetwlMM

The video shows the whole process - exploration with the black trail, then the blue line showing the shortest path.

## How the Code is Organised

- `bfs()` - the pathfinding algorithm
- `turn()` - makes the robot face a specific direction
- `move()` - moves forward and adds to the graph
- `backtrack()` - moves without recording (for paths we already know)
- `explore()` - the main DFS loop that maps everything
- `nav_to_start()` - gets back to the start position
- `nav()` - follows any path
- `draw_map()` - prints the ASCII maze

## Running It

1. Go to https://vr.vex.com/
2. Pick the "Dynamic Wall Maze" playground
3. Copy the code from `solve_maze.py`
4. Paste it into the Python editor
5. Hit start 

## Stuff I Used for Reference

- DFS on Wikipedia: https://en.wikipedia.org/wiki/Depth-first_search
- BFS on Wikipedia: https://en.wikipedia.org/wiki/Breadth-first_search
- Python docs when I got stuck: https://docs.python.org/3/

## Problems I Ran Into

- **Left-Wall Following Mistake**: Originally I implemented a left-wall following algorithm, which did find the exit but only explored one path through the maze. Had to completely restructure it to use proper DFS that checks all four directions systematically so it would map the ENTIRE maze, not just one route.
- **Falling Off Edges**: The robot kept falling off at the start and exit boundaries. Fixed this by adding special position checks for (0,0) going south and checking for the red exit tile.
- **Backtracking Issues**: At first when the robot backtracked, it was re-recording all the connections which messed up the graph. Split this into two functions - `move()` for new exploration and `backtrack()` for retracing known paths.

## Performance Stats

- Running at 100% speed for both driving and turning
- Takes about 3-4 minutes to explore and complete the whole maze
- The shortest path is usually about 30-40% of the total distance the robot travels during exploration
