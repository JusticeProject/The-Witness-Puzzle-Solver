MAX_VERTEX_COLUMN = 4
MAX_VERTEX_ROW = 4
MAX_VERTICES = (MAX_VERTEX_COLUMN + 1) * (MAX_VERTEX_ROW + 1)
CORRECT_START_VERTEX = MAX_VERTEX_COLUMN
CORRECT_END_VERTEX = (MAX_VERTEX_COLUMN + 1) * MAX_VERTEX_ROW

############################################################################################

class Vertex:
    def __init__(self):
        self.vertexNumber = 0
        self.column = 0
        self.row = 0
        self.leftDone = False
        self.downDone = False
        self.rightDone = False
        self.upDone = False
        self.nextVertex = 0
        self.allBreaks = []
        
    #####################################
        
    def __str__(self):
        return str(self.vertexNumber)
        
    #####################################
    
    def setData(self, column, row, number, left, down, right, up, allBreaks):
        self.vertexNumber = number
        self.column = column
        self.row = row
        self.leftDone = left
        self.downDone = down
        self.rightDone = right
        self.upDone = up
        self.allBreaks = allBreaks
    
    #####################################
    
    def isVertexAvailable(self, newColumn, newRow, vertices):
        newVertexNumber = newRow * (MAX_VERTEX_COLUMN + 1) + newColumn
        for vert in vertices:
            if (newVertexNumber == vert.vertexNumber):
                return False

        # check for breaks in the path
        vertexPair = ( min(self.vertexNumber, newVertexNumber), max(self.vertexNumber, newVertexNumber) )
        if (vertexPair in self.allBreaks):
            return False
        
        self.nextVertex = newVertexNumber
        return True
    
    #####################################
    
    def calcNextMove(self, vertices):
        if (self.leftDone == False) and (self.column > 0) and (self.isVertexAvailable(self.column - 1, self.row, vertices) == True):
            self.leftDone = True
            #print("making left move from ", currentX, currentY)
            newColumn = self.column - 1
            return newColumn, self.row, self.nextVertex
        else:
            self.leftDone = True
            
        if (self.downDone == False) and (self.row < MAX_VERTEX_ROW) and (self.isVertexAvailable(self.column, self.row + 1, vertices) == True):
            self.downDone = True
            #print("making down move from ", currentX, currentY)
            newRow = self.row + 1
            return self.column, newRow, self.nextVertex
        else:
            self.downDone = True

        # if we're on the bottom, we can't go right
        if (self.rightDone == False) and (self.column < MAX_VERTEX_COLUMN) and (self.row < MAX_VERTEX_ROW) and (self.isVertexAvailable(self.column + 1, self.row, vertices) == True):
            self.rightDone = True
            #print("making right move from ", currentX, currentY)
            newColumn = self.column + 1
            return newColumn, self.row, self.nextVertex
        else:
            self.rightDone = True

        # if we're on the right side, we can't go up
        # if we're on the left side, we can't go up
        if (self.upDone == False) and (self.row > 0) and (self.column > 0) and (self.column < MAX_VERTEX_COLUMN) and (self.isVertexAvailable(self.column, self.row - 1, vertices) == True):
            self.upDone = True
            #print("making up move from ", currentX, currentY)
            newRow = self.row - 1
            return self.column, newRow, self.nextVertex
        else:
            self.upDone = True
            
        return self.column, self.row, self.nextVertex
