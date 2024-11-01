import numpy as np
import pieces
import pygame
import sys

class Board():

    def __init__(self, window):
        #Initializes board with an 8x8 grid filled with None, representing empty squares
        self.grid = np.full((8,8), None)

        #Variables to store references to the kings for easy access
        self.black_king = None
        self.white_king = None

        #places pieces on board
        self.place_pawns()
        self.place_value_pieces()
        self.place_kings_queens()

        #Maintains a list of all current pieces on the board
        self.piece_list = []

        #stores the reference to the game window in order to render the board
        self.window = window 

        # Keeps track of squares currently highlighted, for visual feedback in the UI
        self.highlighted_squares = []

        #Variables to handle piece selection, movement, and resetting a piece's position
        self.selected_piece = None
        self.old_pos = None
        self.piece_in_motion = None

        #Variables to control turn logic
        self.white_moves = 0
        self.black_moves = 0
        self.white_turn = True 
        self.black_turn = False 

        #Variables to handle pawn promotion logic
        self.promotion_window = None
        self.promoted_pawn = None

        #Renders the board and updates the game display
        self.render()
        

    def get_piece_list(self):
        '''Returns a list of all pieces on the board'''

        #Initialize an empty list to store the pieces
        piece_list = []
        #iterates over each row on the board
        for row in self.grid:
            #iterates over each column on the board
            for element in row:
                if element:
                    piece_list.append(element)
        #returns list of all pieces found
        return piece_list
    
    def place_pawns(self):
        '''places pawns on board'''
        for x in range(0,8):
            self.grid[1,x]=pieces.Pawn('black', (1,x), self.grid)
            self.grid[6,x]=pieces.Pawn('white', (6,x), self.grid)


    def place_value_pieces(self):
        '''places rooks, knights, and bishops on the board'''

        #list of value pieces
        value_pieces = [pieces.Rook, pieces.Knight, pieces.Bishop]

        #iterates over the index and piece class in the value_pieces list
        for x, piece in enumerate(value_pieces):
            #Place pieces for both colors ('white' and 'black') on their respective starting rows
            for color, row in [('white', 7), ('black', 0)]:
                self.grid[row,x]=piece(color, (row,x), self.grid)
                self.grid[row,7-x]=piece(color, (row,7-x), self.grid)
        
    
    def place_kings_queens(self):
         '''places queens and kings on the board'''   
        
         #initializes self.black_king and self.white_king for easy reference 
         self.black_king = pieces.King('black', (0, 4), self.grid)
         self.white_king = pieces.King('white', (7, 4), self.grid)

        #Places queens and kings on their respective square on the board
         self.grid[0,3] = pieces.Queen('black', (0, 3), self.grid)
         self.grid[7,3] = pieces.Queen('white', (7, 3), self.grid)
         self.grid[0,4] = self.black_king
         self.grid[7,4] = self.white_king
         


    def convert_coords_graphics(self, array_position): 
        '''
        convert's a piece's index in the numpy array to a form where it can 
        be graphically represented at the proper place on the board
        '''
        x = array_position[1]*100
        y = array_position[0]*100

        return (x,y)


    def convert_coords_matrix(self, array_position):
        '''
        convert's an index on the graphic board to a form where it can 
        be represented at the proper place in a numpy array   
        '''
        x = array_position[1]//100
        y = array_position[0]//100

        return (x,y)
    

    def is_game_over(self):
        '''
        Determines whether or not the game is over depending on if 
        there is a checkmate/stalemate. 
        '''
        if (self.black_king.is_checkmate() or self.white_king.is_checkmate()
            or self.black_king.is_stalemate() or self.white_king.is_stalemate()):
            return True
        return False
        

    def render(self):
        '''
        Runs the main game loop until a checkmate or stalemate occurs.
        Manages events such as mouse clicks, updates and renders the chessboard,
        displays chess pieces, and handles pawn promotion when needed.
        '''

        #Sets the display caption
        pygame.display.set_caption('CHESS')

        #RGB color values for drawing the board
        brown = (139, 69, 19)
        light_brown = (222, 184, 135)  
        cyan = (0, 255, 255)

        #Initializes game_over with False at the beginning of the game
        game_over = False
        
        #Main game loop that continues until the user exits the game
        while True:
            
            #Checks if the game is over
            game_over = self.is_game_over()
               
            #Handles all events in the Pygame event queue
            for event in pygame.event.get():
                if event.type == pygame.QUIT: 
                    pygame.quit()  
                    sys.exit() 
                #Calls mouse_click method when a mouse button is pressed unless stalemate/checkmate
                if not game_over and event.type == pygame.MOUSEBUTTONDOWN:
                    self.mouse_click(event)
            
            #Draws checkerboard pattern of chess board
            for x in range(0,8):
                for y in range(0,8,2):
                    if x%2==0:
                        pygame.draw.rect(self.window, brown, (x*100, y*100, 100, 100))
                        pygame.draw.rect(self.window, light_brown, (x*100, (y+1)*100, 100, 100))
                    else:
                        pygame.draw.rect(self.window, light_brown, (x*100, y*100, 100, 100))
                        pygame.draw.rect(self.window, brown, (x*100, (y+1)*100, 100, 100))
            
            #Updates the piece list with pieces that are currently on the board
            self.piece_list = self.get_piece_list()

            for piece in self.piece_list:
                piece.grid = self.grid #Updates each piece object's reference to the board


            for piece in self.piece_list:
                self.window.blit(piece.sprite, self.convert_coords_graphics(piece.position)) 
                #Highlights a king if it is in check
                self.in_check(piece) 

            #Iterates through all the highlighted squares in the highligted_squares list
            for square in self.highlighted_squares:
                #Converts the numpy coordinates to graphical coordinates
                coords = self.convert_coords_graphics(square) 
                #Creates a border around highlighted squares
                pygame.draw.rect(self.window, cyan, (coords[0], coords[1], 100, 100), width = 10) 


            #if a pawn is promoted, promotion_window will be initialized and rendered
            if self.promotion_window:
                self.window.blit(self.promotion_window, (200,400))  #Renders the promotion board
                pygame.display.flip() #Updates board
                #Allows user select a piece for pawn promotion
                self.choose_promotion() 

            pygame.display.flip() #Updates board

    
    def in_check(self, piece):
        '''
        If the piece is a king and it is in check, it is highlighted
        with a red border
        '''
        red = (100, 0, 0) #RGB value for the color red

        if isinstance(piece, pieces.King):
            #If the king is in check, highlights it with a red border
            if piece.am_i_in_check():
                #Convert the king's board coordinates to graphical coordinates
                pos = self.convert_coords_graphics(piece.am_i_in_check())
                #Update the king's status for castling purposes
                piece.has_been_checked = True 
                pygame.draw.rect(self.window, red, (pos[0], pos[1], 100, 100), width = 10)


    def update_turn(self):
        '''
        Updates self.white_turn and self.black_turn based on the move count of each side
        '''

        #If move counts are equal, it is White's turn
        if self.white_moves == self.black_moves:
            self.white_turn = True
            self.black_turn = False
        #If move counts are unequal, it is Black's turn
        else:
            self.black_turn = True
            self.white_turn = False


    def update_selected_piece(self, mouse_position): 
        '''
        Updates self.selected piece based on the mouse position
        '''    

        #Check if there is a piece at the mouse position and if it is White's turn
        if self.grid[mouse_position] and self.white_turn and self.grid[mouse_position].color == 'white':
            #Select the piece, update its old position, and set it as the piece in motion
            self.selected_piece = self.grid[mouse_position]
            self.old_pos = self.selected_piece.position 
            self.piece_in_motion = self.selected_piece
        #Check if there is a piece at the mouse position and if it is Black's turn
        elif self.grid[mouse_position] and self.black_turn and self.grid[mouse_position].color == 'black':
            #Select the piece, update its old position, and set it as the piece in motion
            self.selected_piece = self.grid[mouse_position]
            self.old_pos = self.selected_piece.position
            self.piece_in_motion = self.selected_piece
        else:
            #If no valid piece is selected, reset the selected piece
            self.selected_piece = None
        
        
    def count_moves(self, piece, addend):
        '''Counts the moves of both white and black sides'''
        if piece.color == 'white':
            self.white_moves += addend
        if piece.color == 'black':
            self.black_moves += addend


    def reset_highlighted_squares(self):
        '''Resets the list of highlighted squares'''
        self.highlighted_squares = []


    def castling_mechanics(self):
        '''
        Moves the rook if the King just castled
        '''

        #Checks if the piece in motion is a King piece
        if isinstance(self.piece_in_motion, pieces.King):
            if self.piece_in_motion.just_castled:
                #Checks if King castled to the left side of the board
                if self.piece_in_motion.position[1] == 1:
                    x = self.piece_in_motion.position[0] #Row of King
                    y = 2 #Column rook needs to move to
                    y_rook = 0 #Column of the left rook
                    self.grid[x,y_rook].move((x,y)) 
                #Checks if King castled to the right side of the board
                elif self.piece_in_motion.position[1] == 6:
                    x = self.piece_in_motion.position[0] #Row of King
                    y = 5 #Column rook needs to move to
                    y_rook = 7 #Column of the right rook
                    self.grid[x,y_rook].move((x,y)) #
            

    #registers a mouse click and gets the position of the mouse at the time of the click
    def mouse_click(self, event): 
        '''
        Handles all the move logic, including highlighting possible moves, pawn promotions, 
        resetting a move if it is invalid, and castling.
        '''

        #Converts the mouse position at time of click to correspond to an index in self.grid
        mouse_position =  self.convert_coords_matrix(event.pos)


        #Updates self.selected_piece based on mouse position
        self.update_selected_piece(mouse_position)

        #If a piece has been selected and it is clicked, the piece's possible moves are highlighted
        if self.selected_piece and mouse_position == self.selected_piece.position:
            self.highlighted_squares = self.selected_piece.highlight_move() 
        else:
            #Checks if the user clicked a highlighted square
            for square in self.highlighted_squares:
                if mouse_position == square:
                   
                    piece_at_new_pos = self.grid[square] #the element of the grid at the position clicked
                    self.grid = self.piece_in_motion.move(square)
                    self.count_moves(self.piece_in_motion, 1) 
                    self.update_turn() 

                    #Checks if King is in check and the if the side whose king is in check is moving
                    for piece in self.piece_list:
                        if isinstance(piece, pieces.King):
                            if piece.am_i_in_check() and self.piece_in_motion.color == piece.color: 
                                self.grid = self.piece_in_motion.reset_move(self.old_pos, piece_at_new_pos) #resets move
                                self.count_moves(self.piece_in_motion, -1) 
                                self.update_turn() 
                    
                    #If the move is a castle, this handles castling mechanics
                    self.castling_mechanics()

                    #If the move is a pawn promotion, this handles pawn promotion mechanics
                    self.pawn_promotion()


            self.reset_highlighted_squares() #removes highlighted squares for the next turn


    def pawn_promotion(self):
        '''
        Creates a pygame surface with sprites of the pieces that a pawn can be promoted to. 
        '''
        
        #assigns the last rank for the piece based on color
        last_rank = {'white': 0, 'black': 7}
        #assigns the sprites for the piece based on color
        promotions = {'black': ['Chess_bdt60.png', 'Chess_ndt60.png', 'Chess_rdt60.png', 'Chess_qdt60.png'],
                      'white': ['Chess_blt60.png', 'Chess_nlt60.png', 'Chess_rlt60.png', 'Chess_qlt60.png']}

        color = self.piece_in_motion.color

        #check if the piece in motion is a Pawn and has reached the last rank
        if isinstance(self.piece_in_motion, pieces.Pawn):
            rank = self.piece_in_motion.position[0]
            if rank == last_rank[color]:
                #creates the surface displaying the sprites
                self.promotion_window = pygame.Surface((400, 100))
                self.promotion_window.fill((255, 215, 0))
                for x in range(0,4):
                    sprite = pygame.image.load(promotions[color][x])
                    sprite = pygame.transform.scale(sprite, (100, 100))
                    self.promotion_window.blit(sprite, (x*100, 0))
                #sets the promoted pawn to be the current piece in motion
                self.promoted_pawn = self.piece_in_motion
                
    
    def choose_promotion(self):
        '''
        Allows the player to choose a piece for pawn promotion by clicking on a displayed option
        '''
        
        color = self.promoted_pawn.color
        pawn_pos = self.promoted_pawn.position

        #Map screen positions to potential promotion pieces
        promotions = {(4,2): pieces.Bishop(color, pawn_pos, self.grid),
                      (4,3): pieces.Knight(color, pawn_pos, self.grid),
                      (4,4): pieces.Rook(color, pawn_pos, self.grid),
                      (4,5): pieces.Queen(color, pawn_pos, self.grid)}

        #Wait for a valid click in the promotion area
        event = self.wait_for_click()
        mouse_position =  self.convert_coords_matrix(event.pos)
        while mouse_position not in promotions:
            event = self.wait_for_click()
            mouse_position =  self.convert_coords_matrix(event.pos)


        #Promotes the pawn to the piece the user clicked on
        for pos in promotions.keys():
            if mouse_position == pos:
                self.grid[pawn_pos] = promotions[pos]

        #Resets the promotion window
        self.promotion_window = None

            
    def wait_for_click(self):
         '''
         Waits for the user to click the screen
         '''

         while True:
        #Checks all events in the event queue
            for event in pygame.event.get():
            #If a mouse button is clicked, the loop is broken
                if event.type == pygame.MOUSEBUTTONDOWN:
                    return event





    
               
                
                        




        

                    
            

    

                   
            
        







