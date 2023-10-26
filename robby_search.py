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
                    help="Path to a text file containing the world design")
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


def main(file, actions, battery, verbose):
    # Read world parameters (size, location of Robby, and contents) from file
    # ***EDIT CODE HERE***
    rows, cols = 1, 1
    r0, c0 = 0, 0
    contents = 'E'

    # Create Robby's world
    # ***EDIT CODE HERE***
    rw = World(rows, cols)
    rw.graphicsOn()

    # Play in Robby's world
    path = ''
    while True:
        # Check to see if Robby has picked up all the cans
        if False:  # ***EDIT CODE HERE***
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
                    pass


def bfs(rw, state, actions, verbose=False):
    '''Perform breadth-first search on the world state given an ordered string of actions to check (e.g. 'GNESW').'''
    # ***EDIT CODE HERE***
    cnt = 0  # counter to see how long the search took
    path = ''

    if verbose:
        print('--> searched {} paths'.format(cnt))

    return path


def issolved(rw, state, path):
    '''Check whether a series of actions (path) taken in Robby's world results in a solved problem.'''
    rows, cols = rw.numRows, rw.numCols  # size of the world
    row, col = rw.getCurrentPosition()  # Robby's current (starting) position
    state = list(state)  # convert the string to a list so we can update it
    battery = rw.fullBattery

    # ***EDIT CODE HERE***
    for action in path:
        pass

        # Did Robby run out of battery?
        if battery <= 0:
            return False

        # Did Robby grab all the cans?
        if state.count("C") == 0:
            return True

    return False  # if we made it this far, we did not complete the goal


def isvalid(rw, state, path):
    '''Check whether a series of actions (path) taken in Robby's world is valid.'''
    rows, cols = rw.numRows, rw.numCols  # size of the maze
    row, col = rw.getCurrentPosition()  # robby's current (starting) position
    state = list(state)
    memory = []  # keep track of where robby has been to prohibit "loops"
    battery = rw.fullBattery

    # ***EDIT CODE HERE***
    for action in path:
        pass

        # Path is invalid if Robby has run out of battery
        if False:  # ***EDIT CODE HERE***
            return False

        # Path is invalid if Robby's goes "out of bounds"
        if False:  # ***EDIT CODE HERE***
            return False

        # Path is invalid if Robby runs into a wall
        if False:  # ***EDIT CODE HERE***
            return False

        # Path is invalid if robby repeats a state in memory
        if (row, col, "".join(state)) in memory:
            return False
        # add the new state to memory
        memory.append((row, col, "".join(state)))

    return True  # if we made it this far, the path is valid


if __name__ == '__main__':
    args = parser.parse_args()
    main(args.file, args.actions, args.battery)
