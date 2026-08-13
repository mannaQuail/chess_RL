import copy
import torch
from torch.distributions import Categorical

from pieces import Pawn, Rook, Knight, Bishop, Queen, King
from model import ChessNet

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

    def get_castling_rights(self):
        rights = [
            False,  # white kingside
            False,  # white queenside
            False,  # black kingside
            False   # black queenside
        ]

        # White
        white_king = self.board[7][4]

        if isinstance(white_king, King) and not white_king.has_moved:
            rook = self.board[7][7]
            if isinstance(rook, Rook) and rook.color == 'white' and not rook.has_moved:
                rights[0] = True

            rook = self.board[7][0]
            if isinstance(rook, Rook) and rook.color == 'white' and not rook.has_moved:
                rights[1] = True

        # Black
        black_king = self.board[0][4]

        if isinstance(black_king, King) and not black_king.has_moved:
            rook = self.board[0][7]
            if isinstance(rook, Rook) and rook.color == 'black' and not rook.has_moved:
                rights[2] = True

            rook = self.board[0][0]
            if isinstance(rook, Rook) and rook.color == 'black' and not rook.has_moved:
                rights[3] = True

        return rights

    def get_position_key(self, turn):
        board_state = []

        for row in range(8):
            for col in range(8):
                piece = self.board[row][col]

                if piece is None:
                    board_state.append(None)
                else:
                    board_state.append(
                        (
                            piece.color,
                            piece.__class__.__name__
                        )
                    )

        return (
            tuple(board_state),
            turn,
            tuple(self.get_castling_rights()),
            self.en_passant_target
        )

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

def making_input_board(board, en_passant_target):
    input_board = torch.zeros((13, 8, 8), dtype=torch.float32)
    for row in range(8):
        for col in range(8):
            piece = board[row][col]
            if piece is not None:
                piece_index = {
                    'white': {
                        'Pawn': 0,
                        'Rook': 1,
                        'Knight': 2,
                        'Bishop': 3,
                        'Queen': 4,
                        'King': 5
                    },
                    'black': {
                        'Pawn': 6,
                        'Rook': 7,
                        'Knight': 8,
                        'Bishop': 9,
                        'Queen': 10,
                        'King': 11
                    }
                }[piece.color][piece.__class__.__name__]
                input_board[piece_index, row, col] = 1.0

            if isinstance(piece, Pawn) and en_passant_target is not None:
                if (row, col) == en_passant_target:
                    input_board[12, row, col] = 1.0

    return input_board

def making_mask(board, turn):
    valid_mask = torch.zeros(4272, dtype=torch.bool)  # Adjusted size for 4272 possible moves

    for start_row in range(8):
        for start_col in range(8):
            piece = board.board[start_row][start_col]
            if piece is not None and piece.color == turn:
                for end_row in range(8):
                    for end_col in range(8):
                        if (start_row, start_col) != (end_row, end_col):
                            if board.move_piece(turn, (start_row, start_col), (end_row, end_col), judge=True):
                                move_index = (
                                    start_row * 8 * 8 * 8 +
                                    start_col * 8 * 8 +
                                    end_row * 8 +
                                    end_col
                                )
                                valid_mask[move_index] = True

                        if isinstance(piece, Pawn):
                            if piece.color == 'white' and start_row == 1 and end_row == 0 and abs(start_col - end_col) <= 1:
                                for new_piece_id in range(4):
                                    if board.move_piece(turn, (start_row, start_col), (end_row, end_col), new_piece_id, judge=True):
                                        if start_col == end_col:
                                            move_index = (
                                                4096 +
                                                start_col * 4 + 
                                                new_piece_id
                                            )
                                        elif start_col < end_col:
                                            move_index = (
                                                4096 +
                                                32 + 
                                                start_col * 4 + 
                                                new_piece_id
                                            )
                                        else:
                                            move_index = (
                                                4096 +
                                                32 + 28 +
                                                end_col * 4 + 
                                                new_piece_id
                                            )

                                        off_move_index = (
                                            start_row * 8 * 8 * 8 +
                                            start_col * 8 * 8 +
                                            end_row * 8 +
                                            end_col
                                        )

                                        valid_mask[move_index] = True
                                        valid_mask[off_move_index] = False

                            elif piece.color == 'black' and start_row == 6 and end_row == 7 and abs(start_col - end_col) <= 1:
                                for new_piece_id in range(4):
                                    if board.move_piece(turn, (start_row, start_col), (end_row, end_col), new_piece_id, judge=True):
                                        if start_col == end_col:
                                            move_index = (
                                                4096 +
                                                88 +
                                                start_col * 4 + 
                                                new_piece_id
                                            )
                                        elif start_col < end_col:
                                            move_index = (
                                                4096 +
                                                88 + 32 +
                                                start_col * 4 + 
                                                new_piece_id
                                            )
                                        else:
                                            move_index = (
                                                4096 +
                                                88 + 32 + 28 +
                                                end_col * 4 + 
                                                new_piece_id
                                            )
                                        off_move_index = (
                                            start_row * 8 * 8 * 8 +
                                            start_col * 8 * 8 +
                                            end_row * 8 +
                                            end_col
                                        )
                                        valid_mask[move_index] = True
                                        valid_mask[off_move_index] = False

    return valid_mask

def action_parser(action):
    if action < 4096:
        start_row = action // (8 * 8 * 8)
        start_col = (action // (8 * 8)) % 8
        end_row = (action // 8) % 8
        end_col = action % 8
        return (start_row, start_col), (end_row, end_col), None
    elif action >= 4096 and action < 4184:
        promotion_action = action - 4096
        if promotion_action < 32:
            start_row = 1
            start_col = promotion_action // 4
            end_row = 0
            end_col = start_col
            new_piece_id = promotion_action % 4
        elif promotion_action < 60:
            promotion_action -= 32
            start_row = 1
            start_col = promotion_action // 4 + 1
            end_row = 0
            end_col = start_col - 1
            new_piece_id = promotion_action % 4
        elif promotion_action < 88:
            promotion_action -= 60
            start_row = 1
            start_col = promotion_action // 4 + 2
            end_row = 0
            end_col = start_col - 2
            new_piece_id = promotion_action % 4
    else:
        promotion_action = action - 4184
        if promotion_action < 32:
            start_row = 6
            start_col = promotion_action // 4
            end_row = 7
            end_col = start_col
            new_piece_id = promotion_action % 4
        elif promotion_action < 60:
            promotion_action -= 32
            start_row = 6
            start_col = promotion_action // 4 + 1
            end_row = 7
            end_col = start_col - 1
            new_piece_id = promotion_action % 4
        elif promotion_action < 88:
            promotion_action -= 60
            start_row = 6
            start_col = promotion_action // 4 + 2
            end_row = 7
            end_col = start_col - 2
            new_piece_id = promotion_action % 4

        return (start_row, start_col), (end_row, end_col), new_piece_id

def main():
    chess_board = ChessBoard()

    position_history = {}

    initial_key = chess_board.get_position_key('white')
    position_history[initial_key] = 1

    chess_board.view_board()
    chess_net = ChessNet()
    chess_net.eval()  # Set the model to evaluation mode

    state = torch.tensor([0,0,0,0,0], dtype=torch.float32)  # Example state tensor, adjust as needed

    turn = 'white'
    while True:
        input_board = making_input_board(chess_board.board, chess_board.en_passant_target)

        state[0] = 0 if turn == 'white' else 1

        state[1:] = torch.tensor(chess_board.get_castling_rights(), dtype=torch.float32)

        print(chess_board.get_castling_rights())
        
        
        policy, value = chess_net(input_board.unsqueeze(0), state.unsqueeze(0))  # Add batch dimension
    
        valid_mask = making_mask(chess_board, turn)
        policy = policy.masked_fill(~valid_mask, -torch.inf)  # Mask invalid moves

        action = torch.argmax(policy, dim=-1)  # Select the move with the highest probability

        start_net, end_net, new_piece_id_net = action_parser(action)
        print(f"Turn: {turn}, Move: {chr(ord('a')+start_net[1])}{8 - int(start_net[0])} to {chr(ord('a')+end_net[1])}{8 - int(end_net[0])}, Promotion: {new_piece_id_net}")

        # dist = Categorical(logits=policy)

        # action = dist.sample()
        # log_prob = dist.log_prob(action)

        # input_move = input("Enter your move (e.g., 'e2 e4'): ")
        if new_piece_id_net == None:
            input_move = f"{chr(ord('a')+start_net[1])}{8 - int(start_net[0])} {chr(ord('a')+end_net[1])}{8 - int(end_net[0])}"
        else:
            input_move = f"{chr(ord('a')+start_net[1])}{8 - int(start_net[0])} {chr(ord('a')+end_net[1])}{8 - int(end_net[0])}={new_piece_id_net}"

        print(f"AI Move: {input_move}")


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

        if chess_board.board[start[0]][start[1]] is None:
            print("No piece at the starting position.")
            continue

        if turn != chess_board.board[start[0]][start[1]].color:
            print("It's not your turn.")
            continue

        if not chess_board.move_piece(turn, start, end, new_piece_id):
            print("Invalid move. Try again.")
            continue

        turn = 'black' if turn == 'white' else 'white'

        # 현재 position 기록
        position_key = chess_board.get_position_key(turn)

        position_history[position_key] = (
            position_history.get(position_key, 0) + 1
        )

        chess_board.view_board()

        # Threefold repetition
        if position_history[position_key] >= 3:
            print("Draw by threefold repetition.")
            break

        if chess_board.is_checkmate(turn):
            print(f"Checkmate! {turn} loses.")
            break

        elif chess_board.is_stalemate(turn):
            print(f"Stalemate! The game is a draw.")
            break

if __name__ == "__main__":
    main()