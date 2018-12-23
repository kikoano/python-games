# Wormy (a Nibbles clone)
# By Al Sweigart al@inventwithpython.com
# http://inventwithpython.com/pygame
# Released under a "Simplified BSD" license

import random
import pygame
import sys
import time
from pygame.locals import *

FPS = 10
WINDOWWIDTH = 640
WINDOWHEIGHT = 480
CELLSIZE = 20
assert WINDOWWIDTH % CELLSIZE == 0, "Window width must be a multiple of cell size."
assert WINDOWHEIGHT % CELLSIZE == 0, "Window height must be a multiple of cell size."
CELLWIDTH = int(WINDOWWIDTH / CELLSIZE)
CELLHEIGHT = int(WINDOWHEIGHT / CELLSIZE)

#             R    G    B
WHITE = (255, 255, 255)
BLACK = (0,   0,   0)
RED = (255,   0,   0)
GREEN = (0, 255,   0)
DARKGREEN = (0, 155,   0)
DARKGRAY = (40,  40,  40)
BLUE = (0,   0, 255)
BGCOLOR = BLACK

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'

HEAD = 0  # syntactic sugar: index of the worm's head

CHANGEDIR = 0.8


def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT

    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT = pygame.font.Font('freesansbold.ttf', 18)
    pygame.display.set_caption('Wormy')

    showStartScreen()
    while True:
        runGame()
        showGameOverScreen()


def runGame():
    # Set a random start point.
    startx = random.randint(5, CELLWIDTH - 6)
    starty = random.randint(5, CELLHEIGHT - 6)
    wormCoords = [{'x': startx,     'y': starty},
                  {'x': startx - 1, 'y': starty},
                  {'x': startx - 2, 'y': starty}]
    direction = RIGHT

    # Start the apple in a random place.
    apple = getRandomLocation()
    score = 0
    startTime = pygame.time.get_ticks()
    passedTime = 0
    timer = pygame.time.Clock()
    # Computer worms
    npcWorm = []
    turn = False
    flashItems = []
    lastFlashItems = passedTime/1000
    while True:  # main game loop

        for event in pygame.event.get():  # event handling loop
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if (event.key == K_LEFT or event.key == K_a) and direction != RIGHT:
                    direction = LEFT
                elif (event.key == K_RIGHT or event.key == K_d) and direction != LEFT:
                    direction = RIGHT
                elif (event.key == K_UP or event.key == K_w) and direction != DOWN:
                    direction = UP
                elif (event.key == K_DOWN or event.key == K_s) and direction != UP:
                    direction = DOWN
                elif event.key == K_ESCAPE:
                    terminate()

        # check if the worm has hit itself or the edge
        if wormCoords[HEAD]['x'] == -1 or wormCoords[HEAD]['x'] == CELLWIDTH or wormCoords[HEAD]['y'] == -1 or wormCoords[HEAD]['y'] == CELLHEIGHT:
            return  # game over
        for wormBody in wormCoords[1:]:
            if wormBody['x'] == wormCoords[HEAD]['x'] and wormBody['y'] == wormCoords[HEAD]['y']:
                return  # game over

        # check if worm has eaten an apply
        # check if worm has eaten an flashItem
        for item in flashItems:
            if wormCoords[HEAD]['x'] == item['x'] and wormCoords[HEAD]['y'] == item['y']:
                # Addds extra 2 points
                score += 2
                # Delete the eaten item
                flashItems.remove(item)
        if wormCoords[HEAD]['x'] == apple['x'] and wormCoords[HEAD]['y'] == apple['y']:
            # don't remove worm's tail segment
            apple = getRandomLocation()  # set a new apple somewhere
            score += 1
        else:
            # check if player worm touched computer worm
            if npcWorm:
                touch = False
                for wormBody in npcWorm[1:]:
                    if wormBody['x'] == wormCoords[HEAD]['x'] and wormBody['y'] == wormCoords[HEAD]['y']:
                        touch = True
                        break
                if not touch:
                    del wormCoords[-1]
            else:
                del wormCoords[-1]  # remove worm's tail segment

        # move the worm by adding a segment in the direction it is moving
        if direction == UP:
            newHead = {'x': wormCoords[HEAD]['x'], 'y': wormCoords[HEAD]['y'] - 1}
        elif direction == DOWN:
            newHead = {'x': wormCoords[HEAD]['x'], 'y': wormCoords[HEAD]['y'] + 1}
        elif direction == LEFT:
            newHead = {'x': wormCoords[HEAD]['x'] - 1, 'y': wormCoords[HEAD]['y']}
        elif direction == RIGHT:
            newHead = {'x': wormCoords[HEAD]['x'] + 1, 'y': wormCoords[HEAD]['y']}
        wormCoords.insert(0, newHead)

        # Adds random flashing items that last 5s
        if (passedTime/1000) - lastFlashItems > 5:
            lastFlashItems = passedTime/1000
            flashItems.clear()
            for i in range(3):
                flashItems.append(getRandomLocation())
        # After 45 seconds from the beginning of the game add computer worm
        # Disabled self hit on computer worm and added smart turn near edge so computer worm is challenging to the player
        if (passedTime/1000) > 45 and not npcWorm:
            computerDirection = random.choice((UP, DOWN, LEFT, RIGHT))
            startx = random.randint(5, CELLWIDTH - 6)
            starty = random.randint(5, CELLHEIGHT - 6)
            npcWorm = [{'x': startx,     'y': starty}, {'x': startx - 1, 'y': starty}, {'x': startx - 2, 'y': starty}]
        if npcWorm:
            # check if computer worm touched player worm
            touch = False
            for wormBody in wormCoords[1:]:
                if wormBody['x'] == npcWorm[HEAD]['x'] and wormBody['y'] == npcWorm[HEAD]['y']:
                    touch = True
                    break
            if not touch:
                del npcWorm[-1]
            # Random direction
            if random.random() > CHANGEDIR:
                while True:
                    tempDir = random.choice((UP, DOWN, LEFT, RIGHT))
                    if (tempDir != computerDirection) and not(tempDir == LEFT and computerDirection == RIGHT) and not(tempDir == RIGHT and computerDirection == LEFT) and not(tempDir == UP and computerDirection == DOWN) and not(tempDir == DOWN and computerDirection == UP):
                        computerDirection = tempDir
                        break
            # Smart self turn if near edge
            if turn:
                if npcWorm[HEAD]['x'] == 0:
                    computerDirection = RIGHT
                if npcWorm[HEAD]['x'] == CELLWIDTH-1:
                    computerDirection = LEFT
                if npcWorm[HEAD]['y'] == 0:
                    computerDirection = DOWN
                if npcWorm[HEAD]['y'] == CELLHEIGHT-1:
                    computerDirection = UP
                turn = False
            else:
                if npcWorm[HEAD]['x'] == 0:
                    if npcWorm[HEAD]['y'] == 0:
                        computerDirection = RIGHT
                    else:
                        computerDirection = UP
                        turn = True
                elif npcWorm[HEAD]['x'] == CELLWIDTH-1:
                    if npcWorm[HEAD]['y'] == CELLHEIGHT-1:
                        computerDirection = LEFT
                    else:
                        turn = True
                        computerDirection = DOWN
                elif npcWorm[HEAD]['y'] == 0:
                    if npcWorm[HEAD]['x'] == CELLWIDTH-1:
                        computerDirection = DOWN
                    else:
                        computerDirection = RIGHT
                        turn = True
                elif npcWorm[HEAD]['y'] == CELLHEIGHT-1:
                    if npcWorm[HEAD]['x'] == 0:
                        computerDirection = UP
                    else:
                        computerDirection = LEFT
                        turn = True
            # Move computer worm
            if computerDirection == UP:
                newHead = {'x': npcWorm[HEAD]['x'], 'y': npcWorm[HEAD]['y'] - 1}
            elif computerDirection == DOWN:
                newHead = {'x': npcWorm[HEAD]['x'], 'y': npcWorm[HEAD]['y'] + 1}
            elif computerDirection == LEFT:
                newHead = {'x': npcWorm[HEAD]['x'] - 1, 'y': npcWorm[HEAD]['y']}
            elif computerDirection == RIGHT:
                newHead = {'x': npcWorm[HEAD]['x'] + 1, 'y': npcWorm[HEAD]['y']}
            npcWorm.insert(0, newHead)
        DISPLAYSURF.fill(BGCOLOR)
        drawGrid()
        # Draw computer worm if exists
        if npcWorm:
            drawWorm(npcWorm, BLUE)
        drawWorm(wormCoords)
        drawApple(apple)
        if flashItems:
            for item in flashItems:
                drawFlashItem(item)
        drawScore(score)
        pygame.display.update()
        FPSCLOCK.tick(FPS)
        # Calculate passedTime
        passedTime = pygame.time.get_ticks() - startTime


def drawPressKeyMsg():
    pressKeySurf = BASICFONT.render('Press a key to play.', True, DARKGRAY)
    pressKeyRect = pressKeySurf.get_rect()
    pressKeyRect.topleft = (WINDOWWIDTH - 200, WINDOWHEIGHT - 30)
    DISPLAYSURF.blit(pressKeySurf, pressKeyRect)


def checkForKeyPress():
    if len(pygame.event.get(QUIT)) > 0:
        terminate()

    keyUpEvents = pygame.event.get(KEYUP)
    if len(keyUpEvents) == 0:
        return None
    if keyUpEvents[0].key == K_ESCAPE:
        terminate()
    return keyUpEvents[0].key


def showStartScreen():
    titleFont = pygame.font.Font('freesansbold.ttf', 100)
    titleSurf1 = titleFont.render('Wormy!', True, WHITE, DARKGREEN)
    titleSurf2 = titleFont.render('Wormy!', True, GREEN)

    degrees1 = 0
    degrees2 = 0
    while True:
        DISPLAYSURF.fill(BGCOLOR)
        rotatedSurf1 = pygame.transform.rotate(titleSurf1, degrees1)
        rotatedRect1 = rotatedSurf1.get_rect()
        rotatedRect1.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2)
        DISPLAYSURF.blit(rotatedSurf1, rotatedRect1)

        rotatedSurf2 = pygame.transform.rotate(titleSurf2, degrees2)
        rotatedRect2 = rotatedSurf2.get_rect()
        rotatedRect2.center = (WINDOWWIDTH / 2, WINDOWHEIGHT / 2)
        DISPLAYSURF.blit(rotatedSurf2, rotatedRect2)

        drawPressKeyMsg()

        if checkForKeyPress():
            pygame.event.get()  # clear event queue
            return
        pygame.display.update()
        FPSCLOCK.tick(FPS)
        degrees1 += 3  # rotate by 3 degrees each frame
        degrees2 += 7  # rotate by 7 degrees each frame


def terminate():
    pygame.quit()
    sys.exit()


def getRandomLocation():
    return {'x': random.randint(0, CELLWIDTH - 1), 'y': random.randint(0, CELLHEIGHT - 1)}


def showGameOverScreen():
    # Fonts
    gameOverFont = pygame.font.Font('freesansbold.ttf', 150)
    menuFont = pygame.font.Font('freesansbold.ttf', 30)

    # Text Surfs
    gameSurf = gameOverFont.render('Game', True, WHITE)
    overSurf = gameOverFont.render('Over', True, WHITE)
    startOverSurf = menuFont.render('Start from the beginning', True, WHITE)
    quitSurf = menuFont.render('Quit', True, WHITE)

    # Rects
    gameRect = gameSurf.get_rect()
    overRect = overSurf.get_rect()
    startOverRect = startOverSurf.get_rect()
    quitRect = quitSurf.get_rect()

    # Rects positions
    gameRect.midtop = (WINDOWWIDTH / 2, 10)
    overRect.midtop = (WINDOWWIDTH / 2, gameRect.height + 10 + 25)
    startOverRect.midtop = (WINDOWWIDTH / 2, gameRect.height + 200)
    quitRect.midtop = (WINDOWWIDTH / 2, gameRect.height + 250)

    # Draw on screen
    DISPLAYSURF.blit(gameSurf, gameRect)
    DISPLAYSURF.blit(overSurf, overRect)
    DISPLAYSURF.blit(startOverSurf, startOverRect)
    DISPLAYSURF.blit(quitSurf, quitRect)

    pygame.display.update()
    while True:
        checkForKeyPress()
        for event in pygame.event.get():  # event handling loop
            # Mouse clicked
            if event.type == MOUSEBUTTONUP:
                
                if startOverRect.collidepoint(event.pos):
                    return
                if quitRect.collidepoint(event.pos):
                    terminate()


def drawScore(score):
    scoreSurf = BASICFONT.render('Score: %s' % (score), True, WHITE)
    scoreRect = scoreSurf.get_rect()
    scoreRect.topleft = (WINDOWWIDTH - 120, 10)
    DISPLAYSURF.blit(scoreSurf, scoreRect)


def drawWorm(wormCoords, color=GREEN):
    for coord in wormCoords:
        x = coord['x'] * CELLSIZE
        y = coord['y'] * CELLSIZE
        wormSegmentRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
        pygame.draw.rect(DISPLAYSURF, DARKGREEN, wormSegmentRect)
        wormInnerSegmentRect = pygame.Rect(x + 4, y + 4, CELLSIZE - 8, CELLSIZE - 8)
        pygame.draw.rect(DISPLAYSURF, color, wormInnerSegmentRect)


def drawApple(coord):
    x = coord['x'] * CELLSIZE
    y = coord['y'] * CELLSIZE
    appleRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
    pygame.draw.rect(DISPLAYSURF, RED, appleRect)


def drawFlashItem(coord):
    x = coord['x'] * CELLSIZE
    y = coord['y'] * CELLSIZE
    appleRect = pygame.Rect(x, y, CELLSIZE, CELLSIZE)
    if round(time.time(), 1) * 10 % 2 == 1:
        pygame.draw.rect(DISPLAYSURF, WHITE, appleRect)


def drawGrid():
    for x in range(0, WINDOWWIDTH, CELLSIZE):  # draw vertical lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (x, 0), (x, WINDOWHEIGHT))
    for y in range(0, WINDOWHEIGHT, CELLSIZE):  # draw horizontal lines
        pygame.draw.line(DISPLAYSURF, DARKGRAY, (0, y), (WINDOWWIDTH, y))


if __name__ == '__main__':
    main()
