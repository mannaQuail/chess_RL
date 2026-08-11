import copy
from pieces import Pawn, Rook, Knight, Bishop, Queen, King

class ChessBoard:
    def __init__(self):
        self.board = [[None for _ in range(8)] for _ in range(8)]
        self.setup_board()

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

    def move_piece(self, turn, start_pos, end_pos, new_piece_id=None, judge=False):
        piece = self.board[start_pos[0]][start_pos[1]]
        tmp_board = copy.deepcopy(self.board)

        if piece and piece.is_valid_move(start_pos, end_pos, self.board):
            if self.board[end_pos[0]][end_pos[1]] is not None:
                if self.board[end_pos[0]][end_pos[1]].color == turn:
                    return False



            self.board[end_pos[0]][end_pos[1]] = piece
            self.board[start_pos[0]][start_pos[1]] = None

            if new_piece_id is not None:
                if not self.promote_pawn(end_pos, new_piece_id):
                    self.board = tmp_board  # Revert the move
                    return False

            if self.is_in_check(turn):
                self.board = tmp_board  # Revert the move
                return False

            if judge:
                self.board = tmp_board  # Revert the move for judge mode

            return True

        return False

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