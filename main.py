import board
import pygame


class Chess():

    def __init__(self):
        pygame.init()
        self.width, self.height = 800, 800
        self.window = pygame.display.set_mode((self.width, self.height))
        self.board_instance = board.Board(self.window)
            
Chess()



