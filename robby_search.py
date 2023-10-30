# robby_search.py
# Use breadth-first search (BFS) to help Robby the Robot pick up cans without running out of battery.

import argparse
from collections import deque
import pdb
from queue import Queue
from robby.graphics import *
from robby import World
import time

# Use argparse to allow user to enter command line arguments for:
#   *file - a text file containing the world design (required)
#   *actions - a string defining the order of actions to search (optional, default='GNESW')
#   *battery - an integer defining the full battery power (optional, default=7)
#   *verbose - a flag to display details about the search
parser = argparse.ArgumentParser(
    description="Use breadth-first search (BFS) to help Robby the Robot pick up cans without running out of battery")
# ***EDIT CODE HERE***
parser.add_argument('-f', '--file',
                    help="Path to a text file containing the world design",
                    required=True)
parser.add_argument('-a', '--actions',
                    help="String defining the order of actions to search (default: 'GNESW')",
                    default="GNESW")
parser.add_argument('-b', '--battery',
                    help="Integer defining the full battery power",
                    default=7,
                    type=int)
parser.add_argument('-v', '--verbose',
                    help="Flag to display details about the search",
                    default=False,
                    action=argparse.BooleanOptionalAction)


def main(file: str, actions: str, battery: int, verbose: bool):
    # Read world parameters (size, location of Robby, and contents) from file
    # ***EDIT CODE HERE***
    lines = open(file, 'r').readlines()
    rows, cols = [int(char) for char in lines[0].strip().split(' ')]
    r0, c0 = [int(char) for char in lines[1].strip().split(' ')]
    contents = ''.join([line.strip() for line in lines[2:]]).replace('.', 'E')

    # Create Robby's world
    # ***EDIT CODE HERE***
    rw = World(rows, cols)
    rw.graphicsOn()
    rw.load(contents)
    rw.goto(r0, c0)
    rw.setFullBattery(battery)
    
    # Play in Robby's world
    path = ''
    while True:
        # Check to see if Robby has picked up all the cans
        if rw.getCansRemaining() <= 0:  # ***EDIT CODE HERE***
            rw.graphicsOff("Robby wins!")

        # Handle key presses
        key = rw.checkKey()
        if key:
            if key == "Escape":
                break
            elif key == "Up":
                rw.north()
            elif key == "Down":
                rw.south()
            elif key == "Right":
                rw.east()
            elif key == "Left":
                rw.west()
            elif key == "space":
                rw.grab()
            elif key == "d":  # debug
                pdb.set_trace()
            elif key == "r":  # reset the world
                rw.reset()
                rw.goto(r0, c0)
                rw.graphicsOn()
            elif key == "s":  # display the current world at the command line
                rw.show()
            elif key == "b":  # BFS
                print('Running breadth-first search...', end='')
                time.sleep(0.5)
                path = bfs(rw, contents, actions, verbose=verbose)
                if len(path) > 0:
                    print(path)
                else:
                    print("No solution found.")
            elif key == "Return":
                # Use the discovered path (from bfs) to actually move robby through
                # the world! Add a small time delay with time.sleep() so that robby does not move too fast.
                rw.reset()
                rw.goto(r0, c0)
                time.sleep(0.5)

                # ***EDIT CODE HERE***
                for action in path:
                    if action == "N":
                        rw.north()
                    elif action == "S":
                        rw.south()
                    elif action == "E":
                        rw.east()
                    elif action == "W":
                        rw.west()
                    elif action == "G":
                        rw.grab()


def bfs(rw: World, state: str, actions: str, verbose: bool = False) -> str:
    '''Perform breadth-first search on the world state given an ordered string of actions to check (e.g. 'GNESW').'''
    # ***EDIT CODE HERE***
    cnt = 0  # counter to see how long the search took
    tempPath = '' # The string of actions to check if valid or solved
    finalPath = '' # The path that will be built once we solve the problem
    row, col = rw.getCurrentPosition()  # Robby's current (starting) position
    rows, cols = rw.numRows, rw.numCols # Number of rows and columns in the world

    visited = []  # Initialize the list of visited nodes
    
    # Initialize backpointers
    backpointers = {
        (row, col, state): None
    }

    queue = Queue()  # Initialize the queue

    # Add starting node to queue and visited nodes
    queue.put((row, col, state)) 
    visited.append((row, col, state))

    while True:
        # If there are no nodes for expansion then failure
        if queue.empty():
            path = ''
            break

        node = queue.get()      # Pop the first node from the queue
        cnt += 1                # Increase our search length count
            
        # If the node contains the goal state then return the solution
        if issolved(rw, state, path):
            break

        # For each available action
        for action in actions:
            child = ()
            # if (isvalid(rw, node[2], action)):
                # pdb.set_trace()
            # Determine the child node for the given action
            print(f'\nCurrent position: ({node[0]}, {node[1]})')
            if action == 'N':
                child = (node[0] - 1, node[1], state)
            elif action == 'E':
                child = (node[0], node[1] + 1, state)
            elif action == 'S':
                child = (node[0] + 1, node[1], state)
            elif action == 'W':
                child = (node[0], node[1] - 1, state)
            elif action == 'G':
                new_state = node[2]
                position = node[0] * cols + node[1]
                new_state = new_state[:position] + 'E' + new_state[(position + 1):]
                child = (node[0], node[1], new_state)

            # If the move to this child node is not a valid move, move on
            if not isvalid(rw, state, path + action):
                continue # Move on to the next possible action
            
            # If the child has not been visited 
            if child not in visited:
                queue.put(child) # Add child to queue
                visited.append(child) # Add child to visited nodes
                backpointers[child] = node # Add parent node as backpointer to child
            
                # # Build the path 
                # pathNode = node
                # while pathNode is not None:
                #     path.insert(0, pathNode)
                #     pathNode = backpointers[pathNode]
                # path = "".join(path)
                

        # for action in actions:
        #     pdb.set_trace()
        #     if (isvalid(rw, state, path + action)):
        #         queue.put(action)
        # if queue.empty() or issolved(rw, state, path):
        #     break
        # path += queue.get()

    if verbose:
        print('--> searched {} paths'.format(cnt))

    return path


def issolved(rw: World, state: str, path: str) -> bool:
    '''Check whether a series of actions (path) taken in Robby's world results in a solved problem.'''
    row, col = rw.getCurrentPosition()  # Robby's current (starting) position
    rows, cols = rw.numRows, rw.numCols
    state = list(state)  # convert the string to a list so we can update it

    if not isvalid(rw, state, path):
        return False

    # ***EDIT CODE HERE***
    for action in path:
        if action == "N":
            row += 1
        elif action == "S":
            row -= 1
        elif action == "E":
            col += 1
        elif action == "W":
            col -= 1
        elif action == "G":
            state[row * cols + col] = "E"

        # Did Robby grab all the cans?
        if state.count("C") == 0:
            return True

    return False  # if we made it this far, we did not complete the goal


def isvalid(rw: World, state: str, path: str) -> bool:
    '''Check whether a series of actions (path) taken in Robby's world is valid.'''
    rows, cols = rw.numRows, rw.numCols  # size of the maze

    # It's getting the starting position from the very beginning and not from where Robby is currently
    row, col = rw.getCurrentPosition()  # robby's current (starting) position
    state = list(state)
    memory = []  # keep track of where robby has been to prohibit "loops"
    battery = rw.fullBattery

    # ***EDIT CODE HERE***
    for action in path:
        battery -= 1

        if action == "N":
            row -= 1
        elif action == "S":
            row += 1
        elif action == "E":
            col += 1
        elif action == "W":
            col -= 1
        elif action == "G":
            item = state[row * cols + col]
            if item == "B":
                battery = rw.fullBattery
            if item != 'W':
                state[row * cols + col] = "E"
        pdb.set_trace()
        # Path is invalid if Robby has run out of battery
        if battery <= 0:  # ***EDIT CODE HERE***
            return False

        # Path is invalid if Robby's goes "out of bounds"
        if row < 0 or row >= rows or col < 0 or col >= cols:  # ***EDIT CODE HERE***
            return False

        # Path is invalid if Robby runs into a wall
        if state[row * cols + col] == 'W':  # ***EDIT CODE HERE***
            return False

        # Path is invalid if robby repeats a state in memory
        if (row, col, "".join(state)) in memory:
            return False
        # add the new state to memory
        memory.append((row, col, "".join(state)))

    return True  # if we made it this far, the path is valid


if __name__ == '__main__':
    args = parser.parse_args()
    main(args.file, args.actions, args.battery, args.verbose)
