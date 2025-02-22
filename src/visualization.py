import pygame as pg
import numpy as np
import os
from pygame.color import THECOLORS
import random

def calculateIncludedAngle(vector1, vector2):
    includedAngle = abs(np.angle(complex(vector1[0], vector1[1]) / complex(vector2[0], vector2[1])))
    return includedAngle


def findQuadrant(vector):
    quadrant = 0
    if vector[0] > 0 and vector[1] > 0:
        quadrant = 0


class InitializeScreen:
    def __init__(self, screenWidth, screenHeight, fullScreen):
        self.screenWidth = screenWidth
        self.screenHeight = screenHeight
        self.fullScreen = fullScreen

    def __call__(self):
        pg.init()
        if self.fullScreen:
            screen = pg.display.set_mode((self.screenWidth, self.screenHeight), pg.FULLSCREEN, pg.SRCALPHA)
        else:
            screen = pg.display.set_mode((self.screenWidth, self.screenHeight), pg.SRCALPHA)
        pg.display.init()
        pg.fastevent.init()
        return screen


def drawText(screen, text, textColorTuple, textPositionTuple, textSize=50):
    font = pg.font.Font(None, textSize)
    textObj = font.render(text, True, textColorTuple)
    screen.blit(textObj, textPositionTuple)
    return


class GiveExperimentFeedback():
    def __init__(self, screen, textColorTuple, screenWidth, screenHeight):
        self.screen = screen
        self.textColorTuple = textColorTuple
        self.screenHeight = screenHeight
        self.screenWidth = screenWidth

    def __call__(self, trialIndex, score):
        self.screen.fill((0, 0, 0))
        for j in range(trialIndex + 1):
            drawText(self.screen, "No. " + str(j + 1) + " experiment" + "  score: " + str(score[j]),
                     self.textColorTuple, (self.screenWidth / 5, self.screenHeight * (j + 3) / 12))
        pg.display.flip()
        pg.time.wait(3000)

class DrawBackgroundWithStep():
    def __init__(self, screen, gridSize, leaveEdgeSpace, backgroundColor, textColorTuple, playerColors):
        self.screen = screen
        self.gridSize = gridSize
        self.leaveEdgeSpace = leaveEdgeSpace
        self.widthLineStepSpace = np.int(screen.get_width() / (gridSize + 2 * self.leaveEdgeSpace))
        self.heightLineStepSpace = np.int(screen.get_height() / (gridSize + 2 * self.leaveEdgeSpace))
        self.backgroundColor = backgroundColor
        self.textColorTuple = textColorTuple


        self.playerColors = playerColors

    def __call__(self, currentStep, currentScore):
        self.screen.fill((0, 0, 0))
        pg.draw.rect(self.screen, self.backgroundColor, pg.Rect(np.int(self.leaveEdgeSpace * self.widthLineStepSpace),np.int(self.leaveEdgeSpace * self.heightLineStepSpace),np.int(self.gridSize * self.widthLineStepSpace),np.int(self.gridSize * self.heightLineStepSpace)))

        drawText(self.screen, 'Step: ' + str("%3.0f" % currentStep), THECOLORS['white'],
                 (self.widthLineStepSpace * 5, self.widthLineStepSpace), 60)
        # drawText(self.screen, '1P: ' + str(currentScore[0]), self.playerColors[0], (self.widthLineStepSpace * 35  , self.leaveEdgeSpace * 3))
        # drawText(self.screen, '2P: ' + str(currentScore[1]), self.playerColors[1], (self.widthLineStepSpace * 50, self.leaveEdgeSpace * 3))
        drawText(self.screen, 'TotalScore: ' + str(round(float(np.sum(currentScore)), 2)), self.textColorTuple,
                 (self.widthLineStepSpace * 25, self.widthLineStepSpace), 60)
        return


class DrawBackground():
    def __init__(self, screen, gridSize, leaveEdgeSpace, backgroundColor, textColorTuple, playerColors):
        self.screen = screen
        self.gridSize = gridSize
        self.leaveEdgeSpace = leaveEdgeSpace
        self.widthLineStepSpace = np.int(screen.get_width() / (gridSize + 2 * self.leaveEdgeSpace))
        self.heightLineStepSpace = np.int(screen.get_height() / (gridSize + 2 * self.leaveEdgeSpace))
        self.backgroundColor = backgroundColor
        self.textColorTuple = textColorTuple


        self.playerColors = playerColors

    def __call__(self, currentTime, currentScore):
        self.screen.fill((0, 0, 0))
        pg.draw.rect(self.screen, self.backgroundColor, pg.Rect(np.int((self.leaveEdgeSpace - 1) * self.widthLineStepSpace),np.int((self.leaveEdgeSpace - 1)  * self.heightLineStepSpace), 
                                np.int((self.gridSize + 2) * self.widthLineStepSpace),np.int((self.gridSize + 2) * self.heightLineStepSpace)))

        seconds = currentTime / 1000
        drawText(self.screen, 'Time: ' + str("%4.1f" % seconds) + 's', THECOLORS['white'],
                 (self.widthLineStepSpace * 5, self.widthLineStepSpace), 60)
        # drawText(self.screen, '1P: ' + str(currentScore[0]), self.playerColors[0], (self.widthLineStepSpace * 35  , self.leaveEdgeSpace * 3))
        # drawText(self.screen, '2P: ' + str(currentScore[1]), self.playerColors[1], (self.widthLineStepSpace * 50, self.leaveEdgeSpace * 3))
        drawText(self.screen, 'TotalScore: ' + str("%4.1f" % currentScore), self.textColorTuple,
                 (self.widthLineStepSpace * 25, self.widthLineStepSpace), 60)
        return


class DrawNewStateWithBlocksAndFeedback():
    def __init__(self, screen, drawBackground, playerColors, blockColors, targetRadius, playerRadius, blockRadius,
                 mapSize, sheepLife, catchColor=[THECOLORS['yellow'], THECOLORS['white'], THECOLORS['red']]):
        self.screen = screen
        self.drawBackground = drawBackground
        self.playerColors = playerColors
        self.blockColors = blockColors
        self.targetRadius = targetRadius
        self.playerRadius = playerRadius
        self.blockRadius = blockRadius
        self.mapSize = mapSize
        self.leaveEdgeSpace = drawBackground.leaveEdgeSpace
        self.widthLineStepSpace = drawBackground.widthLineStepSpace
        self.heightLineStepSpace = drawBackground.heightLineStepSpace
        self.catchColor = catchColor
        self.sheepLife = sheepLife
    def __call__(self, targetColors, targetPositions, playerPositions, blockPositions, currentTime, currentScore, currentEatenFlag,caughtHistoryList):
        self.drawBackground(currentTime, currentScore)
        mappingFun = lambda x: (x + self.mapSize)*(self.drawBackground.gridSize/(2*self.mapSize))  # mapping mapSize[-1,1] to gridSize[0,40]
        for i, targetPosition in enumerate(targetPositions):
            posX = np.int((mappingFun(targetPosition[0]) + self.leaveEdgeSpace) * self.widthLineStepSpace)
            posY = np.int((mappingFun(targetPosition[1]) + self.leaveEdgeSpace) * self.heightLineStepSpace)
            targetColor = targetColors[i]
            if currentEatenFlag[i] and caughtHistoryList[i] == self.sheepLife:
                # targetColor = self.catchColor[1]
                pg.draw.circle(self.screen, self.catchColor[2], [posX, posY], self.targetRadius * 1.2, width=10)
                pg.time.wait(75)
            elif currentEatenFlag[i]:
                targetColor = np.array(targetColor) - np.array([0, 0, 0, 128])
            surface = pg.Surface(pg.display.get_window_size(), pg.SRCALPHA)
            pg.draw.circle(surface, targetColor, [posX, posY], self.targetRadius)
            self.screen.blit(surface, (0,0))
            #drawText(self.screen, str(i+1), THECOLORS['black'], [posX - self.targetRadius / 4, posY - self.targetRadius / 4], self.targetRadius)

        for blockPosition, blockColor in zip(blockPositions[:], self.blockColors[:]):
            pg.draw.circle(self.screen, blockColor,
                           [np.int((mappingFun(blockPosition[0]) + self.leaveEdgeSpace) * self.widthLineStepSpace),
                            np.int((mappingFun(blockPosition[1]) + self.leaveEdgeSpace) * self.heightLineStepSpace)],
                           self.blockRadius)

        for j, playerPosition, playerColor in zip(range(len(playerPositions)), playerPositions, self.playerColors):
            posPlayerX = np.int((mappingFun(playerPosition[0]) + self.leaveEdgeSpace) * self.widthLineStepSpace)
            posPlayerY = np.int((mappingFun(playerPosition[1]) + self.leaveEdgeSpace) * self.heightLineStepSpace)
            pg.draw.circle(self.screen, playerColor, [posPlayerX, posPlayerY], self.playerRadius)
            drawText(self.screen, str(j+1), THECOLORS['black'], [posPlayerX - self.playerRadius / 4, posPlayerY - self.playerRadius / 4], self.playerRadius)

        return self.screen


class DrawNewStateWithBlocks():
    def __init__(self, screen, drawBackground, playerColors, blockColors, targetRadius, playerRadius, blockRadius, mapSize, catchColor=[THECOLORS['yellow']]):
        self.screen = screen
        self.drawBackground = drawBackground
        self.playerColors = playerColors
        self.blockColors = blockColors
        self.targetRadius = targetRadius
        self.playerRadius = playerRadius
        self.blockRadius = blockRadius
        self.mapSize = mapSize
        self.leaveEdgeSpace = drawBackground.leaveEdgeSpace
        self.widthLineStepSpace = drawBackground.widthLineStepSpace
        self.heightLineStepSpace = drawBackground.heightLineStepSpace
        self.catchColor = catchColor
    def __call__(self, targetColors, targetPositions, playerPositions,blockPositions,currentTime, currentScore,currentEatenFlag):
        self.drawBackground(currentTime, currentScore)
        mappingFun = lambda x: (x + self.mapSize)*(self.drawBackground.gridSize/(2*self.mapSize))  # mapping mapSize[-1,1] to gridSize[0,40]
        for i, targetPosition in enumerate(targetPositions):
            posX = np.int((mappingFun(targetPosition[0]) + self.leaveEdgeSpace) * self.widthLineStepSpace)
            posY = np.int((mappingFun(targetPosition[1]) + self.leaveEdgeSpace) * self.heightLineStepSpace)
            if currentEatenFlag[i]:
                targetColor = self.catchColor[0]
            else:
                targetColor = targetColors[i]
            pg.draw.circle(self.screen, targetColor, [posX, posY], self.targetRadius)
            drawText(self.screen, str(i+1), THECOLORS['black'], [posX - self.targetRadius / 4, posY - self.targetRadius / 4], self.targetRadius)

        for blockPosition, blockColor in zip(blockPositions[:], self.blockColors[:]):
            pg.draw.circle(self.screen, blockColor,
                           [np.int((mappingFun(blockPosition[0]) + self.leaveEdgeSpace) * self.widthLineStepSpace),
                            np.int((mappingFun(blockPosition[1]) + self.leaveEdgeSpace) * self.heightLineStepSpace)],
                           self.blockRadius)

        for playerPosition, playerColor in zip(playerPositions, self.playerColors):
            pg.draw.circle(self.screen, playerColor,
                           [np.int((mappingFun(playerPosition[0]) + self.leaveEdgeSpace) * self.widthLineStepSpace),
                            np.int((mappingFun(playerPosition[1]) + self.leaveEdgeSpace) * self.heightLineStepSpace)],
                           self.playerRadius)
        return self.screen


class DrawNewState():
    def __init__(self, screen, drawBackground, targetColors, playerColors, targetRadius, playerRadius, mapSize):
        self.screen = screen
        self.drawBackground = drawBackground
        self.targetColors = targetColors
        self.playerColors = playerColors
        self.targetRadius = targetRadius
        self.playerRadius = playerRadius
        self.mapSize = mapSize
        self.leaveEdgeSpace = drawBackground.leaveEdgeSpace
        self.widthLineStepSpace = drawBackground.widthLineStepSpace
        self.heightLineStepSpace = drawBackground.heightLineStepSpace

    def __call__(self, targetPositions, playerPositions, currentTime, currentScore):
        self.drawBackground(currentTime, currentScore)
        mappingFun = lambda x: (x + self.mapSize)*(self.drawBackground.gridSize/(2*self.mapSize))  # mapping maxRange to gridSize


        for targetPosition, targetColor in zip(targetPositions[:], self.targetColors[:]):
            pg.draw.circle(self.screen, targetColor,
                           [np.int((mappingFun(targetPosition[0]) + self.leaveEdgeSpace) * self.widthLineStepSpace),
                            np.int((mappingFun(targetPosition[1]) + self.leaveEdgeSpace) * self.heightLineStepSpace)],
                           self.targetRadius)

        # for targetPosition, targetColor in zip(targetPositions[2:], self.targetColors[2:]):
        #     pg.draw.circle(self.screen, targetColor,
        #                    [np.int((mappingFun(targetPosition[0]) + self.leaveEdgeSpace) * self.widthLineStepSpace),
        #                     np.int((mappingFun(targetPosition[1]) + self.leaveEdgeSpace) * self.heightLineStepSpace)],
        #                    self.targetRadius)

        for playerPosition, playerColor in zip(playerPositions, self.playerColors):
            pg.draw.circle(self.screen, playerColor,
                           [np.int((mappingFun(playerPosition[0]) + self.leaveEdgeSpace) * self.widthLineStepSpace),
                            np.int((mappingFun(playerPosition[1]) + self.leaveEdgeSpace) * self.heightLineStepSpace)],
                           self.playerRadius)
        return self.screen


class DrawImageWithJoysticksCheck():
    def __init__(self, screen, joystickList, waitPress=True, showTime=1000):
        self.screen = screen
        self.joystickList = joystickList
        self.screenCenter = (self.screen.get_width() / 2, self.screen.get_height() / 2)
        self.waitPress = waitPress
        self.showTime = showTime

    def __call__(self, image):
        imageRect = image.get_rect()
        imageRect.center = self.screenCenter
        pg.event.set_allowed([pg.KEYDOWN, pg.KEYUP, pg.QUIT])
        self.screen.fill((0, 0, 0))
        self.screen.blit(image, imageRect)
        pg.display.flip()
        pauseList = [True] * len(self.joystickList)
        if self.waitPress:
            while np.any(pauseList):
                pg.time.wait(10)
                for event in pg.event.get(): # User did something
                    if event.type == pg.QUIT: # If user clicked close
                        pauseList = [False] * len(self.joystickList)  # Flag that we are done so we exit this loop
                for joystickId, joystick in enumerate(self.joystickList):
                    joystick.init()
                    value = joystick.get_button(0)
                    # print(value)
                    if value:
                        pauseList[joystickId] = False
                    
                pg.time.wait(10)
        else:
            pg.time.wait(self.showTime)
        return True

class DrawImage():
    def __init__(self, screen, waitPress=True, showTime=1000):
        self.screen = screen
        self.screenCenter = (self.screen.get_width() / 2, self.screen.get_height() / 2)
        self.waitPress = waitPress
        self.showTime = showTime

    def __call__(self, image):
        imageRect = image.get_rect()
        imageRect.center = self.screenCenter
        pause = True
        pg.event.set_allowed([pg.KEYDOWN, pg.KEYUP, pg.QUIT])
        self.screen.fill((0, 0, 0))
        self.screen.blit(image, imageRect)
        pg.display.flip()
        if self.waitPress:
            while pause:
                pg.time.wait(10)
                for event in pg.event.get():
                    if event.type == pg.KEYDOWN and event.key == pg.K_SPACE:
                        pause = False
                    elif event.type == pg.QUIT:
                        pg.quit()
                pg.time.wait(10)
            pg.event.set_blocked([pg.KEYDOWN, pg.KEYUP, pg.QUIT])
        else:
            pg.time.wait(self.showTime)
        return True


class DrawAttributionTrail:
    def __init__(self, screen, playerColors, totalBarLength, barHeight, screenCenter):
        self.screen = screen
        self.playerColors = playerColors
        self.screenCenter = screenCenter
        self.totalBarLength = totalBarLength
        self.barHeight = barHeight

    def __call__(self, attributorId, attributorPercent):
        print(attributorId)
        recipentId = 1 - attributorId
        attributorLen = int(self.totalBarLength * attributorPercent)

        attributorRect = ((self.screenCenter[0] - self.totalBarLength / 2, self.screenCenter[1] - self.barHeight / 2),
                          (attributorLen, self.barHeight))
        recipentRect = (
            (self.screenCenter[0] - self.totalBarLength / 2 + attributorLen, self.screenCenter[1] - self.barHeight / 2),
            (self.totalBarLength - attributorLen, self.barHeight))

        pg.draw.rect(self.screen, self.playerColors[attributorId], attributorRect)
        pg.draw.rect(self.screen, self.playerColors[recipentId], recipentRect)

        pg.display.flip()
        return self.screen


if __name__ == "__main__":
    pg.init()
    screenWidth = 720
    screenHeight = 720
    screen = pg.display.set_mode((screenWidth, screenHeight))
    gridSize = 20
    leaveEdgeSpace = 2
    lineWidth = 2
    backgroundColor = [188, 188, 0]
    lineColor = [255, 255, 255]
    targetColor = [255, 50, 50]
    playerColor = [50, 50, 255]
    targetRadius = 10
    playerRadius = 10
    targetPositionA = [5, 5]
    targetPositionB = [15, 5]
    playerPosition = [10, 15]
    picturePath = os.path.abspath(os.path.join(os.getcwd(), os.pardir)) + '/Pictures/'
    restImage = pg.image.load(picturePath + 'rest.png')
    currentTime = 138456
    currentScore = 5
    textColorTuple = (255, 50, 50)
    drawBackground = DrawBackground(screen, gridSize, leaveEdgeSpace, backgroundColor, lineColor, lineWidth,
                                    textColorTuple)
    drawNewState = DrawNewState(screen, drawBackground, targetColor, playerColor, targetRadius, playerRadius)
    drawImage = DrawImage(screen)
    drawBackground(currentTime, currentScore)
    pg.time.wait(5000)
    pg.quit()
