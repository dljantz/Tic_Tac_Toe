# Tic Tac Toe adaptation created by David Jantz, May 2019

import pygame, sys, random, math, time
from pygame.locals import *

FPS = 60
WINDOWSIZE = 700
MARGIN = 70
BOARDSIZE = WINDOWSIZE - MARGIN * 2
SPOTSIZE = (WINDOWSIZE - MARGIN * 2) / 3 # divide by three because the board is 3 spots wide

WHITE =     (255, 255, 255)
BLACK =     (  0,   0,   0)
PINK =      (255, 130, 130)
GREEN =     ( 20, 100,  20)
DARKGREEN = ( 10,  40,  10)
PURPLE =    (170, 120, 255)
TRANSPARENT = (255, 255, 255, 0) # needed for fading stuff in and out

BGCOLOR = GREEN
BOARDCOLOR = WHITE

X = 1 # assigning numbers to X and O helps check for winners. Empty spots on the board are 0
O = -1

def main(): # lots of boring initial stuff, plus a while loop to repeat the game
    pygame.init()
    pygame.display.set_caption("Tic Tac Toe adaptation by David Jantz")
    
    global SCREEN, SCREEN2, SCREEN3, SMALLFONT, MEDIUMFONT, BIGFONT, CLOCK
    SCREEN = pygame.display.set_mode((WINDOWSIZE, WINDOWSIZE))
    SCREEN2 = SCREEN.convert_alpha()
    SCREEN3 = SCREEN.convert_alpha()
    SMALLFONT = pygame.font.Font('freesansbold.ttf', 30)
    MEDIUMFONT = pygame.font.Font('freesansbold.ttf', 50)
    BIGFONT = pygame.font.Font('freesansbold.ttf', 80)
    CLOCK = pygame.time.Clock()
    
    while True: # endless rounds of tic tac toe until player exits out.
        playGame()
        gameOverScreen()

def playGame(): # the main event
    playMode = startScreen() # playMode is an integer -- the number of people playing. 1 means it's against the computer.
    
    # some variable definitions -- some just need to exist from the start so the code doesn't break
    board = [[0, 0, 0], [0, 0, 0], [0, 0, 0]] # 2D list of board locations
    fadeValues = [[0, 0, 0], [0, 0, 0], [0, 0, 0]] # 2D list of "fade values" -- how transparent the pieces on the board are. Range from 0 to 255.
    whoseTurn = X
    mouseCoords = (0, 0)
    potentialSpot = None
    winningLineFadeTarget = 0
    winningLineTransparency = 0
    
    while True:
        # if you're playing against the computer, it's the computer's turn, and the game isn't over...
        if playMode == 1 and whoseTurn == O and winningLine == None:
            outcome, board = computerAddsPiece(board, whoseTurn, 0)
            whoseTurn = X
        
        # event handling
        for event in pygame.event.get():
            checkForTerminate(event) # Escape button or exited out
            if event.type == MOUSEBUTTONDOWN and potentialSpot != None: # if mouseCoords are on a valid location, add a piece there.
                fadeValues = resetFadeValues(board, fadeValues) # when you click, all empty spots on the board become transparent.
                board = addPiece(board, potentialSpot, whoseTurn)
                if whoseTurn == X: # if a piece was added, change whose turn it is.
                    whoseTurn = O
                else:
                    whoseTurn = X
                potentialSpot = isValidSpot(mouseCoords, board) # do this at the end because otherwise you can change the spot that was just played if you haven't moved the mouse.
            elif event.type == MOUSEMOTION:
                mouseCoords = event.pos # every time the mouse is moved, update its location.
                potentialSpot = isValidSpot(mouseCoords, board) # constantly updating location of mouse in board coordinates, but only for open slots
        
        # end-of-game handling
        winningLine, winner = isGameOver(board, X)
        if winningLine == None:
            winningLine, winner = isGameOver(board, O)
        
        if winningLine != None: # if the game is over
            potentialSpot = None # hovering the mouse over empty spots doesn't do anything now that the game is over.
            timeDelay = time.time() - recentTime
            if int(timeDelay) % 2 == 0: # an even number of seconds since you won sets the line to opaque, an odd number sets it to translucent. This makes it fade in and out.
                winningLineFadeTarget = 255
            else:
                winningLineFadeTarget = 0
            if timeDelay > 5: # back to main() 5 seconds after the game is over.
                return
        else:
            recentTime = time.time() # constantly update recentTime if the game is still being played.
        
        #draw all the schtuff to the screen
        SCREEN.fill(BGCOLOR)
        SCREEN2.fill(TRANSPARENT)
        SCREEN3.fill(TRANSPARENT)
        drawBoard() # just the four lines that make the board, not the pieces.
        fadeValues = drawPermanentPieces(board, fadeValues) # Passing fadeValues up and down was a pain, but it kept it from being a global variable.
        fadeValues = drawShadowPieces(board, fadeValues, potentialSpot, whoseTurn)
        winningLineTransparency = drawWinningLine(winningLine, winningLineFadeTarget, winningLineTransparency)
        SCREEN.blit(SCREEN2, (0, 0))
        SCREEN.blit(SCREEN3, (0, 0))
        pygame.display.update()
        CLOCK.tick(FPS)

def startScreen():
    # animated stuff in the style of the game -- fade the title in and out on a board
    instructions1 = SMALLFONT.render('Press "C" to play against the computer.', True, DARKGREEN)
    instructions2 = SMALLFONT.render('Press "H" if you are playing against another human.', True, DARKGREEN)
    instructions1Rect = instructions1.get_rect()
    instructions2Rect = instructions2.get_rect()
    instructions1Rect.midtop = (int(WINDOWSIZE / 2), 10)
    instructions2Rect.midbottom = (int(WINDOWSIZE / 2), WINDOWSIZE - 10)
    
    ticSpot = None
    tacSpot = None
    toeSpot = None
    ticFadeValue = 0
    tacFadeValue = 0
    toeFadeValue = 0
    elapsedTime = 1000 # just has to be greater than 5
    animationTime = 8 # Number of seconds it takes to complete one animation cycle.
    
    while True:
        # event handling -- quit events, key presses
        for event in pygame.event.get():
            checkForTerminate(event)
            if event.type == KEYDOWN:
                if event.key == K_c:
                    return 1
                elif event.key == K_h:
                    return 2
        
        # Make the words 'tic tac toe' fade in and out on the board
        if elapsedTime > animationTime: # every 8 seconds...
            ticSpot, tacSpot, toeSpot = getRandomStartScreen() # A random set of 3 spots in a row.
            ticSpot = getPixelCoords(ticSpot[0], ticSpot[1])
            tacSpot = getPixelCoords(tacSpot[0], tacSpot[1])
            toeSpot = getPixelCoords(toeSpot[0], toeSpot[1])
            oldTime = time.time()
        elapsedTime = time.time() - oldTime
        
        #draw all the schtuff to the screen
        SCREEN.fill(BGCOLOR)
        SCREEN2.fill(TRANSPARENT)
        drawBoard()
        # Below, I do some funky little calculations in the function call to offset when the words fade in on the screen.
        #   There are 8 discrete chunks of the animation, so they are offset by eighths of the animation duration.
        ticFadeValue = drawTicTacAndToe(elapsedTime, animationTime, ticFadeValue, ticSpot, 'TIC')
        tacFadeValue = drawTicTacAndToe(elapsedTime - animationTime * 0.125, animationTime, tacFadeValue, tacSpot, 'TAC')
        toeFadeValue = drawTicTacAndToe(elapsedTime - animationTime * 0.250, animationTime, toeFadeValue, toeSpot, 'TOE')
        SCREEN.blit(SCREEN2, (0, 0))
        SCREEN.blit(instructions1, instructions1Rect)
        SCREEN.blit(instructions2, instructions2Rect)
        pygame.display.update()
        CLOCK.tick(FPS)

def getRandomStartScreen(): # gets a random set of 3 spots in a row to run the animation.
    while True: # while loop runs until it randomly finds a combination with 3 in a row.
        tic = getRandomSpot(None, None, None)
        tac = getRandomSpot(tic, None, None)
        toe = getRandomSpot(tic, tac, None)
        
        temporaryBoard = [[0, 0, 0], [0, 0, 0], [0, 0, 0]] # Create an empty board...
        temporaryBoard[tic[0]][tic[1]] = X # fill that board with X's corresponding to the randomly generated tuples
        temporaryBoard[tac[0]][tac[1]] = X
        temporaryBoard[toe[0]][toe[1]] = X
        
        winningLine, winner = isGameOver(temporaryBoard, X)  # use preexisting function to see if X "won". If not, try again.
        if winner == X: # (didn't actually need to get the winningLine variable, just needed to unpack returned values from isGameOver().
            return tic, tac, toe

def getRandomSpot(tic, tac, toe): # generates a random board location for startScreen().
    while True:
        randomX = random.randint(0, 2)
        randomY = random.randint(0, 2)
        # if the randomly selected coordinates are already taken, keep searching. Otherwise, use them.
        if tic != (randomX, randomY) and tac != (randomX, randomY) and toe != (randomX, randomY):
            return (randomX, randomY)

def drawTicTacAndToe(elapsedTime, animationTime, fadeValue, pixCoords, word): # draws one word to the screen -- fades it in and out.
    fadeTime = animationTime / 8 # there are 8 "chunks" to the animation. The words each take one "chunk" to fade in or out.
    if 0 < elapsedTime < fadeTime * 2: # if we are at the beginning of the animation...
        fadeValue = fadeInOut(fadeValue, 255, fadeTime) # make it fade in.
    elif elapsedTime > animationTime / 2: # if we are at the end of the animation...
        fadeValue = fadeInOut(fadeValue, 0, fadeTime) # make it fade out.
    
    text = BIGFONT.render(word, True, PURPLE)
    textRect = text.get_rect()
    pixX = int(pixCoords[0] - textRect[2] / 2) # pixX at the center of the word
    pixY = int(pixCoords[1] - textRect[3] / 2) # pixY at the center of the word
    pixCoords = (pixX, pixY)
    
    # Had to make an extra surface to enable fading in and out.
    extraSurf = pygame.Surface((textRect[2], textRect[3]))
    extraSurf.fill(BGCOLOR)
    extraSurf.blit(text, (0, 0))
    extraSurf.set_alpha(fadeValue)
    SCREEN.blit(extraSurf, pixCoords)
    
    return fadeValue
    
def gameOverScreen(): # maybe I'll use this at some point...
    # set variables if needed
    # while loop
    # draw stuff to screen
    return

def isValidSpot(mouseCoords, board): # Checks to see if the mouse is a) over the board and b) over an empty spot.
    boardX, boardY = getBoardCoords(mouseCoords)
    if boardX != None and boardY != None: # if the mouse is actually over the board...
        if board[boardX][boardY] == 0: # and that spot is unoccupied...
            return boardX, boardY # return those board coordinates.
    return None # otherwise, don't return anything

def getBoardCoords(mouseCoords): # Converts mouse coordinates to board coordinates.
    boardX = (mouseCoords[0] - MARGIN) / SPOTSIZE
    boardY = (mouseCoords[1] - MARGIN) / SPOTSIZE
    # only return board coordinates if the mouse is over the board.
    if 0 < boardX < 3 and 0 < boardY < 3:
        return int(boardX), int(boardY)
    else:
        return None, None

def getPixelCoords(boardX, boardY): # Converts board coordinates to pixel coordinates.
    pixelX = int(boardX * SPOTSIZE + SPOTSIZE / 2 + MARGIN)
    pixelY = int(boardY * SPOTSIZE + SPOTSIZE / 2 + MARGIN)
    return pixelX, pixelY

def addPiece(board, chosenSpot, whoseTurn): # adds an X or O to the list of board locations.
    x = chosenSpot[0]
    y = chosenSpot[1]
    board[x][y] = whoseTurn
    return board

def drawBoard(): # Draws the board (just the four lines, not the pieces)
    linethickness = 10
    # all the values needed to draw vertical lines.
    verticalLeft = MARGIN + SPOTSIZE
    verticalRight = WINDOWSIZE - verticalLeft
    verticalTop = MARGIN
    verticalBottom = WINDOWSIZE - MARGIN
    
    # syntactic sugar -- could use vertical values for horizontal lines directly, but this keeps things non-confusing.
    horizontalTop = verticalLeft
    horizontalBottom = verticalRight
    horizontalLeft = verticalTop
    horizontalRight = verticalBottom
    
    pygame.draw.line(SCREEN, BOARDCOLOR, (verticalLeft, verticalTop), (verticalLeft, verticalBottom), linethickness) # left vertical line
    pygame.draw.line(SCREEN, BOARDCOLOR, (verticalRight, verticalTop), (verticalRight, verticalBottom), linethickness) # right vertical line
    pygame.draw.line(SCREEN, BOARDCOLOR, (horizontalLeft, horizontalTop), (horizontalRight, horizontalTop), linethickness) # top horizontal line
    pygame.draw.line(SCREEN, BOARDCOLOR, (horizontalLeft, horizontalBottom), (horizontalRight, horizontalBottom), linethickness) # bottom horizontal line

def drawPermanentPieces(board, fadeValues): # Draws all the permanent X and O pieces to the screen.
    spotIsChosen = True
    fadeTarget = 255
    fadeTime = 1.5
    for boardX in range(3): # for all the columns...
        for boardY in range(3): # ... and all the rows...
            if board[boardX][boardY] == X:
                fadeValues = drawX(boardX, boardY, fadeValues, spotIsChosen, fadeTarget, fadeTime)
            elif board[boardX][boardY] == O:
                fadeValues = drawO(boardX, boardY, fadeValues, spotIsChosen, fadeTarget, fadeTime)
    return fadeValues # have to return this list up so it's stored till the next iteration of the playGame() while loop.

def drawShadowPieces(board, fadeValues, potentialSpot, whoseTurn): # Draws all the shadow pieces to the screen.
    spotIsChosen = False
    fadeTime = 2
    for boardX in range(3):
        for boardY in range (3):
            if (boardX, boardY) == potentialSpot: # if the mouse is over an empty spot, fade in a shadow piece.
                fadeTarget = 100 # A nice translucent value
                if whoseTurn == X:
                    fadeValues = drawX(boardX, boardY, fadeValues, spotIsChosen, fadeTarget, fadeTime)
                elif whoseTurn == O:
                    fadeValues = drawO(boardX, boardY, fadeValues, spotIsChosen, fadeTarget, fadeTime)
            elif board[boardX][boardY] == 0: # if the mouse is NOT over that spot and the spot is empty, fade out the shadow piece.
                fadeTarget = 0 # completely transparent
                if whoseTurn == X:
                    fadeValues = drawX(boardX, boardY, fadeValues, spotIsChosen, fadeTarget, fadeTime)
                elif whoseTurn == O:
                    fadeValues = drawO(boardX, boardY, fadeValues, spotIsChosen, fadeTarget, fadeTime)
    return fadeValues

def drawX(boardX, boardY, fadeValues, spotIsChosen, fadeTarget, fadeTime): # draws permanent pieces or shadow pieces to the board, depending on input values.
    pieceSize = SPOTSIZE / 2.5 # 2.5 chosen to make the pieces slightly smaller than the spot. A value of 2 would make them fill it completely.
    pixelX, pixelY = getPixelCoords(boardX, boardY)
    transparency = fadeValues[boardX][boardY] #syntactic sugar
    
    # pixel coordinates from getPixelCoords() are in the dead center of that spot on the board, hence all the subtracting and adding.
    left = pixelX - pieceSize
    bottom = pixelY + pieceSize
    right = pixelX + pieceSize
    top = pixelY - pieceSize
    
    transparency = fadeInOut(transparency, fadeTarget, fadeTime) # adjust the transparency slighly to get fade in / out effect.
    XColor = (PURPLE[0], PURPLE[1], PURPLE[2], transparency)
    
    # white X in the background to make it flash white before fading in.
    if spotIsChosen:
        pygame.draw.line(SCREEN, WHITE, (left, bottom), (right, top), 20)
        pygame.draw.line(SCREEN, WHITE, (left, top), (right, bottom), 20)
    
    pygame.draw.line(SCREEN2, XColor, (left, bottom), (right, top), 20)
    pygame.draw.line(SCREEN2, XColor, (left, top), (right, bottom), 20)
    
    fadeValues[boardX][boardY] = transparency # returning syntactic sugar variable to playGame()
    return fadeValues

def drawO(boardX, boardY, fadeValues, spotIsChosen, fadeTarget, fadeTime): # same deal as drawX() -- does shadow pieces or permanent depending on inputs.
    radius = int(SPOTSIZE / 2.5)
    pixelCoords = getPixelCoords(boardX, boardY)

    transparency = fadeValues[boardX][boardY] #syntactic sugar
    
    transparency = fadeInOut(transparency, fadeTarget, fadeTime) # adjust transparency slightly to get fade in / out effect.
    OColor = (PINK[0], PINK[1], PINK[2], transparency)
    
    # make the piece flash white
    if spotIsChosen:
        pygame.draw.circle(SCREEN, WHITE, pixelCoords, radius)
    
    pygame.draw.circle(SCREEN2, OColor, pixelCoords, radius)
    pygame.draw.circle(SCREEN2, BGCOLOR, pixelCoords, radius - 15)
    
    fadeValues[boardX][boardY] = transparency # returning syntactic sugar variable to playGame()
    return fadeValues

def fadeInOut(fadeValue, fadeTarget, fadeTime): # changes transparency values slowly to get fade in / out effect.
    increment = round(255 / FPS / fadeTime) # A full fade from 0 to 255 would take fadeTime seconds to complete.
    if fadeValue < fadeTarget: # if we are in the process of fading in...
        fadeValue += increment
    elif fadeValue > fadeTarget: # if we are in the process of fading out...
        fadeValue -= increment
    
    if abs(fadeValue - fadeTarget) < increment: # if we're pretty close, just jump to fadeTarget. Helps prevent errors like going past 255.
        fadeValue = fadeTarget
    
    return fadeValue

def resetFadeValues(board, fadeValues): # resets the transparency values of every empty spot to 0.
    for boardX in range(3):
        for boardY in range(3):
            if board[boardX][boardY] == 0:
                fadeValues[boardX][boardY] = 0
    return fadeValues

def isGameOver(board, player): # checks all possible ways to win, returns board coordinate tuples to describe where to draw the winning line.
    if sum(board[0]) == player * 3: # first column
        return ((0, -0.5), (0, 2.5)), player
    elif sum(board[1]) == player * 3: # second column
        return ((1, -0.5), (1, 2.5)), player
    elif sum(board[2]) == player * 3: # third column
        return ((2, -0.5), (2, 2.5)), player
    elif board[0][0] + board[1][0] + board[2][0] == player * 3: # first row
        return ((-0.5, 0), (2.5, 0)), player
    elif board[0][1] + board[1][1] + board[2][1] == player * 3: # second row
        return ((-0.5, 1), (2.5, 1)), player
    elif board[0][2] + board[1][2] + board[2][2] == player * 3: # third row
        return ((-0.5, 2), (2.5, 2)), player
    elif board[0][0] + board[1][1] + board[2][2] == player * 3: # diagonal top left to bottom right
        return ((-0.5, -0.5), (2.5, 2.5)), player
    elif board[0][2] + board[1][1] + board[2][0] == player * 3: # diagonal bottom left to top right
        return ((-0.5, 2.5), (2.5, -0.5)), player
    elif 0 not in board[0] and 0 not in board[1] and 0 not in board[2]: # filled board, no winners
        return 'tieGame', None
    else:
        return None, None

def drawWinningLine(winningLine, fadeTarget, transparency): # draws a line over the winning 3 in a row combo.
    if type(winningLine) == tuple: # winningLine is a tuple of tuples, so we have to dig a bit to find the integer values.
        lineStartX = winningLine[0][0]
        lineStartY = winningLine[0][1]
        lineEndX = winningLine[1][0]
        lineEndY = winningLine[1][1]
        
        lineStart = getPixelCoords(lineStartX, lineStartY)
        lineEnd = getPixelCoords(lineEndX, lineEndY)
        
        transparency = fadeInOut(transparency, fadeTarget, 1)
        lineColor = (0, 0, 0, transparency)
        
        pygame.draw.line(SCREEN3, lineColor, lineStart, lineEnd, 20)
        return transparency
    return 0

def computerAddsPiece(board, whoseTurn, depth): # the whole point of this program -- David's first "AI" function!!
    # This chunk of code can be used to add a piece randomly if you want.
#    messingAround = True
#    while messingAround:
#        randomX = random.randint(0, 2)
#        randomY = random.randint(0, 2)
#        if board[randomX][randomY] == 0:
#            board[randomX][randomY] = O
#            messingAround = False

    # base case: X hypothetically wins    
    winningLine, winner = isGameOver(board, X)
    if winner == X:
        return -10, board # return a negative value -- computer lost.
    
    # base case: O hypothetically wins
    winningLine, winner = isGameOver(board, O)
    if winner == O:
        return 10, board # return a positive value -- computer won
    
    # base case: the board is full, tie game
    elif winningLine == 'tieGame':
        return 0, board # a neutral value to denote a tie outcome

    # recursive case: the board has empty spots
    allOutcomes = []
    potentialBoards = []
    tempBoard = copyBoard(board)
    for boardX in range(len(board)): # for every spot on the board...
        for boardY in range(len(board)):
            if board[boardX][boardY] == 0: # ... if that spot is empty, try it and see what the outcome would be.
                tempBoard[boardX][boardY] = whoseTurn
                outcome, throwAwayVariable = computerAddsPiece(tempBoard, whoseTurn * -1, depth + 1) # recursion happens here. the second variable is switching whose turn it is for the next layer down in the tree.
                allOutcomes.append(outcome) # add the outcome value to a list of potential outcomes.
                potentialBoards.append(tempBoard) # add the potenial board to a list.
                tempBoard = copyBoard(board)
    
    if depth == 0:
        if 10 in allOutcomes:
            print("Computer guaranteed to win!")
        elif 0 in allOutcomes:
            print("Tie guaranteed unless you screw up.")
        elif -10 in allOutcomes:
            print("You're guaranteed to win if you play right.")
    
    # Minimax: after finishing the for loop of empy spots, choose either the maximum or minimum outcome value and its associated board (depending on whose turn it is).
    for i in range(len(allOutcomes)):
        if allOutcomes[i] == -10 * whoseTurn:
            #print(allOutcomes[i], potentialBoards[i])
            return allOutcomes[i], potentialBoards[i]
    for i in range(len(allOutcomes)):
        if allOutcomes[i] == 0:
            return allOutcomes[i], potentialBoards[i]
    for i in range(len(allOutcomes)):
        if allOutcomes[i] == 10 * whoseTurn:
            #print(allOutcomes[i], potentialBoards[i], whoseTurn)
            return allOutcomes[i], potentialBoards[i]

def copyBoard(board): # copies the 2D list by creating a new object rather than creating a reference to the same object as the old variable.
    tempBoard = [[0, 0, 0], [0, 0, 0], [0, 0, 0]]
    for boardX in range(len(board)):
        for boardY in range(len(board)):
            tempBoard[boardX][boardY] = board[boardX][boardY]
    return tempBoard

def checkForTerminate(event): #check for any quit events, then run terminate()
    if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
        terminate()
        
def terminate():
    pygame.quit()
    sys.exit()
    
if __name__ == '__main__':
    main()
