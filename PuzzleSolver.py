from PIL import Image
import cv2
import numpy

from Vertex import *

MAX_SQUARE_COLUMN = 3
MAX_SQUARE_ROW = 3
MAX_SQUARES = (MAX_SQUARE_COLUMN + 1) * (MAX_SQUARE_ROW + 1)

class PuzzleSolver:
    def __init__(self):
        self.allBreaks = []

        self.templateStart = cv2.imread("templates/templateStart.png", cv2.IMREAD_GRAYSCALE)
        self.templateEnd = cv2.imread("templates/templateEnd.png", cv2.IMREAD_GRAYSCALE)
        self.templateStar = cv2.imread("templates/templateStar.png", cv2.IMREAD_GRAYSCALE)
        self.templateTetris = cv2.imread("templates/templateTetris.png", cv2.IMREAD_GRAYSCALE)

    ############################################################################################

    def findTemplateInImage(self, image, template):
        result = cv2.matchTemplate(image, template, cv2.TM_SQDIFF)
        result = cv2.normalize(result, None, 0, 1, cv2.NORM_MINMAX)
        loc = numpy.where(result < 0.01)
        for pt in zip(*loc[::-1]):
            xyResults = ( int(pt[0]), int(pt[1]) )
            #print("found template at ", xyResults)
            break
                
        return xyResults

    ############################################################################################

    def findMultipleTemplatesInImage(self, image, template):
        xyResults = []
        result = cv2.matchTemplate(image, template, cv2.TM_SQDIFF)
        result = cv2.normalize(result, None, 0, 1, cv2.NORM_MINMAX)
        loc = numpy.where(result < 0.1)
        for pt in zip(*loc[::-1]):
            xyResults.append( (int(pt[0]) + 8, int(pt[1]) + 8) )
            #print("found template at ", xyResults)
                
        return xyResults

    ############################################################################################

    def getPixelData(self, image, x, y):
        return image[y, x]

    ############################################################################################

    def doesPixelDataMatch(self, image, x, y, expectedColor, blackAndWhite):
        pixel = image[y, x]
        if (blackAndWhite == True):
            return (pixel == expectedColor)
        else:
            for i in range(0, len(expectedColor)):
                if (abs(int(expectedColor[i]) - int(pixel[i])) > 5):
                    return False
            return True

############################################################################################

    def convertXYToSquare(self, xy, startLoc, X_GRID_SPACING, Y_GRID_SPACING):
        BOTTOM_OF_ROW = startLoc[1] - 3 * Y_GRID_SPACING
        RIGHT_OF_COLUMN = startLoc[0] + X_GRID_SPACING
        for y in range(0, 4):
            if (xy[1] < BOTTOM_OF_ROW):
                for x in range(0, 4):
                    if (xy[0] < RIGHT_OF_COLUMN):
                        return (y * 4 + x)
                    else:
                        RIGHT_OF_COLUMN = RIGHT_OF_COLUMN + X_GRID_SPACING
            else:
                BOTTOM_OF_ROW = BOTTOM_OF_ROW + Y_GRID_SPACING

############################################################################################

    def findAttachedTetrisSquares(self, imgColorCropped, singleTetrisSquareLoc, squareNumber, startLoc, X_GRID_SPACING, Y_GRID_SPACING):
        ROW = int(squareNumber / 4)
        COLUMN = squareNumber % 4
        TOP_OF_SQUARE_Y = startLoc[1] - Y_GRID_SPACING * (4 - ROW)
        BOTTOM_OF_SQUARE_Y = TOP_OF_SQUARE_Y + Y_GRID_SPACING
        LEFT_OF_SQUARE_X = startLoc[0] + X_GRID_SPACING * COLUMN
        RIGHT_OF_SQUARE_X = LEFT_OF_SQUARE_X + X_GRID_SPACING
        COLOR_NEEDED = self.getPixelData(imgColorCropped, singleTetrisSquareLoc[0], singleTetrisSquareLoc[1])
        PIXELS_BETWEEN_SQUARES = 17

        # get the left side of where to start looking
        xToSearch = singleTetrisSquareLoc[0]
        while (xToSearch > LEFT_OF_SQUARE_X):
            xToSearch = xToSearch - PIXELS_BETWEEN_SQUARES
        xToSearch = xToSearch + PIXELS_BETWEEN_SQUARES
        X_TO_SEARCH_START = xToSearch

        # get the upper side of where to start looking
        yToSearch = singleTetrisSquareLoc[1]
        while (yToSearch > TOP_OF_SQUARE_Y):
            yToSearch = yToSearch - PIXELS_BETWEEN_SQUARES
        yToSearch = yToSearch + PIXELS_BETWEEN_SQUARES

        # get all the squares that match the color
        allTetrisSquareLocs = []
        while (yToSearch < BOTTOM_OF_SQUARE_Y):
            xToSearch = X_TO_SEARCH_START
            while (xToSearch < RIGHT_OF_SQUARE_X):
                match = self.doesPixelDataMatch(imgColorCropped, xToSearch, yToSearch, COLOR_NEEDED, False)
                if (match == True):
                    allTetrisSquareLocs.append( (xToSearch, yToSearch) )
                xToSearch += PIXELS_BETWEEN_SQUARES
            yToSearch += PIXELS_BETWEEN_SQUARES
        
        return allTetrisSquareLocs

    ############################################################################################

    def convertTetrisXYToSquares(self, tetrisSquaresLocs):
        tetrisSquares = []

        smallestX = 9000
        smallestY = 9000

        for loc in tetrisSquaresLocs:
            if loc[0] < smallestX:
                smallestX = loc[0]
            if loc[1] < smallestY:
                smallestY = loc[1]

        PIXELS_BETWEEN_SQUARES = 17

        for loc in tetrisSquaresLocs:
            x = (loc[0] - smallestX) / PIXELS_BETWEEN_SQUARES
            y = (loc[1] - smallestY) / PIXELS_BETWEEN_SQUARES
            tetrisSquares.append( int(y) * 4 + int(x) )
        
        return tetrisSquares

    ############################################################################################

    def squaresInSameEnclosure(self, squareA, squareB, enclosureVertices):
        squareAColumn = squareA % (MAX_SQUARE_COLUMN + 1)
        squareARow = int( squareA / (MAX_SQUARE_COLUMN + 1) )
        squareBColumn = squareB % (MAX_SQUARE_COLUMN + 1)
        squareBRow = int( squareB / (MAX_SQUARE_COLUMN + 1) ) 
        
        # find the two vertices in common
        if (squareARow == squareBRow):
            # they are in the same row, use the one on the right
            vertex1 = squareARow * (MAX_VERTEX_COLUMN + 1) + max(squareAColumn, squareBColumn)
            vertex2 = vertex1 + (MAX_VERTEX_COLUMN + 1)
        else:
            # they are in the same column, use the one below
            vertex1 = (MAX_VERTEX_COLUMN + 1) * max(squareARow, squareBRow) + squareAColumn
            vertex2 = vertex1 + 1
            

        # check if the two vertices are directly connected, if yes then return False
        for i in range(0, len(enclosureVertices)):
            if (enclosureVertices[i].vertexNumber == vertex1):
                if (enclosureVertices[i-1].vertexNumber == vertex2) or (enclosureVertices[i+1].vertexNumber == vertex2):
                    return False

        return True

        
    def analyzeNeighborSquares(self, currentSquare, enclosureVertices):
        currentColumn = currentSquare % (MAX_SQUARE_COLUMN + 1)
        currentRow = int( currentSquare / (MAX_SQUARE_COLUMN + 1) )
        newSquares = []
        
        # check left side
        if (currentColumn > 0):
            newSquare = currentSquare - 1
            if (self.squaresInSameEnclosure(currentSquare, newSquare, enclosureVertices) == True):
                newSquares.append(newSquare)
                
        # check below
        if (currentRow < MAX_SQUARE_ROW):
            newSquare = currentSquare + (MAX_SQUARE_COLUMN + 1)
            if (self.squaresInSameEnclosure(currentSquare, newSquare, enclosureVertices) == True):
                newSquares.append(newSquare)
                
        # check right side
        if (currentColumn < MAX_SQUARE_COLUMN):
            newSquare = currentSquare + 1
            if (self.squaresInSameEnclosure(currentSquare, newSquare, enclosureVertices) == True):
                newSquares.append(newSquare)

        # check above
        if (currentRow > 0):
            newSquare = currentSquare - (MAX_SQUARE_COLUMN + 1)
            if (self.squaresInSameEnclosure(currentSquare, newSquare, enclosureVertices) == True):
                newSquares.append(newSquare)
                
        return newSquares


    def convertEnclosuresToSquares(self, allEnclosureVertices):
        allSquares = list(range(0,MAX_SQUARES))
        allEnclosureSquares = []
        
        # for each enclosure, remove the squares from the list of allSquares
        for enclosureVertices in allEnclosureVertices:
            currentEnclosureSquares = []

            # initialize with one square we absolutely know is in the enclosure
            if (enclosureVertices[0].row == 0) and (enclosureVertices[-1] == 0): # starting and ending on the top edge
                if (enclosureVertices[0].vertexNumber == 3):
                    currentEnclosureSquares.append(2)
                else:
                    currentEnclosureSquares.append(1)
            elif (enclosureVertices[0].row == MAX_SQUARE_ROW) and (enclosureVertices[-1] == MAX_SQUARE_ROW): # starting and stopping on the bottom edge
                if (enclosureVertices[0].vertexNumber ==  23):
                    currentEnclosureSquares.append(14)
                else:
                    currentEnclosureSquares.append(13)
            elif (enclosureVertices[0].column == 0) and (enclosureVertices[-1].column == 0): # starting and stopping on the left edge
                if (enclosureVertices[0].vertexNumber == 5):
                    currentEnclosureSquares.append(4)
                else:
                    currentEnclosureSquares.append(8)
            elif (enclosureVertices[0].column == MAX_SQUARE_COLUMN) and (enclosureVertices[-1].column == MAX_SQUARE_COLUMN): # start/stop on right edge
                if (enclosureVertices[0].vertexNumber == 9):
                    currentEnclosureSquares.append(7)
                else:
                    currentEnclosureSquares.append(11)
            elif (enclosureVertices[0].column == MAX_VERTEX_COLUMN): # the enclosure starts on the right edge
                if (enclosureVertices[-1].row == MAX_VERTEX_ROW):
                    currentEnclosureSquares.append(15)
                else:
                    currentEnclosureSquares.append(3)
            elif (enclosureVertices[0].row == MAX_VERTEX_ROW): # the enclosure starts on the bottom edge
                currentEnclosureSquares.append(3)
            elif (enclosureVertices[0].row == 0): # the enclosure starts on the top edge
                if (enclosureVertices[-1].column == 0):
                    currentEnclosureSquares.append(0)
                else:
                    currentEnclosureSquares.append(3)
            elif (enclosureVertices[0].column == 0): # the enclosure starts on the left edge
                currentEnclosureSquares.append(0)


            index = 0
            while (index < len(currentEnclosureSquares)):
                newSquares = self.analyzeNeighborSquares(currentEnclosureSquares[index], enclosureVertices)
                for square in newSquares:
                    if (square not in currentEnclosureSquares):
                        currentEnclosureSquares.append(square)
                #print(currentEnclosureSquares)
                index += 1

            trimmedEnclosureSquares = []
            for square in currentEnclosureSquares:
                if (square in allSquares):
                    allSquares.remove(square)
                    trimmedEnclosureSquares.append(square)
            allEnclosureSquares.append(trimmedEnclosureSquares)

        allEnclosureSquares.append(allSquares)
        return allEnclosureSquares

    def normalizeSquares(self, squares):
        smallestColumn = MAX_SQUARE_COLUMN
        smallestRow = MAX_SQUARE_ROW

        for square in squares:
            column = square % (MAX_SQUARE_COLUMN + 1)
            smallestColumn = min(column, smallestColumn)
            row = int(square / ((MAX_SQUARE_COLUMN + 1)))
            smallestRow = min(row, smallestRow)

        for i in range(0, len(squares)):
            squares[i] = (squares[i] - smallestRow * (MAX_SQUARE_COLUMN + 1)) - smallestColumn

        squares.sort()
        return squares

    def getPossibleLocations(self, tetrisShape):
        # the input has already been normalized
        largestColumn = 0
        largestRow = 0

        for square in tetrisShape:
            column = square % (MAX_SQUARE_COLUMN + 1)
            largestColumn = max(column, largestColumn)
            row = int(square / ((MAX_SQUARE_COLUMN + 1)))
            largestRow = max(row, largestRow)

        possibleLocations = []
        for columnShift in range(0, MAX_SQUARE_COLUMN + 1 - largestColumn):
            for rowShift in range(0, MAX_SQUARE_ROW + 1 - largestRow):
                possibleLocation = tetrisShape.copy()
                for i in range(0, len(possibleLocation)):
                    possibleLocation[i] += (columnShift + rowShift * (MAX_SQUARE_COLUMN + 1))
                possibleLocations.append(possibleLocation)
        
        return possibleLocations

    def combineAndNormalizeSquares(self, firstSquares, secondSquares):
        expectedLength = len(firstSquares) + len(secondSquares)

        # add the two lists, convert it to a set which will remove duplicates, then convert back to a list
        comboShape = list(set(firstSquares + secondSquares))
        if (len(comboShape) != expectedLength):
            return [] # there must have been overlap in the two shapes, so return empty list

        comboShape = self.normalizeSquares(comboShape)
        return comboShape

    def isCorrectSolution(self, vertices, firstStarSquare, secondStarSquare, firstTetrisSquare, secondTetrisSquare, firstTetrisShape, secondTetrisShape):
        # find the vertices for all of the enclosures
        allEnclosureVertices = []
        currentEnclosureVertices = []
        awayFromEdge = False
        for vertx in vertices:
            if (awayFromEdge == True):
                if (vertx.column == 0) or (vertx.column == MAX_VERTEX_COLUMN) or (vertx.row == 0) or (vertx.row == MAX_VERTEX_ROW):
                    currentEnclosureVertices.append(vertx)
                    allEnclosureVertices.append(currentEnclosureVertices)
                    currentEnclosureVertices = []
                    awayFromEdge = False
                else:
                    currentEnclosureVertices.append(vertx)
            else:
                if (vertx.column == 0) or (vertx.column == MAX_VERTEX_COLUMN) or (vertx.row == 0) or (vertx.row == MAX_VERTEX_ROW):
                    currentEnclosureVertices.clear()
                    currentEnclosureVertices.append(vertx)
                else:
                    awayFromEdge = True
                    currentEnclosureVertices.append(vertx)


        # debug only, print the enclosures
    ##    print("Enclosure vertices:")
    ##    for enclosureVertices in allEnclosureVertices:
    ##        result = ""
    ##        for vertx in enclosureVertices:
    ##            result += str(vertx) + " "
    ##        print(result)
        
        # convert enclosure vertices to square numbers
        allEnclosureSquares = self.convertEnclosuresToSquares(allEnclosureVertices)
        #print(allEnclosureSquares)

        # if one enclosure contains a star, verify the other star is there too, else return False
        for enclosureSquares in allEnclosureSquares:
            if (firstStarSquare in enclosureSquares):
                if (secondStarSquare not in enclosureSquares):
                    return False

        # if enclosure contains 1 or 2 tetris shapes, verify the size of the enclosure matches the size of the tetris shape(s), else return False
        for enclosureSquares in allEnclosureSquares:
            if (firstTetrisSquare in enclosureSquares) and (secondTetrisSquare in enclosureSquares):
                expectedSize = len(firstTetrisShape) + len(secondTetrisShape)
                if (expectedSize != len(enclosureSquares)):
                    return False

                # combine and check shapes
                firstTetrisLocations = self.getPossibleLocations(firstTetrisShape)
                secondTetrisLocations = self.getPossibleLocations(secondTetrisShape)
                enclosureShape = self.normalizeSquares(enclosureSquares.copy())
                for firstSquares in firstTetrisLocations:
                    for secondSquares in secondTetrisLocations:
                        comboShape = self.combineAndNormalizeSquares(firstSquares, secondSquares)
                        if (comboShape == enclosureShape):
                            return True

                # we couldn't find the comboShape in the enclosure
                return False
                
            elif (firstTetrisSquare in enclosureSquares):
                if (len(firstTetrisShape) != len(enclosureSquares)):
                    return False
                enclosureShape = self.normalizeSquares(enclosureSquares.copy())
                if (firstTetrisShape != enclosureShape):
                    return False
                
            elif (secondTetrisSquare in enclosureSquares):
                if (len(secondTetrisShape) != len(enclosureSquares)):
                    return False
                enclosureShape = self.normalizeSquares(enclosureSquares.copy())
                if (secondTetrisShape != enclosureShape):
                    return False

        # if we made it this far, no problems occurred
        return True

    ############################################################################################

    def drawCorrectSolution(self, imgColorCropped, vertices, startLoc, X_GRID_SPACING, Y_GRID_SPACING):
        if (len(vertices) > 0):
            currentVertex = vertices.pop()
            currentLoc = startLoc

            while (len(vertices) > 0):
                nextVertex = vertices.pop()
                vertexDifference = nextVertex.vertexNumber - currentVertex.vertexNumber
                if (vertexDifference == 1):
                    nextLoc = (currentLoc[0] + X_GRID_SPACING, currentLoc[1])
                elif (vertexDifference == -5):
                    nextLoc = (currentLoc[0], currentLoc[1] - Y_GRID_SPACING)
                elif (vertexDifference == -1):
                    nextLoc = (currentLoc[0] - X_GRID_SPACING, currentLoc[1])
                elif (vertexDifference == 5):
                    nextLoc = (currentLoc[0], currentLoc[1] + Y_GRID_SPACING)

                cv2.line(imgColorCropped, currentLoc, nextLoc, (123, 255, 123), 2)

                currentVertex = nextVertex
                currentLoc = nextLoc
            return True
        else:
            return False
            #cv2.putText(imgColorCropped, "No solution found", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    ############################################################################################
    ############################################################################################
    ############################################################################################

    def run(self, img, debug):
        # resize the image to 1920 x 1080 if not already
        # TODO: have not tested this, the image might become too blurry so I may have to sharpen the image
        if (img.width != 1920) or (img.height != 1080):
            print("Resizing to 1920 x 1080")
            img = img.resize((1920, 1080))

        imgColor = cv2.cvtColor(numpy.array(img), cv2.COLOR_RGB2BGR)
        imgGray = cv2.cvtColor(numpy.array(img), cv2.COLOR_RGB2GRAY)
        thr, imgBW = cv2.threshold(imgGray, 50, 255, cv2.THRESH_BINARY) # do binarization, was 50
        templateStartLoc = self.findTemplateInImage(imgBW, self.templateStart)
        templateEndLoc = self.findTemplateInImage(imgBW, self.templateEnd)
        if (templateStartLoc[0] > templateEndLoc[0]): # we may have grabbed the start of the other puzzle due to the flashing cursor
            templateStartLoc = self.findTemplateInImage(imgBW[:,0:templateEndLoc[0]], self.templateStart) # try again by ignoring the other puzzle
    ##    print(templateStartLoc, templateEndLoc)
    ##    finish = False
    ##    while not finish:
    ##        cv2.imshow("Result", imgGray)
    ##        key = cv2.waitKey(1000)
    ##        if (key >= 0):
    ##            finish = True

        #############################################################


        # crop the image so that we work with a smaller amount of data when template matching, when cropping the image it uses [y,x]
        imgBWCropped = imgBW[templateEndLoc[1]:templateStartLoc[1]+76, templateStartLoc[0]:templateEndLoc[0]+68]
        imgColorCropped = imgColor[templateEndLoc[1]:templateStartLoc[1]+76, templateStartLoc[0]:templateEndLoc[0]+68]
        CROPPED_TO_ORIGINAL_OFFSET_X = templateStartLoc[0]
        CROPPED_TO_ORIGINAL_OFFSET_Y = templateEndLoc[1]

        # calculate the center of the start circle and the center of the end
        startLoc = (38, templateStartLoc[1] + 38 - CROPPED_TO_ORIGINAL_OFFSET_Y)
        endLoc = (templateEndLoc[0] + 30 - CROPPED_TO_ORIGINAL_OFFSET_X, 40)
        #cv2.line(imgColorCropped, startLoc, endLoc, (0, 0, 255))
        X_GRID_SPACING = int((endLoc[0] - startLoc[0]) / 4 + 0.5) # the 0.5 is for rounding
        Y_GRID_SPACING = int((startLoc[1] - endLoc[1]) / 4 + 0.5)

        #############################################################


        # find the horz breaks in the puzzle path
        self.allBreaks = []
        xToTest = startLoc[0] + int(X_GRID_SPACING / 2)
        for x in range(0, 4):
            yToTest = endLoc[1]
            for y in range(0, 5):
                broken = self.doesPixelDataMatch(imgBWCropped, xToTest, yToTest, 0, True)
                if (broken == True):
                    self.allBreaks.append( (y*5 + x,y*5 + x + 1) )    # (y*9 + x)
                    if (debug):
                        cv2.circle(imgColorCropped, (xToTest, yToTest), 5, (0, 0, 255))
                yToTest = yToTest + Y_GRID_SPACING
            xToTest = xToTest + X_GRID_SPACING


        #############################################################


        # find the vert breaks in the puzzle path
        xToTest = startLoc[0]
        for x in range(0, 5):
            yToTest = endLoc[1] + int(Y_GRID_SPACING / 2)
            for y in range(0, 4):
                broken = self.doesPixelDataMatch(imgBWCropped, xToTest, yToTest, 0, True)
                if (broken == True):
                    self.allBreaks.append( (y*5 + x,y*5 + x + 5) )           # (4 + y*9 + x)
                    if (debug):
                        cv2.circle(imgColorCropped, (xToTest, yToTest), 5, (0, 0, 255))
                yToTest = yToTest + Y_GRID_SPACING
            xToTest = xToTest + X_GRID_SPACING


        #############################################################


        # find one of the stars
        starLoc = self.findTemplateInImage(imgBWCropped, self.templateStar)
        if (debug):
            cv2.circle(imgColorCropped, starLoc, 5, (255, 0, 0))
        
        x = starLoc[0]
        y = starLoc[1]
        pts = numpy.full((1,4,2), 0)
        pts[0,0] = (x,y)
        pts[0,1] = (x+40,y)
        pts[0,2] = (x+40,y+40)
        pts[0,3] = (x,y+40)
        
        # look for the other star
        cv2.fillPoly(imgBWCropped, pts, 0)
        starLoc2 = self.findTemplateInImage(imgBWCropped, self.templateStar)
        if (debug):
            cv2.circle(imgColorCropped, starLoc2, 5, (255, 0, 0))

        # find which numbered squares have the stars, 0 - 15
        squaresWithStars = []
        firstStarSquare = self.convertXYToSquare(starLoc, startLoc, X_GRID_SPACING, Y_GRID_SPACING)
        squaresWithStars.append(firstStarSquare)
        secondStarSquare = self.convertXYToSquare(starLoc2, startLoc, X_GRID_SPACING, Y_GRID_SPACING)
        squaresWithStars.append(secondStarSquare)


        #############################################################

        
        # find the tetris blocks
        tetrisLocs = self.findMultipleTemplatesInImage(imgBWCropped, self.templateTetris)
        
        firstTetrisSquareLoc = tetrisLocs.pop(0)
        firstTetrisSquare = self.convertXYToSquare(firstTetrisSquareLoc, startLoc, X_GRID_SPACING, Y_GRID_SPACING)

        squaresWithTetrisBlocks = []
        squaresWithTetrisBlocks.append(firstTetrisSquare)

        while (len(tetrisLocs) > 0):
            secondTetrisSquareLoc = tetrisLocs.pop()
            secondTetrisSquare = self.convertXYToSquare(secondTetrisSquareLoc, startLoc, X_GRID_SPACING, Y_GRID_SPACING)
            if (secondTetrisSquare in squaresWithTetrisBlocks):
                continue
            else:
                squaresWithTetrisBlocks.append(secondTetrisSquare)
                break

        # find all the locs of the tetris squares
        firstTetrisSquaresLocs = self.findAttachedTetrisSquares(imgColorCropped, firstTetrisSquareLoc, firstTetrisSquare, startLoc, X_GRID_SPACING, Y_GRID_SPACING)
        secondTetrisSquaresLocs = self.findAttachedTetrisSquares(imgColorCropped, secondTetrisSquareLoc, secondTetrisSquare, startLoc, X_GRID_SPACING, Y_GRID_SPACING)

        if (debug):
            for loc in firstTetrisSquaresLocs:
                cv2.circle(imgColorCropped, loc, 9, (255, 0, 255))
            for loc in secondTetrisSquaresLocs:
                cv2.circle(imgColorCropped, loc, 9, (255, 0, 255))

        # turn tetris xy coords into square numbers 0 - 15
        firstTetrisShape = self.convertTetrisXYToSquares(firstTetrisSquaresLocs)
        secondTetrisShape = self.convertTetrisXYToSquares(secondTetrisSquaresLocs)


        #############################################################


        # find the correct solution
        vertexPool = []
        vertices = []
        for i in range(0, MAX_VERTICES):
            vertexPool.append( Vertex() )

        newVertex = vertexPool.pop()
        newVertex.setData(MAX_VERTEX_COLUMN, 0, MAX_VERTEX_COLUMN, False, False, True, True, self.allBreaks)
        vertices.append(newVertex)

        currentColumn = MAX_VERTEX_COLUMN
        currentRow = 0
        newVertexNumber = -1

        running = True
        while (running == True):
            if (newVertexNumber == CORRECT_END_VERTEX):

                # check if correct solution
                if (self.isCorrectSolution(vertices, firstStarSquare, secondStarSquare, firstTetrisSquare, secondTetrisSquare, firstTetrisShape, secondTetrisShape) == True):
                    running = False
                    break
            
                # remove end vertex, send it back to the pool
                vertexPool.append(vertices.pop())
                currentColumn = vertices[-1].column
                currentRow = vertices[-1].row
                newVertexNumber = -1
            else:
                backingUp = True
                while (backingUp == True):
                    newColumn, newRow, newVertexNumber = vertices[-1].calcNextMove(vertices)
                    if (currentColumn == newColumn) and (currentRow == newRow):
                        # can't move, so back up
                        vertexPool.append(vertices.pop())
                        if (len(vertices) > 0):
                            currentColumn = vertices[-1].column
                            currentRow = vertices[-1].row
                        else:
                            running = False # no more complete lines are possible
                            break
                    else:
                        # we did move
                        currentColumn = newColumn
                        currentRow = newRow
                        backingUp = False

                        # add vertex
                        newVertex = vertexPool.pop()
                        newVertex.setData(currentColumn, currentRow, newVertexNumber, False, False, False, False, self.allBreaks)
                        vertices.append(newVertex)


        #############################################################
        
        
        # draw the correct solution
        success = self.drawCorrectSolution(imgColorCropped, vertices, startLoc, X_GRID_SPACING, Y_GRID_SPACING)

        # return the image
        if (success):
            return Image.fromarray(cv2.cvtColor(imgColorCropped, cv2.COLOR_BGR2RGB))
        else:
            return None


###################################################################################################


if __name__ == "__main__":
    img = Image.open("sample_screenshots/1.png")
    slv = PuzzleSolver()
    result = slv.run(img, True)
    result.show()
