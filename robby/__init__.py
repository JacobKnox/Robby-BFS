"""
Robby the Robot simulator

Written by Jim Marshall
Sarah Lawrence College, Spring 2015
http://science.slc.edu/~jmarshall

Based on Chapter 9 of the book "Complexity: A Guided Tour"
by Melanie Mitchell, Oxford University Press, 2009.

Updated by Jake Roman and Matthew Eicholtz
Florida Southern College, Fall 2023
"""

from robby.graphics import *
import random
import time
import os

POSSIBLE_ACTIONS = ["MoveNorth", "MoveSouth", "MoveEast", "MoveWest", "PickUp"]
ROOT = "robby" + os.sep

class World(GraphWin):
    def __init__(self, rows, cols):
        # Create the grid
        iconSize = 40 # pixels
        spacing = 3 # pixels
        windowWidth = (iconSize + 2 * spacing) * (cols + 2)
        windowHeight = (iconSize + 2 * spacing) * (rows + 2)
        GraphWin.__init__(self, "Robby the Robot", windowWidth, windowHeight)
        self.setBackground("white")
        self.graphicsEnabled = False
        self.blank = Rectangle(Point(-1, iconSize), Point(windowWidth, windowHeight - iconSize))
        self.blank.setFill("aliceblue")
        self.blank.setOutline("black")
        self.cellw = iconSize + 2 * spacing
        self.cellh = iconSize + 2 * spacing
        x1, y1 = self.cellw, self.cellh
        x2, y2 = self.cellw * (cols + 1), self.cellh * (rows + 1)
        x, y = x1, y1
        for r in range(rows + 1):
            Line(Point(x1, y), Point(x2, y)).draw(self)
            y += self.cellh
        for r in range(cols + 1):
            Line(Point(x, y1), Point(x, y2)).draw(self)
            x += self.cellw
        self.numRows = rows
        self.numCols = cols
        self.topRow = 0
        self.bottomRow = rows - 1
        self.leftCol = 0
        self.rightCol = cols - 1
        
        # Set Robby's current position
        self.robbyRow = 0
        self.robbyCol = 0
        
        # Create the cells
        self.grid = [[GridCell(self, r, c) for c in range(cols)] for r in range(rows)]

        # Add text objects
        self.centerText = Text(Point(windowWidth / 2, windowHeight / 2), "")
        self.centerText._reconfig("anchor", "c")
        self.centerText.setStyle("italic")
        self.centerText.setSize(36)
        self.topLeftText = Text(Point(iconSize + 2 * spacing, iconSize / 2 + spacing), "")
        self.topLeftText._reconfig("anchor", "w")
        self.topLeftText.setSize(12)
        self.topLeftText.draw(self)
        self.topRightText = Text(Point(windowWidth - iconSize - 2 * spacing, iconSize / 2 + spacing), "")
        self.topRightText._reconfig("anchor", "e")
        self.topRightText.setSize(12)
        self.topRightText.draw(self)
        self.bottomLeftText = Text(Point(iconSize + 2 * spacing, windowHeight - iconSize / 2 - spacing), "")
        self.bottomLeftText._reconfig("anchor", "w")
        self.bottomLeftText.setSize(12)
        self.bottomLeftText.draw(self)

        # Create parameters to track score, cost, and battery life
        self.score = 0
        self.cost = 0
        self.fullBattery = rows * cols
        self.batteryLife = self.fullBattery

        self.costPerAction = 1
        self.costPerCrash = 10
        self.scorePerCan = 1
        self.scorePerBattery = 0

        self.updateScore()
        self.updateCost()
        self.updateBatteryLife()

        # Initialize a parameter of initial contents (used to remember when contents are loaded from file)
        self.originalContents = None

    def graphicsOff(self, message=""):
        if self.graphicsEnabled:
            self.blank.draw(self)
            self.centerText.setText(message)
            self.centerText.draw(self)
            # self.topLeftText.undraw()
            # self.topRightText.undraw()
            # self.bottomLeftText.undraw()
            self.graphicsEnabled = False

    def graphicsOn(self):
        if not self.graphicsEnabled:
            self.blank.undraw()
            self.centerText.undraw()
            # self.topLeftText.draw(self)
            # self.topRightText.draw(self)
            # self.bottomLeftText.draw(self)
            self.graphicsEnabled = True
            self._updateGrid()

    def _updateGrid(self):
        for r in range(self.numRows):
            for c in range(self.numCols):
                self.grid[r][c].updateGraphics()

    def distributeBatteries(self, density=0.50):
        for r in range(self.numRows):
            for c in range(self.numCols):
                if random.uniform(0, 1) < density:
                    self.grid[r][c].setContents("B")

    def distributeCans(self, density=0.50):
        for r in range(self.numRows):
            for c in range(self.numCols):
                if random.uniform(0, 1) < density:
                    self.grid[r][c].setContents("C")

    def distributeWalls(self, density=0.50):
        for r in range(self.numRows):
            for c in range(self.numCols):
                if random.uniform(0, 1) < density and not self.grid[r][c].robbyIsHere():
                    self.grid[r][c].setContents("W")               

    def _gridContents(self):
        return "".join([self.grid[r][c].contents for r in range(self.numRows) for c in range(self.numCols)])

    def performAction(self, action):
        # Check if desired action is possible
        if action not in POSSIBLE_ACTIONS:
            print("ERROR -- possible actions are:\n%s" % POSSIBLE_ACTIONS)
        
        # Check edge crashes
        elif action == "MoveNorth" and self.robbyRow == self.topRow or \
                action == "MoveSouth" and self.robbyRow == self.bottomRow or \
                action == "MoveEast" and self.robbyCol == self.rightCol or \
                action == "MoveWest" and self.robbyCol == self.leftCol:
            self.grid[self.robbyRow][self.robbyCol].crashIntoWall(action)
            self.cost += self.costPerCrash
            self.batteryLife -= self.costPerCrash
        
        # Check wall crashes
        elif action == "MoveNorth" and self.grid[self.robbyRow - 1][self.robbyCol].contents == "W" or \
                action == "MoveSouth" and self.grid[self.robbyRow + 1][self.robbyCol].contents == "W" or \
                action == "MoveEast" and self.grid[self.robbyRow][self.robbyCol + 1].contents == "W" or \
                action == "MoveWest" and self.grid[self.robbyRow][self.robbyCol - 1].contents == "W":
            self.grid[self.robbyRow][self.robbyCol].crashIntoWall(action)
            self.cost += self.costPerCrash
            self.batteryLife -= self.costPerCrash

        # Take action
        else:
            self.grid[self.robbyRow][self.robbyCol].undrawRobby()
            if action == "MoveNorth":
                self.robbyRow -= 1
                self.cost += self.costPerAction
                self.batteryLife -= self.costPerAction
            elif action == "MoveSouth":
                self.robbyRow += 1
                self.cost += self.costPerAction
                self.batteryLife -= self.costPerAction
            elif action == "MoveEast":
                self.robbyCol += 1
                self.cost += self.costPerAction
                self.batteryLife -= self.costPerAction
            elif action == "MoveWest":
                self.robbyCol -= 1
                self.cost += self.costPerAction
                self.batteryLife -= self.costPerAction
            elif action == "PickUp":
                if self.grid[self.robbyRow][self.robbyCol].contents == "B":
                    self.score += self.scorePerBattery
                    self.cost += self.costPerAction
                    self.batteryLife = self.fullBattery
                elif self.grid[self.robbyRow][self.robbyCol].contents == "C":
                    self.score += self.scorePerCan
                    self.cost += self.costPerAction
                    self.batteryLife -= self.costPerAction
                self.grid[self.robbyRow][self.robbyCol].setContents("E")
            else:
                raise Exception("bad action: %s" % action) # should never happen
            self.grid[self.robbyRow][self.robbyCol].updateGraphics()

        if self.graphicsEnabled:
            self.updateScore()
            self.updateCost()
            self.updateBatteryLife()
        return 1

    def north(self):
        return self.performAction("MoveNorth")

    def south(self):
        return self.performAction("MoveSouth")

    def east(self):
        return self.performAction("MoveEast")

    def west(self):
        return self.performAction("MoveWest")

    def grab(self):
        return self.performAction("PickUp")
    
    def look(self):
        return self.getPercept()

    def getCansRemaining(self):
        '''Return the number of cans remaining in the world.'''
        return self._gridContents().count("C")

    def getCurrentPosition(self):
        return self.robbyRow, self.robbyCol

    def getPercept(self):
        '''Get the contents of the neighboring cells returned as a dictionary. The keys include Robby and the 
        principal directions that can be searched.'''
        percept = {}
        percept['Robby'] = self.grid[self.robbyRow][self.robbyCol].contents
        percept['North'] = "W" if self.robbyRow == self.topRow else self.grid[self.robbyRow - 1][self.robbyCol].contents
        percept['South'] = "W" if self.robbyRow == self.bottomRow else self.grid[self.robbyRow + 1][self.robbyCol].contents
        percept['East'] = "W" if self.robbyCol == self.rightCol else self.grid[self.robbyRow][self.robbyCol + 1].contents
        percept['West'] = "W" if self.robbyCol == self.leftCol else self.grid[self.robbyRow][self.robbyCol - 1].contents
        return percept

    def getState(self):
        '''Get the current state of the environment, encoded as a string.'''
        state = ""
        for r in range(self.numRows):
            for c in range(self.numCols):
                if r == self.robbyRow and c == self.robbyCol:
                    state += "R" + self.grid[r][c].contents
                else:
                    state += self.grid[r][c].contents + " "
        return state

    def goto(self, row, col):
        '''Move Robby directly to a specific row and column.'''
        assert 0 <= row < self.numRows and 0 <= col < self.numCols
        self.grid[self.robbyRow][self.robbyCol].undrawRobby()
        self.robbyRow = row
        self.robbyCol = col
        self.grid[self.robbyRow][self.robbyCol].updateGraphics()

    def load(self, contents):
        '''Load environment setup from a string of contents.'''
        # Check to make sure the contents are valid
        rows, cols = self.numRows, self.numCols
        if len(contents) != rows * cols:
            print(f"ERROR -- invalid grid contents for size ({rows}, {cols}): {contents}")
            return 0
        
        # Set contents in the world
        for r in range(rows):
            for c in range(cols):
                self.grid[r][c].setContents(contents[r * cols + c])

        # Store the original contents for potential re-loading in the future
        self.originalContents = contents

    def reset(self):
        '''Reset the world contents, score, cost, and battery life.'''
        if self.originalContents is not None:
            self.load(self.originalContents)
        self.score = 0
        self.cost = 0
        self.batteryLife = self.fullBattery
        self.updateScore()
        self.updateCost()
        self.updateBatteryLife()
        self.graphicsOn()

    def setFullBattery(self, battery):
        '''Update the power in a full battery.'''
        self.fullBattery = battery
        self.batteryLife = battery
        self.updateBatteryLife()

    def show(self):
        '''Display the current state of Robby's world at the command line.'''
        s = "\n"
        for r in range(self.numRows):
            for c in range(self.numCols):
                if r == self.robbyRow and c == self.robbyCol:
                    if self.grid[r][c].contents == "B":
                        s += "RB "
                    elif self.grid[r][c].contents == "C":
                        s += "RC "
                    elif self.grid[r][c].contents == "W":
                        s += "RW " # this should never happen!
                    else:
                        s += "R  "
                else:
                    s += ".  " if self.grid[r][c].contents == "E" else self.grid[r][c].contents + "  "
            s += "\n"
        print(s)

    def updateScore(self):
        '''Update the text object that tracks score.'''
        self.topLeftText.setText(f"SCORE = {self.score}")

    def updateCost(self):
        '''Update the text object that tracks cost.'''
        self.topRightText.setText(f"COST = {self.cost}")

    def updateBatteryLife(self):
        '''Update the text object that tracks battery life.'''
        self.bottomLeftText.setText(f"BATTERY = {self.batteryLife}/{self.fullBattery}")

        if self.batteryLife <= 0:
            # self.centerText.setText("Robby Died!")
            self.graphicsOff("Robby Died!")

class GridCell:
    def __init__(self, world, row, col):
        # Setup cell properties
        self.world = world
        self.row = row
        self.col = col
        self.contents = "E"
        self.icon = None
        self.owIcon = None
        
        # Compute center of cell
        x = (col + 1) * world.cellw + world.cellw / 2
        y = (row + 1) * world.cellh + world.cellh / 2

        # Make dictionary of icons
        iconNames = ["robby", "can", "robby_can", "battery", "robby_battery", "wall",
            "crash_n", "crash_can_n", "crash_battery_n",
            "crash_s", "crash_can_s", "crash_battery_s",
            "crash_e", "crash_can_e", "crash_battery_e",
            "crash_w", "crash_can_w", "crash_battery_w"]
        self.icons = {}
        for name in iconNames:
            self.icons[name] = Image(Point(x, y), ROOT + name + ".gif")

        # Add icons to the dictionary for crashes
        self.icons["ow_n"] = Image(Point(x, y - world.cellh), ROOT + "ow_n.gif")
        self.icons["ow_s"] = Image(Point(x, y + world.cellh), ROOT + "ow_s.gif")
        self.icons["ow_w"] = Image(Point(x - world.cellw, y), ROOT + "ow_w.gif")
        self.icons["ow_e"] = Image(Point(x + world.cellw, y), ROOT + "ow_e.gif")


    def robbyIsHere(self):
        return self.row == self.world.robbyRow and self.col == self.world.robbyCol

    def setContents(self, newContents):
        assert newContents in ["E", "C", "W", "B"]
        self.contents = newContents
        self.updateGraphics()

    def clearOwIcon(self):
        if self.owIcon is not None:
            self.owIcon.undraw()
            self.owIcon = None

    def updateGraphics(self):
        '''Update the graphics in the current GridCell object.'''
        if not self.world.graphicsEnabled:
            return 0
        self.clearOwIcon()
        
        if self.robbyIsHere():
            if self.contents == "B":
                newIcon = self.icons["robby_battery"]
            elif self.contents == "C":
                newIcon = self.icons["robby_can"]
            else:
                newIcon = self.icons["robby"]
        else:
            if self.contents == "B":
                newIcon = self.icons["battery"]
            elif self.contents == "C":
                newIcon = self.icons["can"]
            elif self.contents == "W":
                newIcon = self.icons["wall"]
            else:
                newIcon = None
        if newIcon is not self.icon:
            if newIcon is not None:
                newIcon.draw(self.world)
            if self.icon is not None:
                self.icon.undraw()
            self.icon = newIcon

    def undrawRobby(self):
        if not self.world.graphicsEnabled:
            return
        self.clearOwIcon()
        if self.contents == "B":
            newIcon = self.icons["battery"]
            newIcon.draw(self.world)
            self.icon.undraw()
            self.icon = newIcon
        elif self.contents == "C":
            newIcon = self.icons["can"]
            newIcon.draw(self.world)
            self.icon.undraw()
            self.icon = newIcon
        elif self.contents == "W":
            newIcon = self.icons["wall"]
            newIcon.draw(self.world)
            self.icon.undraw()
            self.icon = newIcon
        else:
            self.icon.undraw()
            self.icon = None

    def crashIntoWall(self, action):
        # Are graphics enabled?
        if not self.world.graphicsEnabled:
            return 0

        # Check if there are any contents in the cell Robby is at
        if self.contents == "B":
            item = "_battery"
        elif self.contents == "C":
            item = "_can"
        else:
            item = ""

        # Check which direction Robby is attempting to move
        if action == "MoveNorth":
            direction = "_n"
        elif action == "MoveSouth":
            direction = "_s"
        elif action == "MoveEast":
            direction = "_e"
        elif action == "MoveWest":
            direction = "_w"
        else:
            raise Exception("bad crash action: %s" % action)

        # Setup appropriate icons
        crashIcon = self.icons["crash" + item + direction]
        owIcon = self.icons["ow" + direction]
        if self.icon is not None:
            self.icon.undraw()
        if self.owIcon is not None:
            self.owIcon.undraw()
        crashIcon.draw(self.world)
        owIcon.draw(self.world)
        self.icon = crashIcon
        self.owIcon = owIcon

