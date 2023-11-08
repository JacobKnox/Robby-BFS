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
    description="Use breadth-first search (BFS) to help Robby the Robot pick up cans without running out of battery"
)
# ***EDIT CODE HERE***
parser.add_argument(
    "file",
    help="Path to a text file containing the world design",
)
parser.add_argument(
    "-a",
    "--actions",
    help="String defining the order of actions to search (default: 'GNESW')",
    default="GNESW",
)
parser.add_argument(
    "-b",
    "--battery",
    help="Integer defining the full battery power",
    default=7,
    type=int,
)
parser.add_argument(
    "-v",
    "--verbose",
    help="Flag to display details about the search",
    action="store_true",
)


def main(file: str, actions: str, battery: int, verbose: bool):
    # Read world parameters (size, location of Robby, and contents) from file
    # ***EDIT CODE HERE***
    lines = open(file, "r").readlines()
    rows, cols = [int(char) for char in lines[0].strip().split(" ")]
    r0, c0 = [int(char) for char in lines[1].strip().split(" ")]
    contents = "".join([line.strip() for line in lines[2:]]).replace(".", "E")

    # Create Robby's world
    # ***EDIT CODE HERE***
    rw = World(rows, cols)
    rw.graphicsOn()
    rw.load(contents)
    rw.goto(r0, c0)
    rw.setFullBattery(battery)

    # Play in Robby's world
    path = ""
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
                print("Running breadth-first search...", end="")
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
                    time.sleep(0.5)
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
    """Perform breadth-first search on the world state given an ordered string of actions to check (e.g. 'GNESW')."""
    # ***EDIT CODE HERE***
    path = ""
    cnt = 0  # counter to see how long the search took
    row, col = rw.getCurrentPosition()  # Robby's current (starting) position
    rows, cols = rw.numRows, rw.numCols  # Number of rows and columns in the world

    visited = []  # Initialize the list of visited nodes

    queue = Queue()  # Initialize the queue

    # Add starting node to queue and visited nodes
    queue.put(("", row, col, state))
    visited.append((row, col, state))

    while not queue.empty():
        node = queue.get()  # Pop the first node from the queue
        if verbose:
            print(f"Exploring paths from {node[0]}...")
        visited.append((node[1], node[2], node[3]))
        cnt += 1  # Increase our search length count
        temp_path = node[0]

        # If the node contains the goal state then return the solution
        if issolved(rw, state, temp_path):
            path = temp_path
            break

        # For each available action
        for action in actions:
            # Determine the child node for the given action
            # print(f'\nCurrent position: ({node[1]}, {node[2]})')
            if isvalid(rw, state, temp_path + action):
                child = ()
                if action == "N":
                    child = (temp_path + action, node[1] - 1, node[2], state)
                elif action == "E":
                    child = (temp_path + action, node[1], node[2] + 1, state)
                elif action == "S":
                    child = (temp_path + action, node[1] + 1, node[2], state)
                elif action == "W":
                    child = (temp_path + action, node[1], node[2] - 1, state)
                elif action == "G":
                    new_state = list(node[3])
                    position = node[1] * cols + node[2]
                    new_state[position] = "E"
                    child = (temp_path + action, node[1], node[2], "".join(new_state))
                if child not in visited:
                    queue.put(child)

    if verbose:
        print("--> searched {} paths".format(cnt))

    return path


def issolved(rw: World, state: str, path: str) -> bool:
    """Check whether a series of actions (path) taken in Robby's world results in a solved problem."""
    row, col = rw.getCurrentPosition()  # Robby's current (starting) position
    rows, cols = rw.numRows, rw.numCols
    state = list(state)  # convert the string to a list so we can update it

    if not isvalid(rw, "".join(state), path):
        return False

    # ***EDIT CODE HERE***
    for action in path:
        if action == "N":
            row -= 1
        elif action == "S":
            row += 1
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
    """Check whether a series of actions (path) taken in Robby's world is valid."""
    rows, cols = rw.numRows, rw.numCols  # size of the maze

    # It's getting the starting position from the very beginning and not from where Robby is currently
    row, col = rw.getCurrentPosition()  # robby's current (starting) position
    state = list(state)
    memory = []  # keep track of where robby has been to prohibit "loops"
    battery = rw.fullBattery

    # ***EDIT CODE HERE***
    for action in path:
        battery -= 1
        if state[row * cols + col] == "C" and action != "G":
            return False
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
            if item == "E" or item == "W":
                return False
            if item == "B":
                battery = rw.fullBattery
            state[row * cols + col] = "E"
        # pdb.set_trace()
        # Path is invalid if Robby has run out of battery
        if battery <= 0:  # ***EDIT CODE HERE***
            return False

        # Path is invalid if Robby's goes "out of bounds"
        if row < 0 or row >= rows or col < 0 or col >= cols:  # ***EDIT CODE HERE***
            return False

        # Path is invalid if Robby runs into a wall
        if state[row * cols + col] == "W":  # ***EDIT CODE HERE***
            return False

        # Path is invalid if robby repeats a state in memory
        if (row, col, "".join(state)) in memory:
            return False
        # add the new state to memory
        memory.append((row, col, "".join(state)))

    return True  # if we made it this far, the path is valid


if __name__ == "__main__":
    args = parser.parse_args()
    main(args.file, args.actions, args.battery, args.verbose)
