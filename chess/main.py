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

    def move_piece(self, start_pos, end_pos):
        piece = self.board[start_pos[0]][start_pos[1]]
        if piece and piece.is_valid_move(start_pos, end_pos):
            self.board[end_pos[0]][end_pos[1]] = piece
            self.board[start_pos[0]][start_pos[1]] = None
            return True
        return False


    def view_board(self):
        for row in self.board:
            print(' '.join([piece.symbol if piece else '.' for piece in row]))

def main():
    chess_board = ChessBoard()
    chess_board.view_board()
    turn = 'white'
    while True:
        input_move = input("Enter your move (e.g., 'e2 e4'): ")
        start, end = input_move.split()
        if start[0] not in 'abcdefgh' or end[0] not in 'abcdefgh' or start[1] not in '12345678' or end[1] not in '12345678':
            print("Invalid input. Please use the format 'e2 e4'.")
            continue

        start = (8 - int(start[1]), ord(start[0]) - ord('a'))
        end = (8 - int(end[1]), ord(end[0]) - ord('a'))
        print(start, end)

        if turn != chess_board.board[start[0]][start[1]].color:
            print("It's not your turn.")
            continue

        if not chess_board.move_piece(start, end):
            print("Invalid move. Try again.")
        else:
            turn = 'black' if turn == 'white' else 'white'

        chess_board.view_board()

if __name__ == "__main__":
    main()