import numpy as np
from random import randint
import pygame
import pyperclip
from time import time


settings = {0: ([9, 9], 10),
            1: ([16, 16], 40),
            2: ([16, 30], 99)}

numbers = {1.: '1️⃣',
           2.: '2️⃣',
           3.: '3️⃣',
           4.: '4️⃣',
           5.: '5️⃣',
           6.: '6️⃣',
           7.: '7️⃣',
           8.: '8️⃣'}


def keyEncrypt(binary):
    def binaryToDecimal(binary):
        decimal, i, n = 0, 0, 0
        while binary != 0:
            dec = binary % 10
            decimal = decimal + dec * pow(2, i)
            binary = binary//10
            i += 1
        return decimal

    def decimalToLetter(n):
        result = ''
        while n > 0:
            index = (n - 1) % 26
            result += chr(index + ord('A'))
            n = (n - 1) // 26
        return result[::-1]    
    
    return decimalToLetter(binaryToDecimal(binary))

def keyDecrypt(name):
    def decimalToBinary(n):
        return bin(n).replace("0b", "")

    def letterToDecimal(name):
        n = 0
        for c in name:
            n = n * 26 + 1 + ord(c) - ord('A')
        return n
    
    return decimalToBinary(int(letterToDecimal(name)))


def asciiDisplay(gameMap):
    for row in gameMap:
        for val in row:
            if val == 0.: print('⬛', end='')
            elif val == -1.: print('🛑', end='')
            elif val == -2.: print('⬜', end='')
            elif val == -3.: print('🟨', end='')
            elif val == -4.: print('🟩', end='')
            else: print(numbers[val], end='')
        print('')


def keyGeneration(difficulty):
    dummyMap = np.zeros(settings[difficulty][0])

    for i in range(settings[difficulty][1]):
        while True:
            rowIdx = randint(0, settings[difficulty][0][0]-1)
            colIdx = randint(0, settings[difficulty][0][1]-1)
            if dummyMap[rowIdx][colIdx] != 1.:
                break
        dummyMap[rowIdx][colIdx] = 1.

    key = '1'
    for row in dummyMap:
        for val in row: key += str(int(val))
    key = keyEncrypt(int(key))

    return key


def mapGeneration(difficulty, key):
    global maparr, newmaparr
    maparr = keyDecrypt(key)
    maparr = np.array(list(maparr)).astype('int')[1:].reshape(settings[difficulty][0])
    maparr[maparr == 1] = -1.

    newmaparr = np.array([-2] * (settings[difficulty][0][1]+2))
    for row in maparr:
        newmaparr = np.append(newmaparr, [-2.])
        newmaparr = np.append(newmaparr, row)
        newmaparr = np.append(newmaparr, [-2])
    newmaparr = np.append(newmaparr, [-2.] * (settings[difficulty][0][1]+2))
    maparr = newmaparr.reshape(settings[difficulty][0][0]+2, settings[difficulty][0][1]+2)

    for rowIdx, row in enumerate(maparr):
        for colIdx, val in enumerate(row):
            if val == 0.:
                minesCount = 0

                if maparr[rowIdx-1][colIdx-1] == -1.: minesCount += 1
                if maparr[rowIdx-1][colIdx] == -1.: minesCount += 1
                if maparr[rowIdx-1][colIdx+1] == -1.: minesCount += 1

                if maparr[rowIdx][colIdx-1] == -1.: minesCount += 1
                if maparr[rowIdx][colIdx+1] == -1.: minesCount += 1

                if maparr[rowIdx+1][colIdx-1] == -1.: minesCount += 1
                if maparr[rowIdx+1][colIdx] == -1.: minesCount += 1
                if maparr[rowIdx+1][colIdx+1] == -1.: minesCount += 1

                maparr[rowIdx][colIdx] = minesCount
    
    maparr = maparr[1:settings[difficulty][0][0]+1, 1:settings[difficulty][0][1]+1]


def displayMapGeneration():
    global displayMap
    displayMap = np.array([-2] * np.size(maparr)).reshape(np.shape(maparr))
    displayMap[maparr==0.] = -4.

    newDisplayMap = np.array([0.] * (np.shape(displayMap)[1] + 2))
    for row in displayMap:
        newDisplayMap = np.append(newDisplayMap, [0.])
        newDisplayMap = np.append(newDisplayMap, row)
        newDisplayMap = np.append(newDisplayMap, [0.])
    newDisplayMap = np.append(newDisplayMap, np.array([0.] * (np.shape(displayMap)[1] + 2)))

    displayMap = newDisplayMap.reshape(np.add(np.shape(displayMap), 2))

    dummyDisplayMap = np.copy(displayMap)

    for rowIdx, row in enumerate(displayMap):
        for colIdx, val in enumerate(row):
            if val == -2. and maparr[rowIdx-1][colIdx-1] != -1.:
                isInside = False

                if displayMap[rowIdx-1][colIdx-1] == -4.: isInside = True
                if displayMap[rowIdx-1][colIdx] == -4.: isInside = True
                if displayMap[rowIdx-1][colIdx+1] == -4.: isInside = True

                if displayMap[rowIdx][colIdx-1] == -4.: isInside = True
                if displayMap[rowIdx][colIdx+1] == -4.: isInside = True

                if displayMap[rowIdx+1][colIdx-1] == -4.: isInside = True
                if displayMap[rowIdx+1][colIdx] == -4.: isInside = True
                if displayMap[rowIdx+1][colIdx+1] == -4.: isInside = True

                if isInside: dummyDisplayMap[rowIdx][colIdx] = -4.

    displayMap = dummyDisplayMap[1:np.shape(dummyDisplayMap)[0]-1, 1:np.shape(dummyDisplayMap)[1]-1]


def floodFill(image, row, col, target_color, replacement_color):
    if row < 0 or row >= len(image) or col < 0 or col >= len(image[0]):
        return
    
    if image[row][col] != target_color:
        return
    
    image[row][col] = replacement_color
    
    floodFill(image, row + 1, col, target_color, replacement_color)
    floodFill(image, row - 1, col, target_color, replacement_color)
    floodFill(image, row, col + 1, target_color, replacement_color)
    floodFill(image, row, col - 1, target_color, replacement_color)

def input(colIdx, rowIdx):
    global displayMap
    if displayMap[rowIdx][colIdx] == -2.:
        displayMap[rowIdx][colIdx] = maparr[rowIdx][colIdx]
    elif displayMap[rowIdx][colIdx] == -4.:
        floodFill(displayMap, rowIdx,colIdx, -4.,-3.)
        for r, row in enumerate(displayMap):
            for c, val in enumerate(row):
                if val == -3.: displayMap[r][c] = maparr[r][c]


bgc = (150,150,150)
topBorderColor = (100,100,100)
bottomBorderColor = (200,200,200)
textColor = (80,80,80)


pygame.init()

pygame.display.set_caption('key-based minesweeper')

def menuToggle():
    global screen
    screen = pygame.display.set_mode([400, 420])
    screen.fill(bgc)

    for i in range(3):
        pygame.draw.polygon(screen, topBorderColor, [(50,30+i*130), (350,30+i*130), (340,40+i*130), (60,40+i*130), (60,120+i*130), (50,130+i*130)])
        pygame.draw.polygon(screen, bottomBorderColor, [(50,130+i*130), (350,130+i*130), (350,30+i*130), (340,40+i*130), (340,120+i*130), (60,120+i*130)])
    
    text = pygame.font.Font('freesansbold.ttf', 32).render('Generate Key', True, textColor)
    textCenter = text.get_rect()
    textCenter.center = (200, 80)
    screen.blit(text, textCenter)

    text = pygame.font.Font('freesansbold.ttf', 32).render('Paste Key', True, textColor)
    textCenter = text.get_rect()
    textCenter.center = (200, 210)
    screen.blit(text, textCenter)

    text = pygame.font.Font('freesansbold.ttf', 32).render('How to play', True, textColor)
    textCenter = text.get_rect()
    textCenter.center = (200, 340)
    screen.blit(text, textCenter)

    pygame.display.update()
menuToggle()
inMenu = True

def diffMenuToggle():
    global screen
    screen = pygame.display.set_mode([400, 420])
    screen.fill(bgc)

    for i in range(3):
        pygame.draw.polygon(screen, topBorderColor, [(50,30+i*130), (350,30+i*130), (340,40+i*130), (60,40+i*130), (60,120+i*130), (50,130+i*130)])
        pygame.draw.polygon(screen, bottomBorderColor, [(50,130+i*130), (350,130+i*130), (350,30+i*130), (340,40+i*130), (340,120+i*130), (60,120+i*130)])
    
    text = pygame.font.Font('freesansbold.ttf', 32).render('Beginner', True, (60, 118, 61))
    textCenter = text.get_rect()
    textCenter.center = (200, 80)
    screen.blit(text, textCenter)

    text = pygame.font.Font('freesansbold.ttf', 32).render('Intermediate', True, (35, 106, 151))
    textCenter = text.get_rect()
    textCenter.center = (200, 210)
    screen.blit(text, textCenter)

    text = pygame.font.Font('freesansbold.ttf', 32).render('Expert', True, (169, 68, 66))
    textCenter = text.get_rect()
    textCenter.center = (200, 340)
    screen.blit(text, textCenter)

    pygame.display.update()
inDiffMenu = False

def helpMenuToggle():
    global screen
    screen = pygame.display.set_mode([400, 250])
    screen.fill(bgc)
    
    aFont = pygame.font.Font('freesansbold.ttf', 20)
    text = aFont.render('Game map is generated by a key', True, textColor)
    textCenter = text.get_rect()
    textCenter.center = (200, 20)
    screen.blit(text, textCenter)

    text = aFont.render('Press "Generate Key" to copy a key', True, textColor)
    textCenter = text.get_rect()
    textCenter.center = (200, 45)
    screen.blit(text, textCenter)

    text = aFont.render('Extra 5 seconds when clicked on a mine', True, textColor)
    textCenter = text.get_rect()
    textCenter.center = (200, 70)
    screen.blit(text, textCenter)

    text = aFont.render('Right click to flag or unflag', True, (200, 50 ,50))
    textCenter = text.get_rect()
    textCenter.center = (200, 95)
    screen.blit(text, textCenter)

    text = aFont.render('Green squares = no mines', True, (0, 128, 0))
    textCenter = text.get_rect()
    textCenter.center = (200, 115)
    screen.blit(text, textCenter)

    pygame.draw.polygon(screen, topBorderColor, [(150, 200), (250, 200), (245, 205), (155, 205), (155, 235), (150, 240)])
    pygame.draw.polygon(screen, bottomBorderColor, [(150, 240), (250, 240), (250, 200), (245, 205), (245, 235), (155, 235)])

    text = pygame.font.Font('freesansbold.ttf', 24).render('ok', True, textColor)
    textCenter = text.get_rect()
    textCenter.center = (200, 220)
    screen.blit(text, textCenter)

    pygame.display.update()
inHelpMenu = False


font = pygame.font.Font('freesansbold.ttf', 20)
flagsLeft = 0
inGame = False
def gameMapToggle():
    global screen, flagsLeft

    rowLen = settings[difficulty][0][0]
    colLen = settings[difficulty][0][1]

    screen = pygame.display.set_mode([40 + 30*colLen, 40 + 30*rowLen + 50])
    screen.fill(bgc)


    middleX = (40 + 30*colLen) // 2
    pygame.draw.polygon(screen, topBorderColor, [(middleX-40,12), (middleX+40,12), (middleX+40-5,12+5), (middleX-40+5,12+5), (middleX-40+5,50-5), (middleX-40, 50)])
    pygame.draw.polygon(screen, bottomBorderColor, [(middleX-40,50), (middleX+40,50), (middleX+40,12), (middleX+40-5,12+5), (middleX+40-5,50-5), (middleX-40+5,50-5)])

    borderX = 40 + 30*colLen - 12
    borderY = 40 + 30*rowLen + 50 - 12
    pygame.draw.polygon(screen, topBorderColor, [(12,12+50), (borderX,12+50), (borderX-8,20+50), (20,20+50), (20,borderY-8), (12,borderY)])
    pygame.draw.polygon(screen, bottomBorderColor, [(12,borderY), (borderX,borderY), (borderX,12+50), (borderX-8,20+50), (borderX-8,borderY-8), (20,borderY-8)])

    for rowIdx, row in enumerate(displayMap):
        for colIdx, val in enumerate(row):
            if val == -2.:
                pygame.draw.polygon(screen, bottomBorderColor, [(20+colIdx*30, 72+rowIdx*30), (50+colIdx*30, 72+rowIdx*30), (47+colIdx*30, 75+rowIdx*30),
                                                                (23+colIdx*30, 75+rowIdx*30), (23+colIdx*30, 99+rowIdx*30), (20+colIdx*30, 102+rowIdx*30)])
                pygame.draw.polygon(screen, topBorderColor, [(20+colIdx*30, 102+rowIdx*30), (50+colIdx*30, 102+rowIdx*30), (50+colIdx*30, 72+rowIdx*30),
                                                             (47+colIdx*30, 75+rowIdx*30), (47+colIdx*30, 99+rowIdx*30), (23+colIdx*30, 99+rowIdx*30)])
            elif val == -4.:
                pygame.draw.polygon(screen, (111, 209, 135), [(20+colIdx*30, 72+rowIdx*30), (50+colIdx*30, 72+rowIdx*30), (47+colIdx*30, 75+rowIdx*30),
                                                                (23+colIdx*30, 75+rowIdx*30), (23+colIdx*30, 99+rowIdx*30), (20+colIdx*30, 102+rowIdx*30)])
                pygame.draw.polygon(screen, (24, 105, 30), [(20+colIdx*30, 102+rowIdx*30), (50+colIdx*30, 102+rowIdx*30), (50+colIdx*30, 72+rowIdx*30),
                                                             (47+colIdx*30, 75+rowIdx*30), (47+colIdx*30, 99+rowIdx*30), (23+colIdx*30, 99+rowIdx*30)])
                pygame.draw.polygon(screen, (68, 163, 87), [(23+colIdx*30, 75+rowIdx*30), (47+colIdx*30, 75+rowIdx*30), (47+colIdx*30, 99+rowIdx*30),
                                                             (23+colIdx*30, 99+rowIdx*30)])
                
            elif val == -1.:
                pygame.draw.polygon(screen, (0, 0, 0), [(25+colIdx*30, 77+rowIdx*30), (45+colIdx*30, 77+rowIdx*30),
                                                        (45+colIdx*30, 97+rowIdx*30), (25+colIdx*30, 97+rowIdx*30)])
            elif val == 1.:
                text = font.render(str(int(val)), True, (0, 0, 255))
                textCenter = text.get_rect()
                textCenter.center = (20+colIdx*30 + 15, 72+rowIdx*30 + 15)
                screen.blit(text, textCenter)
            elif val == 2.:
                text = font.render(str(int(val)), True, (0, 128, 0))
                textCenter = text.get_rect()
                textCenter.center = (20+colIdx*30 + 15, 72+rowIdx*30 + 15)
                screen.blit(text, textCenter)
            elif val == 3.:
                text = font.render(str(int(val)), True, (200, 50, 50))
                textCenter = text.get_rect()
                textCenter.center = (20+colIdx*30 + 15, 72+rowIdx*30 + 15)
                screen.blit(text, textCenter)
            elif val == 4.:
                text = font.render(str(int(val)), True, (0, 0, 128))
                textCenter = text.get_rect()
                textCenter.center = (20+colIdx*30 + 15, 72+rowIdx*30 + 15)
                screen.blit(text, textCenter)
            elif val == 5.:
                text = font.render(str(int(val)), True, (128, 0, 0))
                textCenter = text.get_rect()
                textCenter.center = (20+colIdx*30 + 15, 72+rowIdx*30 + 15)
                screen.blit(text, textCenter)
            elif val == 6.:
                text = font.render(str(int(val)), True, (0, 150, 160))
                textCenter = text.get_rect()
                textCenter.center = (20+colIdx*30 + 15, 72+rowIdx*30 + 15)
                screen.blit(text, textCenter)
            elif val == 7.:
                text = font.render(str(int(val)), True, (0, 0, 0))
                textCenter = text.get_rect()
                textCenter.center = (20+colIdx*30 + 15, 72+rowIdx*30 + 15)
                screen.blit(text, textCenter)
            elif val == 8.:
                text = font.render(str(int(val)), True, (135, 135, 135))
                textCenter = text.get_rect()
                textCenter.center = (20+colIdx*30 + 15, 72+rowIdx*30 + 15)
                screen.blit(text, textCenter)
            
            elif val == -5.:
                pygame.draw.polygon(screen, (235, 96, 96), [(20+colIdx*30, 72+rowIdx*30), (50+colIdx*30, 72+rowIdx*30), (47+colIdx*30, 75+rowIdx*30),
                                                                (23+colIdx*30, 75+rowIdx*30), (23+colIdx*30, 99+rowIdx*30), (20+colIdx*30, 102+rowIdx*30)])
                pygame.draw.polygon(screen, (168, 30, 30), [(20+colIdx*30, 102+rowIdx*30), (50+colIdx*30, 102+rowIdx*30), (50+colIdx*30, 72+rowIdx*30),
                                                             (47+colIdx*30, 75+rowIdx*30), (47+colIdx*30, 99+rowIdx*30), (23+colIdx*30, 99+rowIdx*30)])
                pygame.draw.polygon(screen, (212, 38, 38), [(23+colIdx*30, 75+rowIdx*30), (47+colIdx*30, 75+rowIdx*30), (47+colIdx*30, 99+rowIdx*30),
                                                             (23+colIdx*30, 99+rowIdx*30)])

    text = font.render(str(flagsLeft), True, (200, 50, 50))
    textCenter = text.get_rect()
    textCenter.center = (middleX, 32)
    screen.blit(text, textCenter)

    
    pygame.display.update()

def input(colIdx, rowIdx):
    global displayMap, minesDiscovered
    if displayMap[rowIdx][colIdx] == -2.:
        displayMap[rowIdx][colIdx] = maparr[rowIdx][colIdx]
    elif displayMap[rowIdx][colIdx] == -4.:
        floodFill(displayMap, rowIdx,colIdx, -4.,-3.)
        for r, row in enumerate(displayMap):
            for c, val in enumerate(row):
                if val == -3.: displayMap[r][c] = maparr[r][c]


endGame = False
def checkEnd():
    global minesFound
    minesFound = np.size(np.where(displayMap == -1.)[0])
    minesUnfound = np.size(np.where(np.all([displayMap==-2., maparr==-1.], axis=0))[0])
    minesFlagged = np.size(np.where(np.all([displayMap==-5., maparr==-1.], axis=0))[0])
    falseFlagged = np.size(np.where(np.all([displayMap==-5., maparr!=-1.], axis=0))[0])
    if minesUnfound == np.size(np.where(displayMap==-2.)[0])+falseFlagged: return 'end'
    if minesFound + minesFlagged + minesUnfound - falseFlagged == settings[difficulty][1] and np.size(np.where(displayMap==-2.)[0]) == 0: return 'end'
    

inEndMenu = False
def endMenuToggle():
    global screen
    screen = pygame.display.set_mode([200, 100])
    screen.fill(bgc)

    text = pygame.font.Font('freesansbold.ttf', 32).render("%.2f" % ((endTime-startTime) + minesFound*5) + 's', True, (200,50,50))
    textCenter = text.get_rect()
    textCenter.center = (100, 28)
    screen.blit(text, textCenter)

    pygame.draw.polygon(screen, topBorderColor, [(60, 50), (140, 50), (135, 55), (65, 55), (65, 85), (60, 90)])
    pygame.draw.polygon(screen, bottomBorderColor, [(60, 90), (140, 90), (140, 50), (135, 55), (135, 85), (65, 85)])

    text = pygame.font.Font('freesansbold.ttf', 24).render('ok', True, textColor)
    textCenter = text.get_rect()
    textCenter.center = (100, 70)
    screen.blit(text, textCenter)

    pygame.display.update()


running = True
while running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        
        if event.type == pygame.MOUSEBUTTONUP :
            x, y = pygame.mouse.get_pos()
            if inGame:
                for rowIdx, row in enumerate(displayMap):
                    for colIdx, val in enumerate(row):
                        if 20+colIdx*30 <= x <= 50+colIdx*30 and 72+rowIdx*30 <= y <= 102+rowIdx*30:
                            if event.button == 1 and val in [-2., -4.]:
                                input(colIdx, rowIdx)
                                gameMapToggle()
                                if checkEnd() == 'end':
                                    endTime = time()
                                    endGame = True; inGame = False; inEndMenu = True
                                    endMenuToggle()
                                    break
                            elif event.button == 3 and val == -2.:
                                displayMap[rowIdx][colIdx] = -5.
                                flagsLeft -= 1
                                gameMapToggle()
                                if checkEnd() == 'end':
                                    endTime = time()
                                    endGame = True; inGame = False; inEndMenu = True
                                    endMenuToggle()
                                    break
                            elif event.button == 3 and val == -5.:
                                displayMap[rowIdx][colIdx] = -2.
                                flagsLeft += 1
                                gameMapToggle()
                                if checkEnd() == 'end':
                                    endTime = time()
                                    endGame = True; inGame = False; inEndMenu = True
                                    endMenuToggle()
                                    break

                    if endGame: break

            elif event.button == 1:
                if inMenu:
                    if 50 <= x <= 350 and 30 <= y <= 130:
                        inMenu = False; inDiffMenu = True
                        diffMenuToggle()
                    elif 50 <= x <= 350 and 160 <= y <= 260:
                        clipboard = pyperclip.paste()
                        key = keyDecrypt(clipboard)[1:]
                        if len(key) == 81: difficulty = 0
                        elif len(key) == 16*16: difficulty = 1
                        elif len(key) == 16*30: difficulty = 2
                        else: difficulty = -1

                        if difficulty != -1:
                            flagsLeft = settings[difficulty][1]
                            inMenu = False; inDiffMenu = False; inGame = True
                            mapGeneration(difficulty, clipboard)
                            displayMapGeneration()
                            gameMapToggle()
                            startTime = time()
                    elif 50 <= x <= 350 and 290 <= y <= 390:
                        inMenu = False; inHelpMenu = True
                        helpMenuToggle()
                            
                elif inDiffMenu:
                    if 50 <= x <= 350 and 30 <= y <= 130:
                        key = keyGeneration(0)
                        pyperclip.copy(key)
                        inMenu = True; inDiffMenu = False
                        menuToggle()
                    elif 50 <= x <= 350 and 160 <= y <= 260:
                        key = keyGeneration(1)
                        pyperclip.copy(key)
                        inMenu = True; inDiffMenu = False
                        menuToggle()
                    elif 50 <= x <= 350 and 290 <= y <= 390:
                        key = keyGeneration(2)
                        pyperclip.copy(key)
                        inMenu = True; inDiffMenu = False
                        menuToggle()
                
                elif inEndMenu:
                    if 60 <= x <= 140 and 50 <= y <= 90:
                        inEndMenu = False; endGame= False
                        menuToggle(); inMenu = True
            
                elif inHelpMenu:
                    if 150 <= x <= 250 and 200 <= y <= 240:
                        inHelpMenu = False
                        menuToggle(); inMenu = True

            pygame.time.delay(100)


pygame.quit()
