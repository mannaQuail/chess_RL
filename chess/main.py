import copy
from pieces import Pawn, Rook, Knight, Bishop, Queen, King

class ChessBoard:
    def __init__(self):
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.setup_board()
        self.en_passant_target = None  # Track the target square for en passant

    def setup_board(self):
        # Set up pawns
        for i in range(8):
            self.board[1][i] = Pawn('black')
            self.board[6][i] = Pawn('white')

        # Set up rooks
        self.board[0][0] = Rook('black')
        self.board[0][7] = Rook('black')
        self.board[7][0] = Rook('white')
        self.board[7][7] = Rook('white')

        # Set up knights
        self.board[0][1] = Knight('black')
        self.board[0][6] = Knight('black')
        self.board[7][1] = Knight('white')
        self.board[7][6] = Knight('white')

        # Set up bishops
        self.board[0][2] = Bishop('black')
        self.board[0][5] = Bishop('black')
        self.board[7][2] = Bishop('white')
        self.board[7][5] = Bishop('white')

        # Set up queens
        self.board[0][3] = Queen('black')
        self.board[7][3] = Queen('white')

        # Set up kings
        self.board[0][4] = King('black')
        self.board[7][4] = King('white')

    # def move_piece(self, turn, start_pos, end_pos, new_piece_id=None, judge=False):
    #     piece = self.board[start_pos[0]][start_pos[1]]
    #     tmp_board = copy.deepcopy(self.board)
    #     tmp_en_passant_target = self.en_passant_target  # Save the current en passant target

    #     if piece is None:
    #         return False

    #     if isinstance(piece, King) and self.is_castling_move(start_pos, end_pos):
    #         return self.castle(start_pos, end_pos, judge)

    #     if isinstance(piece, Pawn) and self.is_en_passant_move(start_pos, end_pos):
    #         captured_pos = (start_pos[0], end_pos[1])

    #         # Move pawn
    #         self.board[end_pos[0]][end_pos[1]] = piece
    #         self.board[start_pos[0]][start_pos[1]] = None

    #         # Remove captured pawn
    #         self.board[captured_pos[0]][captured_pos[1]] = None

    #     elif piece and piece.is_valid_move(start_pos, end_pos, self.board):
    #         if self.board[end_pos[0]][end_pos[1]] is not None:
    #             if self.board[end_pos[0]][end_pos[1]].color == turn:
    #                 return False

    #         self.board[end_pos[0]][end_pos[1]] = piece
    #         self.board[start_pos[0]][start_pos[1]] = None

    #         if new_piece_id is not None:
    #             if not self.promote_pawn(end_pos, new_piece_id):
    #                 self.board = tmp_board  # Revert the move
    #                 self.en_passant_target = tmp_en_passant_target  # Revert the en passant target
    #                 return False

    #         if self.is_in_check(turn):
    #             self.board = tmp_board  # Revert the move
    #             self.en_passant_target = tmp_en_passant_target  # Revert the en passant target
    #             return False

    #         if judge:
    #             self.board = tmp_board  # Revert the move for judge mode
    #             self.en_passant_target = tmp_en_passant_target  # Revert the en passant target
    #             return True

    #         if isinstance(piece, (King, Rook)):
    #             piece.has_moved = True  # Mark the piece as having moved

    #         return True

    #     return False

    def move_piece(self, turn, start_pos, end_pos, new_piece_id=None, judge=False):
        piece = self.board[start_pos[0]][start_pos[1]]

        if piece is None:
            return False

        if piece.color != turn:
            return False

        tmp_board = copy.deepcopy(self.board)
        tmp_en_passant_target = self.en_passant_target

        # -------------------------
        # Castling
        # -------------------------
        if isinstance(piece, King) and self.is_castling_move(
            start_pos, end_pos
        ):
            return self.castle(start_pos, end_pos, judge)

        # -------------------------
        # En passant
        # -------------------------
        elif isinstance(piece, Pawn) and self.is_en_passant_move(
            start_pos, end_pos
        ):
            captured_pos = (start_pos[0], end_pos[1])

            self.board[end_pos[0]][end_pos[1]] = piece
            self.board[start_pos[0]][start_pos[1]] = None

            self.board[captured_pos[0]][captured_pos[1]] = None

        # -------------------------
        # Normal move
        # -------------------------
        elif piece.is_valid_move(
            start_pos, end_pos, self.board
        ):

            target = self.board[end_pos[0]][end_pos[1]]

            if target is not None and target.color == turn:
                return False

            self.board[end_pos[0]][end_pos[1]] = piece
            self.board[start_pos[0]][start_pos[1]] = None

            if new_piece_id is not None:
                if not self.promote_pawn(end_pos, new_piece_id):
                    self.board = tmp_board
                    self.en_passant_target = tmp_en_passant_target
                    return False

        else:
            return False

        # -------------------------
        # Check validation
        # -------------------------
        if self.is_in_check(turn):
            self.board = tmp_board
            self.en_passant_target = tmp_en_passant_target
            return False

        # -------------------------
        # Update en passant target
        # -------------------------
        self.en_passant_target = None

        if isinstance(piece, Pawn):
            if abs(start_pos[0] - end_pos[0]) == 2:
                middle_row = (start_pos[0] + end_pos[0]) // 2
                self.en_passant_target = (
                    middle_row,
                    start_pos[1]
                )

        # -------------------------
        # Judge mode
        # -------------------------
        if judge:
            self.board = tmp_board
            self.en_passant_target = tmp_en_passant_target
            return True

        # -------------------------
        # Mark moved
        # -------------------------
        if isinstance(piece, (King, Rook)):
            piece.has_moved = True

        return True

    def castle(self, start_pos, end_pos, judge=False):
        row = start_pos[0]

        # King-side
        if end_pos[1] > start_pos[1]:
            rook_start = (row, 7)
            rook_end = (row, 5)

        # Queen-side
        else:
            rook_start = (row, 0)
            rook_end = (row, 3)

        king = self.board[start_pos[0]][start_pos[1]]
        rook = self.board[rook_start[0]][rook_start[1]]

        tmp_board = copy.deepcopy(self.board)
        tmp_en_passant_target = self.en_passant_target  # Save the current en passant target

        # King 이동
        self.board[end_pos[0]][end_pos[1]] = king
        self.board[start_pos[0]][start_pos[1]] = None

        # Rook 이동
        self.board[rook_end[0]][rook_end[1]] = rook
        self.board[rook_start[0]][rook_start[1]] = None

        king.has_moved = True
        rook.has_moved = True

        self.en_passant_target = None

        if self.is_in_check(king.color):
            self.board = tmp_board
            self.en_passant_target = tmp_en_passant_target
            return False

        if judge:
            self.board = tmp_board
            self.en_passant_target = tmp_en_passant_target

        return True

    def is_castling_move(self, start_pos, end_pos):
        piece = self.board[start_pos[0]][start_pos[1]]

        if not isinstance(piece, King) or piece.has_moved:
            return False

        # King must move two squares horizontally
        if start_pos[0] != end_pos[0] or abs(start_pos[1] - end_pos[1]) != 2:
            return False

        # Find rook
        rook_col = 0 if end_pos[1] < start_pos[1] else 7
        rook = self.board[start_pos[0]][rook_col]

        if not isinstance(rook, Rook):
            return False

        if rook.color != piece.color or rook.has_moved:
            return False

        # Squares between King and Rook must be empty
        col_start, col_end = sorted([start_pos[1], rook_col])

        for col in range(col_start + 1, col_end):
            if self.board[start_pos[0]][col] is not None:
                return False

        # King cannot castle while in check
        if self.is_in_check(piece.color):
            return False

        # King cannot pass through or land on an attacked square
        opponent = 'black' if piece.color == 'white' else 'white'

        step = 1 if end_pos[1] > start_pos[1] else -1

        for col in range(
            start_pos[1],
            end_pos[1] + step,
            step
        ):
            if self.is_square_attacked(
                (start_pos[0], col),
                opponent
            ):
                return False

        return True

    def is_en_passant_move(self, start_pos, end_pos):
        piece = self.board[start_pos[0]][start_pos[1]]

        if not isinstance(piece, Pawn):
            return False

        # 현재 앙파상 가능한 칸인지
        if self.en_passant_target != end_pos:
            return False

        # Pawn은 대각선 한 칸 이동
        if abs(end_pos[1] - start_pos[1]) != 1:
            return False

        direction = -1 if piece.color == 'white' else 1

        if end_pos[0] - start_pos[0] != direction:
            return False

        # 잡히는 Pawn의 위치
        captured_pos = (start_pos[0], end_pos[1])
        captured_piece = self.board[captured_pos[0]][captured_pos[1]]

        if not isinstance(captured_piece, Pawn):
            return False

        if captured_piece.color == piece.color:
            return False

        return True

    def is_in_check(self, color):
        # Find the king's position
        king_pos = None
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if isinstance(piece, King) and piece.color == color:
                    king_pos = (row, col)
                    break
            if king_pos:
                break

        if not king_pos:
            return False  # King not found, should not happen in a valid game

        # Check if any opposing piece can move to the king's position
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.color != color:
                    if piece.is_valid_move((row, col), king_pos, self.board):
                        return True

        return False

    def is_square_attacked(self, pos, attacking_color):
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]

                if piece is None:
                    continue

                if piece.color != attacking_color:
                    continue

                if isinstance(piece, Pawn):
                    direction = -1 if attacking_color == 'white' else 1

                    if (
                        row + direction == pos[0]
                        and abs(col - pos[1]) == 1
                    ):
                        return True

                else:
                    if piece.is_valid_move((row, col), pos, self.board):
                        return True

        return False
    
    def promote_pawn(self, pos, new_piece_id):
        piece = self.board[pos[0]][pos[1]]
        if isinstance(piece, Pawn):
            if (piece.color == 'white' and pos[0] == 0) or (piece.color == 'black' and pos[0] == 7):
                if new_piece_id == 0:
                    self.board[pos[0]][pos[1]] = Queen(piece.color)
                elif new_piece_id == 1:
                    self.board[pos[0]][pos[1]] = Rook(piece.color)
                elif new_piece_id == 2:
                    self.board[pos[0]][pos[1]] = Bishop(piece.color)
                elif new_piece_id == 3:
                    self.board[pos[0]][pos[1]] = Knight(piece.color)
                else:
                    raise ValueError("Invalid piece ID for promotion.")
                return True
            
        print("Promotion failed: Not a pawn or not in the correct row.")
        return False

    def is_checkmate(self, color):
        if not self.is_in_check(color):
            return False

        # Check if any move can get the king out of check
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.color == color:
                    for r in range(8):
                        for c in range(8):
                            if (row, col) != (r, c):
                                if self.move_piece(color, (row, col), (r, c), judge=True):
                                    return False  # Found a valid move to escape check

        return True  # No valid moves found, it's checkmate

    def is_stalemate(self, color):
        if self.is_in_check(color):
            return False

        # Check if any move can be made
        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]
                if piece and piece.color == color:
                    for r in range(8):
                        for c in range(8):
                            if (row, col) != (r, c):
                                if self.move_piece(color, (row, col), (r, c), judge=True):
                                    return False  # Found a valid move

        return True  # No valid moves found, it's stalemate

    
    def view_board(self):
        for i, row in enumerate(self.board):
            print(8 - i, end=' ')
            print(' '.join([piece.symbol if piece else '.' for piece in row]))
        print('  a b c d e f g h')

def main():
    chess_board = ChessBoard()
    chess_board.view_board()
    turn = 'white'
    while True:
        input_move = input("Enter your move (e.g., 'e2 e4'): ")
        if '=' in input_move:
            move_part, promotion_part = input_move.split('=')
            start, end = move_part.split()
            new_piece_id = int(promotion_part)
        else:
            start, end = input_move.split()
            new_piece_id = None

        if start[0] not in 'abcdefgh' or end[0] not in 'abcdefgh' or start[1] not in '12345678' or end[1] not in '12345678':
            print("Invalid input. Please use the format 'e2 e4'.")
            continue

        start = (8 - int(start[1]), ord(start[0]) - ord('a'))
        end = (8 - int(end[1]), ord(end[0]) - ord('a'))

        if turn != chess_board.board[start[0]][start[1]].color:
            print("It's not your turn.")
            continue

        if not chess_board.move_piece(turn, start, end, new_piece_id):
            print("Invalid move. Try again.")
        else:
            turn = 'black' if turn == 'white' else 'white'

        chess_board.view_board()

        if chess_board.is_checkmate(turn):
            print(f"Checkmate! {turn} loses.")
            break

        elif chess_board.is_stalemate(turn):
            print(f"Stalemate! The game is a draw.")
            break

if __name__ == "__main__":
    main()