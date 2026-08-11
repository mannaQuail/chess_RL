class Pawn:
    def __init__(self, color):
        self.color = color
        self.symbol = '♙' if color == 'white' else '♟'

    def is_valid_move(self, start_pos, end_pos, board):
        # Pawns move forward one square, but can move two squares from their starting position
        direction = -1 if self.color == 'white' else 1
        row_diff = end_pos[0] - start_pos[0]
        col_diff = abs(start_pos[1] - end_pos[1])

        # Normal move
        if row_diff == direction and col_diff == 0:
            if board[end_pos[0]][end_pos[1]] is None:
                return True
        # Initial double move
        if (start_pos[0] == 1 and self.color == 'black') or (start_pos[0] == 6 and self.color == 'white'):
            if row_diff == 2 * direction and col_diff == 0:
                if board[start_pos[0] + direction][start_pos[1]] is None and board[end_pos[0]][end_pos[1]] is None:
                    return True
        # Capture move
        if row_diff == direction and col_diff == 1:
            if board[end_pos[0]][end_pos[1]] is not None:
                return True

        return False

class Knight:
    def __init__(self, color):
        self.color = color
        self.symbol = '♘' if color == 'white' else '♞'

    def is_valid_move(self, start_pos, end_pos, board):
        # Knights move in an L-shape: two squares in one direction and one square perpendicular
        row_diff = abs(start_pos[0] - end_pos[0])
        col_diff = abs(start_pos[1] - end_pos[1])
        return (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2)
    
class Bishop:
    def __init__(self, color):
        self.color = color
        self.symbol = '♗' if color == 'white' else '♝'

    def is_valid_move(self, start_pos, end_pos, board):
        # Bishops move diagonally, so the absolute difference between the row and column must be equal
        start_row, start_col = start_pos
        end_row, end_col = end_pos

        # 대각선 이동인지 확인
        if abs(end_row - start_row) != abs(end_col - start_col):
            return False

        # 이동 방향
        row_step = 1 if end_row > start_row else -1
        col_step = 1 if end_col > start_col else -1

        # 시작점 다음 칸
        row = start_row + row_step
        col = start_col + col_step

        # 도착지 전까지 blocking 검사
        while (row, col) != (end_row, end_col):
            if board[row][col] is not None:
                return False

            row += row_step
            col += col_step

        return True

class Rook:
    def __init__(self, color):
        self.color = color
        self.symbol = '♖' if color == 'white' else '♜'

    def is_valid_move(self, start_pos, end_pos, board):
        # Rooks move in straight lines, so either the row or column must be the same
        if start_pos[0] == end_pos[0] or start_pos[1] == end_pos[1]:
            # Check if there are any pieces in the way
            if start_pos[0] == end_pos[0]:  # Horizontal move
                col_start, col_end = sorted([start_pos[1], end_pos[1]])
                for col in range(col_start + 1, col_end):
                    if board[start_pos[0]][col] is not None:
                        return False
                    
            else:  # Vertical move
                row_start, row_end = sorted([start_pos[0], end_pos[0]])
                for row in range(row_start + 1, row_end):
                    if board[row][start_pos[1]] is not None:
                        return False
            return True
        
        return False

class Queen:
    def __init__(self, color):
        self.color = color
        self.symbol = '♕' if color == 'white' else '♛'

    def is_valid_move(self, start_pos, end_pos, board):
        start_row, start_col = start_pos
        end_row, end_col = end_pos

        row_diff = end_row - start_row
        col_diff = end_col - start_col

        # 1. 직선 이동인지 확인
        is_straight = (start_row == end_row or start_col == end_col)

        # 2. 대각선 이동인지 확인
        is_diagonal = (abs(row_diff) == abs(col_diff))

        if not (is_straight or is_diagonal):
            return False

        # 이동 방향 계산
        row_step = 0 if row_diff == 0 else (1 if row_diff > 0 else -1)
        col_step = 0 if col_diff == 0 else (1 if col_diff > 0 else -1)

        # 시작점 다음 칸부터 도착지 직전까지 검사
        row = start_row + row_step
        col = start_col + col_step

        while (row, col) != (end_row, end_col):
            if board[row][col] is not None:
                return False

            row += row_step
            col += col_step

        return True

class King:
    def __init__(self, color):
        self.color = color
        self.symbol = '♔' if color == 'white' else '♚'

    def is_valid_move(self, start_pos, end_pos, board):
        # Kings move one square in any direction
        row_diff = abs(start_pos[0] - end_pos[0])
        col_diff = abs(start_pos[1] - end_pos[1])
        return row_diff <= 1 and col_diff <= 1