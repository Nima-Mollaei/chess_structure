import tkinter as tk
from tkinter import messagebox, simpledialog

TILE_SIZE = 64
ROWS, COLS = 8, 8
WHITE, BLACK = 'white', 'black'

PIECES = {
    'K': '♔', 'Q': '♕', 'R': '♖', 'B': '♗', 'N': '♘', 'P': '♙',
    'k': '♚', 'q': '♛', 'r': '♜', 'b': '♝', 'n': '♞', 'p': '♟'
}

class Piece:
    def __init__(self, name, color):
        self.name = name
        self.color = color
        self.has_moved = False

    def __str__(self):
        return PIECES[self.name.upper() if self.color == WHITE else self.name.lower()]

    def get_moves(self, board, x, y, en_passant_target=None, check_check=True):
        moves = []

        def inside_board(nx, ny):
            return 0 <= nx < 8 and 0 <= ny < 8

        if self.name == 'P':
            dir = -1 if self.color == WHITE else 1
            start_row = 6 if self.color == WHITE else 1
            # Forward moves
            if inside_board(x, y+dir) and board[y+dir][x] is None:
                moves.append((x, y+dir))
                if y == start_row and board[y+2*dir][x] is None:
                    moves.append((x, y+2*dir))
            # Captures
            for dx in [-1, 1]:
                nx, ny = x + dx, y + dir
                if inside_board(nx, ny):
                    target = board[ny][nx]
                    if target and target.color != self.color:
                        moves.append((nx, ny))
                    elif en_passant_target == (nx, ny):
                        moves.append((nx, ny))

        elif self.name == 'R':
            directions = [(0,1),(1,0),(0,-1),(-1,0)]
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                while inside_board(nx, ny):
                    target = board[ny][nx]
                    if target is None:
                        moves.append((nx, ny))
                    elif target.color != self.color:
                        moves.append((nx, ny))
                        break
                    else:
                        break
                    nx += dx
                    ny += dy

        elif self.name == 'B':
            directions = [(1,1),(1,-1),(-1,1),(-1,-1)]
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                while inside_board(nx, ny):
                    target = board[ny][nx]
                    if target is None:
                        moves.append((nx, ny))
                    elif target.color != self.color:
                        moves.append((nx, ny))
                        break
                    else:
                        break
                    nx += dx
                    ny += dy

        elif self.name == 'Q':
            directions = [(0,1),(1,0),(0,-1),(-1,0),(1,1),(1,-1),(-1,1),(-1,-1)]
            for dx, dy in directions:
                nx, ny = x + dx, y + dy
                while inside_board(nx, ny):
                    target = board[ny][nx]
                    if target is None:
                        moves.append((nx, ny))
                    elif target.color != self.color:
                        moves.append((nx, ny))
                        break
                    else:
                        break
                    nx += dx
                    ny += dy

        elif self.name == 'N':
            jumps = [(2,1),(1,2),(-1,2),(-2,1),(-2,-1),(-1,-2),(1,-2),(2,-1)]
            for dx, dy in jumps:
                nx, ny = x+dx, y+dy
                if inside_board(nx, ny):
                    target = board[ny][nx]
                    if target is None or target.color != self.color:
                        moves.append((nx, ny))

        elif self.name == 'K':
            king_moves = [(x+dx, y+dy) for dx in [-1,0,1] for dy in [-1,0,1] if dx != 0 or dy != 0]
            for nx, ny in king_moves:
                if inside_board(nx, ny):
                    target = board[ny][nx]
                    if target is None or target.color != self.color:
                        moves.append((nx, ny))

            # Castling
            if not self.has_moved:
                row = y
                # Kingside castling
                if self.can_castle(board, x, y, kingside=True):
                    moves.append((x+2, y))
                # Queenside castling
                if self.can_castle(board, x, y, kingside=False):
                    moves.append((x-2, y))

        # If check_check=True, filter out moves that leave king in check
        if check_check:
            valid_moves = []
            for move in moves:
                if not self.move_puts_king_in_check(board, (x, y), move, en_passant_target):
                    valid_moves.append(move)
            return valid_moves

        return moves

    def can_castle(self, board, x, y, kingside):
        # Check if squares between king and rook are empty and not attacked
        rook_x = 7 if kingside else 0
        direction = 1 if kingside else -1
        rook = board[y][rook_x]

        if rook is None or rook.name != 'R' or rook.color != self.color or rook.has_moved:
            return False

        # Squares between king and rook must be empty
        range_start = x + direction
        range_end = rook_x
        step = direction
        for nx in range(range_start, range_end, step):
            if board[y][nx] is not None:
                return False

        # King may not be in check, nor pass through or end on attacked squares
        # We'll check squares: current, one step, two steps in direction
        squares_to_check = [x, x + direction, x + 2*direction]
        game_dummy = ChessGame.dummy_board(board)
        for sq_x in squares_to_check:
            if self.square_attacked(game_dummy, sq_x, y, self.color):
                return False

        return True

    def move_puts_king_in_check(self, board, src, dst, en_passant_target):
        # Simulate move and check if own king is in check
        x1, y1 = src
        x2, y2 = dst
        piece = board[y1][x1]
        target = board[y2][x2]
        board_copy = [row[:] for row in board]
        # Deep copy pieces (to avoid reference issues)
        board_copy = []
        for row in board:
            board_copy.append([p if p is None else Piece(p.name, p.color) for p in row])

        # Apply move on copy
        board_copy[y2][x2] = board_copy[y1][x1]
        board_copy[y1][x1] = None

        # Remove captured pawn for en passant
        if piece.name == 'P' and dst == en_passant_target:
            capture_row = y1
            board_copy[capture_row][x2] = None

        return self.square_attacked(board_copy, *self.find_king(board_copy, piece.color), piece.color)

    @staticmethod
    def square_attacked(board, x, y, color):
        # Check if square (x,y) is attacked by opponent of color
        for j in range(8):
            for i in range(8):
                p = board[j][i]
                if p is not None and p.color != color:
                    moves = p.get_moves(board, i, j, check_check=False)
                    if (x, y) in moves:
                        return True
        return False

    @staticmethod
    def find_king(board, color):
        for y in range(8):
            for x in range(8):
                p = board[y][x]
                if p and p.name == 'K' and p.color == color:
                    return (x, y)
        return (-1, -1)

class ChessGame:
    def __init__(self, root):
        self.root = root
        self.canvas = tk.Canvas(root, width=COLS*TILE_SIZE+200, height=ROWS*TILE_SIZE+40)
        self.canvas.pack()
        self.canvas.bind("<Button-1>", self.on_click)

        self.status_var = tk.StringVar()
        self.status_label = tk.Label(root, textvariable=self.status_var, font=('Arial', 14))
        self.status_label.pack()

        self.selected = None
        self.highlighted = []
        self.turn = WHITE
        self.history = []
        self.captured = []
        self.board = [[None]*8 for _ in range(8)]
        self.en_passant_target = None
        self.in_check_flag = False
        self.game_over = False

        self.setup_board()
        self.draw()

        btn_frame = tk.Frame(root)
        btn_frame.pack()
        tk.Button(btn_frame, text="Undo", command=self.undo).pack(side='left')
        tk.Button(btn_frame, text="Reset", command=self.reset).pack(side='left')

    def setup_board(self):
        placement = ['R','N','B','Q','K','B','N','R']
        for i in range(8):
            self.board[1][i] = Piece('P', BLACK)
            self.board[6][i] = Piece('P', WHITE)
            self.board[0][i] = Piece(placement[i], BLACK)
            self.board[7][i] = Piece(placement[i], WHITE)

    def draw(self):
        self.canvas.delete("all")
        for y in range(8):
            for x in range(8):
                fill = '#EEE' if (x+y)%2 == 0 else '#666'

                # Highlight selected and possible moves
                if self.selected == (x, y):
                    fill = '#8f8'
                elif (x, y) in self.highlighted:
                    fill = '#8cf'

                piece = self.board[y][x]
                # Highlight king in check
                if piece and piece.name == 'K' and self.is_in_check(piece.color):
                    fill = '#f88'

                self.canvas.create_rectangle(x*TILE_SIZE, y*TILE_SIZE,
                                             (x+1)*TILE_SIZE, (y+1)*TILE_SIZE,
                                             fill=fill)
                if piece:
                    self.canvas.create_text((x+0.5)*TILE_SIZE, (y+0.5)*TILE_SIZE,
                                            text=str(piece), font=("Arial", 32))

        # Captured pieces display
        self.canvas.create_text(8*TILE_SIZE+10, 20, text="Captured:", anchor='nw')
        white_caps = ''.join(str(p) for p in self.captured if p.color == BLACK)
        black_caps = ''.join(str(p) for p in self.captured if p.color == WHITE)
        self.canvas.create_text(8*TILE_SIZE+10, 50, text=f"White: {white_caps}", anchor='nw')
        self.canvas.create_text(8*TILE_SIZE+10, 80, text=f"Black: {black_caps}", anchor='nw')

        # Status message
        turn_text = "White" if self.turn == WHITE else "Black"
        if self.game_over:
            self.status_var.set(f"Game Over! {turn_text} lost.")
        else:
            check_text = " (Check!)" if self.is_in_check(self.turn) else ""
            self.status_var.set(f"Turn: {turn_text}{check_text}")

    def on_click(self, event):
        if self.game_over:
            return
        if event.x >= 8*TILE_SIZE or event.y >= 8*TILE_SIZE:
            return
        x, y = event.x // TILE_SIZE, event.y // TILE_SIZE
        piece = self.board[y][x]

        # If selected and clicked on valid move
        if self.selected and (x, y) in self.highlighted:
            self.move_piece(self.selected, (x, y))
            self.selected = None
            self.highlighted = []
            self.draw()
            self.check_game_end()
            return

        # Select piece if belongs to current player
        if piece and piece.color == self.turn:
            self.selected = (x, y)
            self.highlighted = piece.get_moves(self.board, x, y, self.en_passant_target)
        else:
            self.selected = None
            self.highlighted = []

        self.draw()

    def move_piece(self, src, dst):
        x1, y1 = src
        x2, y2 = dst
        piece = self.board[y1][x1]
        target = self.board[y2][x2]
        captured = None
        special = None  # for special moves: castling, en passant, promotion

        # Save state for undo
        state = {
            'board': [[p if p is None else Piece(p.name, p.color) for p in row] for row in self.board],
            'turn': self.turn,
            'en_passant_target': self.en_passant_target,
            'captured': self.captured[:],
        }

        # Handle castling
        if piece.name == 'K' and abs(x2 - x1) == 2:
            special = 'castling'
            if x2 > x1:
                # kingside
                rook_src = (7, y1)
                rook_dst = (x2 -1, y1)
            else:
                # queenside
                rook_src = (0, y1)
                rook_dst = (x2 +1, y1)
            rook = self.board[rook_src[1]][rook_src[0]]
            self.board[rook_dst[1]][rook_dst[0]] = rook
            self.board[rook_src[1]][rook_src[0]] = None
            rook.has_moved = True

        # Handle en passant capture
        if piece.name == 'P' and dst == self.en_passant_target:
            special = 'en_passant'
            capture_row = y1
            captured = self.board[capture_row][x2]
            self.board[capture_row][x2] = None

        # Normal capture
        if target and target.color != piece.color:
            captured = target

        # Move piece
        self.board[y2][x2] = piece
        self.board[y1][x1] = None

        # Promotion
        if piece.name == 'P' and (y2 == 0 or y2 == 7):
            special = 'promotion'
            promoted_piece = self.ask_promotion(piece.color)
            self.board[y2][x2] = Piece(promoted_piece, piece.color)

        # Update flags
        piece.has_moved = True

        # Update en passant target
        if piece.name == 'P' and abs(y2 - y1) == 2:
            self.en_passant_target = (x1, (y1 + y2)//2)
        else:
            self.en_passant_target = None

        # Save move history for undo
        self.history.append({
            'state': state,
            'move': (src, dst),
            'special': special,
            'captured': captured,
        })

        if captured:
            self.captured.append(captured)

        # Change turn
        self.turn = BLACK if self.turn == WHITE else WHITE

    def ask_promotion(self, color):
        choices = {'Q': 'Queen', 'R': 'Rook', 'B': 'Bishop', 'N': 'Knight'}
        while True:
            choice = simpledialog.askstring("Promotion", "Promote to (Q, R, B, N):").upper()
            if choice in choices:
                return choice

    def undo(self):
        if not self.history:
            return
        last = self.history.pop()
        # Restore board
        self.board = [[p if p is None else Piece(p.name, p.color) for p in row] for row in last['state']['board']]
        self.turn = last['state']['turn']
        self.en_passant_target = last['state']['en_passant_target']
        self.captured = last['state']['captured'][:]
        self.selected = None
        self.highlighted = []
        self.game_over = False
        self.draw()

    def is_in_check(self, color):
        king_pos = Piece.find_king(self.board, color)
        if king_pos == (-1, -1):
            return False
        return Piece.square_attacked(self.board, *king_pos, color)

    def check_game_end(self):
        if self.is_in_check(self.turn):
            # Check if no legal moves => checkmate
            if not self.has_legal_moves(self.turn):
                self.game_over = True
                loser = "White" if self.turn == WHITE else "Black"
                messagebox.showinfo("Checkmate", f"Checkmate! {loser} loses.")
                return
        else:
            # Check stalemate
            if not self.has_legal_moves(self.turn):
                self.game_over = True
                messagebox.showinfo("Stalemate", "Stalemate! Draw.")
                return
        self.draw()

    def has_legal_moves(self, color):
        for y in range(8):
            for x in range(8):
                p = self.board[y][x]
                if p and p.color == color:
                    moves = p.get_moves(self.board, x, y, self.en_passant_target)
                    if moves:
                        return True
        return False

    def reset(self):
        self.board = [[None]*8 for _ in range(8)]
        self.captured = []
        self.history = []
        self.selected = None
        self.highlighted = []
        self.turn = WHITE
        self.en_passant_target = None
        self.game_over = False
        self.setup_board()
        self.draw()

    @staticmethod
    def dummy_board(board):
        # For checking attacked squares in castling: shallow copy pieces without has_moved etc
        dummy = []
        for row in board:
            dummy.append([p if p is None else Piece(p.name, p.color) for p in row])
        return dummy

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Chess")
    game = ChessGame(root)
    root.mainloop()
