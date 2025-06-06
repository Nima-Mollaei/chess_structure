# player.py
from enum import Enum

class Player(Enum):
    WHITE = 'White'
    BLACK = 'Black'


# piece.py
from abc import ABCMeta, abstractmethod
from player import Player

class Piece(metaclass=ABCMeta):
    # ... (resto del código)


# chessboard.py
from player import Player

class ChessBoard:
    def __init__(self):
        # ... (resto del código)

    def __repr__(self):
        # ... (resto del código)

    def move_piece(self, start, stop):
        # ... (resto del código)

    def __getitem__(self, loc: str):
        # ... (resto del código)

    def __setitem__(self, loc, value):
        # ... (resto del código)


# main.py
from chessboard import ChessBoard
from player import Player

def main():
    chess_board = ChessBoard()
    chess_board.move_piece("e2", "e4")
    chess_board.move_piece("c7", "c5")
    chess_board.move_piece("g1", "f3")
    chess_board.move_piece("d7", "d5")

    print(chess_board)

if __name__ == "__main__":
    main()
