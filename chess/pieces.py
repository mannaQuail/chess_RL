class Pawn:
    def __init__(self, color):
        self.color = color
        self.symbol = '♙' if color == 'white' else '♟'

    def is_valid_move(self, start_pos, end_pos):
        # Pawns move forward one square, but can move two squares from their starting position
        direction = -1 if self.color == 'white' else 1
        row_diff = end_pos[0] - start_pos[0]
        col_diff = abs(start_pos[1] - end_pos[1])

        # Normal move
        if row_diff == direction and col_diff == 0:
            return True
        # Initial double move
        if (start_pos[0] == 1 and self.color == 'black') or (start_pos[0] == 6 and self.color == 'white'):
            if row_diff == 2 * direction and col_diff == 0:
                return True
        # Capture move
        if row_diff == direction and col_diff == 1:
            return True

        return False

class Knight:
    def __init__(self, color):
        self.color = color
        self.symbol = '♘' if color == 'white' else '♞'

    def is_valid_move(self, start_pos, end_pos):
        # Knights move in an L-shape: two squares in one direction and one square perpendicular
        row_diff = abs(start_pos[0] - end_pos[0])
        col_diff = abs(start_pos[1] - end_pos[1])
        return (row_diff == 2 and col_diff == 1) or (row_diff == 1 and col_diff == 2)
    
class Bishop:
    def __init__(self, color):
        self.color = color
        self.symbol = '♗' if color == 'white' else '♝'

    def is_valid_move(self, start_pos, end_pos):
        # Bishops move diagonally, so the absolute difference between the row and column must be equal
        row_diff = abs(start_pos[0] - end_pos[0])
        col_diff = abs(start_pos[1] - end_pos[1])
        return row_diff == col_diff

class Rook:
    def __init__(self, color):
        self.color = color
        self.symbol = '♖' if color == 'white' else '♜'

    def is_valid_move(self, start_pos, end_pos):
        # Rooks move in straight lines, so either the row or column must be the same
        return start_pos[0] == end_pos[0] or start_pos[1] == end_pos[1]

class Queen:
    def __init__(self, color):
        self.color = color
        self.symbol = '♕' if color == 'white' else '♛'

    def is_valid_move(self, start_pos, end_pos):
        # Queens can move like both bishops and rooks
        row_diff = abs(start_pos[0] - end_pos[0])
        col_diff = abs(start_pos[1] - end_pos[1])
        return (row_diff == col_diff) or (start_pos[0] == end_pos[0] or start_pos[1] == end_pos[1])

class King:
    def __init__(self, color):
        self.color = color
        self.symbol = '♔' if color == 'white' else '♚'

    def is_valid_move(self, start_pos, end_pos):
        # Kings move one square in any direction
        row_diff = abs(start_pos[0] - end_pos[0])
        col_diff = abs(start_pos[1] - end_pos[1])
        return row_diff <= 1 and col_diff <= 1