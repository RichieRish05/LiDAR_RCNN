import pygame

class Piece:
    def __init__(self, color, position, grid):
        self.color = color #Color of piece
        self.position = position #Position of board in numpy array
        self.grid = grid #Grid instance from the board class
        self.num_moves = 0 #Move count for an individual piece

    def highlight_move(self):
        pass

    
    def move(self, new_position): 
        '''Allows us to move the piece by updating its position'''
        self.num_moves += 1 #counts the number of moves for each individual piece
       
        old_position = self.position
        self.position = new_position #updates the position of the piece

        self.grid[new_position] = self #moves the piece to the new position
        self.grid[old_position] = None #removes the piece from the old position


        return self.grid 

    def reset_move(self, new_position, piece_at_new_pos):
        '''Allows us to reset a move made by a piece by updating its position'''
        self.num_moves -= 1 #adjusts the number of moves for each individual piece
        
        old_position = self.position
        self.position = new_position #updates the position of the piece

        self.grid[new_position] = self #moves the piece to the new position
        self.grid[old_position] = piece_at_new_pos #adds the piece from the new position

        return self.grid

    

    def validate_move(self,x,y):
        '''Checks if a move is within the indexes of the board'''
        if 0 <= x < self.grid.shape[0]:
            if 0 <= y < self.grid.shape[1]:
                return True
        return False
    

    def is_empty(self, x, y):
        '''Checks whether a grid space is empty or not'''
        if self.validate_move(x,y) and self.grid[x,y] == None:
            return True
        return False

    def can_capture(self, x, y, color):
        '''Checks whether the selected piece can capture a piece in another grid space'''
        if self.validate_move(x,y) and self.grid[x,y] and self.grid[x,y].color != color:
            return True
        return False
    

    def is_same_color(self, x, y, color):
        '''Checks whether the selected piece has the same color as a piece in another grid space'''
        if self.validate_move(x,y) and self.grid[x,y] and self.grid[x,y].color == color:
            return True
        return False
    

    def vertical_check(self, x, y, direction):
        '''
        Checks all grid spaces in the vertical direction specified until it reaches a grid space
        with a capturable or non capturable piece or it reaches the end of the board
        '''
        vertical_moves = []
        row = x + direction 
        column = y
        pieces_in_the_way = 0 

        #Continue checking as long as the move is valid and no pieces block the path
        while self.validate_move(row, column) and pieces_in_the_way == 0:
            if self.is_empty(row,column):
                vertical_moves.append((row, column))
            
            elif self.is_same_color(row, column, self.color):
                pieces_in_the_way += 1
         
            elif self.can_capture(row, column, self.color):
                vertical_moves.append((row, column))
                pieces_in_the_way += 1
            
            #Continue checking in the direction specified
            row += direction
        
        #Returns list of possible vertical moves in specified direction
        return vertical_moves
    


    def horizontal_check(self, x, y, direction):
        '''
        Checks all grid spaces in the horizontal direction specified until it reaches a grid space
        with a capturable or non capturable piece or it reaches the end of the board
        '''
        horizontal_moves = []
        row = x 
        column = y + direction
        pieces_in_the_way = 0

        #Continue checking as long as the move is valid and no pieces block the path
        while self.validate_move(row, column) and pieces_in_the_way == 0:
            if self.is_empty(row,column):
                horizontal_moves.append((row, column))
            
            elif self.is_same_color(row, column, self.color):
                pieces_in_the_way += 1
         
            elif self.can_capture(row, column, self.color):
                horizontal_moves.append((row, column))
                pieces_in_the_way += 1
            
            #Continue checking in the direction specified
            column += direction

        #Returns list of possible horizontal moves in specified direction
        return horizontal_moves
    

    def diagonal_check(self, x, y, x_direction, y_direction):
        '''
        Checks all grid spaces in the diagonal direction specified until it reaches a grid space
        with a capturable or non capturable piece or it reaches the end of the board
        '''
        diagonal_moves = []
        row = x + x_direction
        column = y + y_direction
        pieces_in_the_way = 0

        #Continue checking as long as the move is valid and no pieces block the path
        while self.validate_move(row, column) and pieces_in_the_way == 0:
            if self.is_empty(row,column):
                diagonal_moves.append((row, column))
            
            elif self.is_same_color(row, column, self.color):
                pieces_in_the_way += 1
         
            elif self.can_capture(row, column, self.color):
                diagonal_moves.append((row, column))
                pieces_in_the_way += 1
            
            #Continue checking in the direction specified
            row += x_direction
            column += y_direction
            
        #Returns list of possible diagonal moves in specified direction
        return diagonal_moves
    

    
    def is_checking(self):
        '''
        Checks to see if the piece is checking a King
        '''
        possible_moves = self.highlight_move() #Gets a list of all possible moves

        for move in possible_moves:
            #If the move leads to a king being captured, the piece is checking a king
            if isinstance(self.grid[move[0], move[1]], King) and self.can_capture(move[0], move[1], self.color):
                return True

        return False
    
    def get_piece_list(self):
        '''
        Returns a list of all pieces that are present on the board
        '''
        piece_list = []

        for row in range(0, self.grid.shape[0]):
            for column in range(0, self.grid.shape[1]):
                if self.grid[row,column]:
                    piece_list.append(self.grid[row,column])

        return piece_list
                    


class King(Piece):
    def __init__(self, color, position, grid):
        super().__init__(color, position, grid)
        #Loads the King's sprite based on color
        if self.color == 'white':
            self.sprite = pygame.image.load('Chess_klt60.png')
            self.sprite = pygame.transform.scale(self.sprite, (100, 100))
        elif self.color == 'black':
            self.sprite = pygame.image.load('Chess_kdt60.png')
            self.sprite = pygame.transform.scale(self.sprite, (100, 100))
            
        self.piece_list = self.get_piece_list() #List of all pieces on the board
        self.has_been_checked = False #Variable to determine if King was checked
        self.just_castled = False #Variable to determine if the King's last move was a castle

    
    def highlight_move(self):
        '''Returns a list of all possible moves for a King at any position on the board'''
        possible_moves = []
        x = self.position[0]
        y = self.position[1]

        
        #Checks all squares one square away from the king
        for row in range(-1,2):
            for column in range(-1,2):
                if self.is_empty(x+row, y+column) and self.am_i_in_check:
                    possible_moves.append((x+row, y+column))
                elif self.can_capture(x+row, y+column, self.color):
                    possible_moves.append((x+row, y+column))

        #If the king can castle, appends the appropriate squares to possible_moves
        if self.can_castle('left') == True:
            possible_moves.append((self.position[0], 1))
        
        if self.can_castle('right') == True:
            possible_moves.append((self.position[0],6))
       
        return possible_moves
    

    def can_castle(self, direction):
        #Map color and direction to the correct (x, y) coordinates
        positions = {'white': {'left': (7, 0), 'right': (7, 7)},
                     'black': {'left': (0, 0), 'right': (0, 7)}}
        #Map direction to the range of squares to check
        squares_to_check = {'left': range(1, 4),
                            'right': range(5, 7)}

        #Ensure the king and rook haven't moved, and the king isn't in check
        x, y = positions[self.color][direction]

        if self.has_been_checked == True or self.num_moves > 0:
            return False
            
        #Make sure the piece at (x, y) is a rook that hasn't moved
        rook = self.grid[x, y]

        if not isinstance(rook, Rook) or rook.num_moves > 0:
            return False

        #Ensure all squares between the king and rook are empty
        squares = squares_to_check[direction] 
        for i in squares:
            if self.grid[x,i]:
                return False

        return True


    def am_i_in_check(self):
        '''Checks if King is in check'''
        self.piece_list = self.get_piece_list()

        for piece in self.piece_list:
            if piece.is_checking() and piece.color != self.color:
                return self.position



    def is_checkmate(self):
        '''Checks if King is in checkmate'''

        original_grid = self.grid #Used to reset grid back to original position
        possible_moves = []

        if self.am_i_in_check(): #Checks if king is in check
            for piece in self.piece_list: 
                if piece.color == self.color: #Checks through all pieces of same color as king
                    possible_moves = piece.highlight_move() #Gets all possible moves of a piece w/ same color as king
                    for move in possible_moves:
                        old_pos = piece.position
                        piece_at_new_pos = self.grid[move]
                        self.grid = piece.move(move) #Moves the piece to all of its possible moves
                        if not self.am_i_in_check(): #Checks if there is one possible move that results in not check
                            self.grid = original_grid #Resets grid
                            piece.reset_move(old_pos, piece_at_new_pos)
                            return False
                        piece.reset_move(old_pos, piece_at_new_pos)
                        self.grid = original_grid #Resets grid
            return True

       
        self.grid = original_grid #Resets grid
        return False


    def is_stalemate(self):
        '''Checks if King is in stalemate'''
        original_grid = self.grid #To reset grid back to original position
        possible_moves = []

        if not self.am_i_in_check(): #Checks if king is not in check
            for piece in self.piece_list: 
                if piece.color == self.color: #Checks through all pieces of same color as king
                    possible_moves = piece.highlight_move() #Gets all possible moves of a piece w/ same color as king
                    for move in possible_moves:
                        old_pos = piece.position
                        piece_at_new_pos = self.grid[move]
                        self.grid = piece.move(move) #Moves the piece to all of its possible moves
                        if not self.am_i_in_check(): #Checks if there is one possible move that results in not check
                            self.grid = original_grid #Resets grid
                            piece.reset_move(old_pos, piece_at_new_pos)
                            return False
                        piece.reset_move(old_pos, piece_at_new_pos)
                        self.grid = original_grid #Resets grid
            return True

       
        self.grid = original_grid #Resets grid
        return False
        

    def move(self, new_position): 
        '''Moves the piece to a new position'''

        self.num_moves += 1 #counts the number of moves for each individual piece
       
        old_position = self.position
        self.position = new_position #updates the position of the piece

        self.grid[new_position] = self #moves the piece to the new position
        self.grid[old_position] = None #removes the piece from the old position


        #If the king was moved to a space more than one space away from it, it just castled
        if abs(new_position[1] - old_position[1]) > 1:
            self.just_castled = True
        else:
            self.just_castled = False


        return self.grid 
      
               

class Queen(Piece):
    def __init__(self, color, position, grid):
        super().__init__(color, position, grid)
        #Loads the Queen's sprite based on color
        if self.color == 'white':
            self.sprite = pygame.image.load('Chess_qlt60.png')
            self.sprite = pygame.transform.scale(self.sprite, (100, 100))
        elif self.color == 'black':
            self.sprite = pygame.image.load('Chess_qdt60.png')
            self.sprite = pygame.transform.scale(self.sprite, (100, 100))

    
    
    def highlight_move(self):
        '''Returns a list of all possible moves for a King at any position on the board'''
        possible_moves = []
        x = self.position[0]
        y = self.position[1]

        possible_moves.extend(self.vertical_check(x,y,1))
        possible_moves.extend(self.vertical_check(x,y,-1))
        possible_moves.extend(self.horizontal_check(x,y,1))
        possible_moves.extend(self.horizontal_check(x,y,-1))
        possible_moves.extend(self.diagonal_check(x,y,1,1))
        possible_moves.extend(self.diagonal_check(x,y,1,-1))
        possible_moves.extend(self.diagonal_check(x,y,-1,-1))
        possible_moves.extend(self.diagonal_check(x,y,-1,1))
        
    
        return possible_moves

class Rook(Piece):
    def __init__(self, color, position, grid):
        super().__init__(color, position, grid)
        #Loads the Rook's sprite based on color
        if self.color == 'white':
            self.sprite = pygame.image.load('Chess_rlt60.png')
            self.sprite = pygame.transform.scale(self.sprite, (100, 100))
        elif self.color == 'black':
            self.sprite = pygame.image.load('Chess_rdt60.png')
            self.sprite = pygame.transform.scale(self.sprite, (100, 100))

    def highlight_move(self):
        '''Returns a list of all possible moves for a King at any position on the board'''
        possible_moves = []
        x = self.position[0]
        y = self.position[1]

        possible_moves.extend(self.vertical_check(x,y,1))
        possible_moves.extend(self.vertical_check(x,y,-1))
        possible_moves.extend(self.horizontal_check(x,y,1))
        possible_moves.extend(self.horizontal_check(x,y,-1))
        
    
        return possible_moves

class Bishop(Piece):
    def __init__(self, color, position, grid):
        super().__init__(color, position, grid)
        #Loads the Bishop's sprite based on color
        if self.color == 'white':
            self.sprite = pygame.image.load('Chess_blt60.png')
            self.sprite = pygame.transform.scale(self.sprite, (100, 100))
        elif self.color == 'black':
            self.sprite = pygame.image.load('Chess_bdt60.png')
            self.sprite = pygame.transform.scale(self.sprite, (100, 100))
    
    def highlight_move(self):
        '''Returns a list of all possible moves for a King at any position on the board'''
        possible_moves = []
        x = self.position[0]
        y = self.position[1]

       
        possible_moves.extend(self.diagonal_check(x,y,1,1))
        possible_moves.extend(self.diagonal_check(x,y,1,-1))
        possible_moves.extend(self.diagonal_check(x,y,-1,-1))
        possible_moves.extend(self.diagonal_check(x,y,-1,1))
        
       
        return possible_moves
    

class Knight(Piece):
    def __init__(self, color, position, grid):
        super().__init__(color, position, grid)
        #Loads the Knight's sprite based on color
        if self.color == 'white':
            self.sprite = pygame.image.load('Chess_nlt60.png')
            self.sprite = pygame.transform.scale(self.sprite, (100, 100))
        elif self.color == 'black':
            self.sprite = pygame.image.load('Chess_ndt60.png')
            self.sprite = pygame.transform.scale(self.sprite, (100, 100))
    
    def l_shape(self, x, y):
        '''Returns a list of all grid positions that form an L shaped move'''
        l_moves = []

        l_moves.append((x+2,y+1))
        l_moves.append((x+2,y-1))
        l_moves.append((x+1,y+2))
        l_moves.append((x+1,y-2))
        l_moves.append((x-1,y+2))
        l_moves.append((x-1,y-2))
        l_moves.append((x-2,y+1))
        l_moves.append((x-2,y-1))

        return l_moves

    def highlight_move(self):
        '''Returns a list of all possible moves for a King at any position on the board'''
        possible_moves = []
        x = self.position[0]
        y = self.position[1]

        l_moves = self.l_shape(x,y)
    
        for move in l_moves:
            if self.is_empty(move[0], move[1]):
                possible_moves.append(move)
            elif self.can_capture(move[0], move[1], self.color):
                possible_moves.append(move)
    
        return possible_moves

class Pawn(Piece):
    def __init__(self, color, position, grid):
        super().__init__(color, position, grid)
        if self.color == 'white':
            self.sprite = pygame.image.load('Chess_plt60.png')
            self.sprite = pygame.transform.scale(self.sprite, (100, 100))
        elif self.color == 'black':
            self.sprite = pygame.image.load('Chess_pdt60.png')
            self.sprite = pygame.transform.scale(self.sprite, (100, 100))



    def highlight_move(self):
        '''Returns a list of all possible moves for a King at any position on the board'''
        possible_moves = []
        x = self.position[0]
        y = self.position[1]

        #Assigns starting row and direction of movement based on color
        if self.color == 'black':
            direction = 1
            starting_row = 1
        if self.color == 'white':
            direction = -1
            starting_row = 6

        #Check for a two-step move from the starting row if both squares are empty
        if x == starting_row and self.is_empty(x+direction*2,y) and self.is_empty(x+direction,y):
            possible_moves.append((x+direction*2,y))
            
        #Check for a one-step move forward if the square is empty
        if self.is_empty(x+direction,y):
            possible_moves.append((x+direction,y))
        
        #Check for possible captures on the left diagonal
        if self.can_capture(x+direction, y-1, self.color):
            possible_moves.append((x+direction, y-1))
            
        #Check for possible captures on the right diagonal
        if self.can_capture(x+direction, y+1, self.color):
            possible_moves.append((x+direction, y+1))
    
    
        return possible_moves

        
