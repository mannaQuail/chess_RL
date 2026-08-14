from chess_board import ChessBoard, making_input_board, making_mask, action_parser
from pieces import Pawn, Rook, Knight, Bishop, Queen, King
from model import ChessNet, ChessNetTransformer
from utils import parse_args

import torch

class Puzzle:
    def __init__(self):
        self.one_move_mate = []
        self.one_move_mate_answer = []
        self.one_move_mate_num = 3

    def makeOneMatePuzzle(self):
        for i in range(self.one_move_mate_num):
            self.one_move_mate.append(ChessBoard(False))
            
        

        self.one_move_mate[0].board[0][0] = Rook('black')
        self.one_move_mate[0].board[1][2] = Rook('black')
        self.one_move_mate[0].board[0][3] = Queen('black')
        self.one_move_mate[0].board[4][4] = Knight('black')
        self.one_move_mate[0].board[3][0] = Pawn('black')
        self.one_move_mate[0].board[3][3] = Pawn('black')
        self.one_move_mate[0].board[2][4] = Pawn('black')
        self.one_move_mate[0].board[1][6] = Pawn('black')
        self.one_move_mate[0].board[2][7] = Pawn('black')
        self.one_move_mate[0].board[3][4] = King('black')
    
        self.one_move_mate[0].board[7][0] = Rook('white')
        self.one_move_mate[0].board[7][5] = Rook('white')
        self.one_move_mate[0].board[1][5] = Queen('white')
        self.one_move_mate[0].board[3][1] = Pawn('white')
        self.one_move_mate[0].board[5][2] = Pawn('white')
        self.one_move_mate[0].board[5][4] = Pawn('white')
        self.one_move_mate[0].board[5][6] = Pawn('white')
        self.one_move_mate[0].board[6][5] = Pawn('white')
        self.one_move_mate[0].board[6][6] = Pawn('white')
        self.one_move_mate[0].board[7][6] = King('white')

        self.one_move_mate_answer.append("f7 f4")

        self.one_move_mate[1].board[0][0] = Rook('black')
        self.one_move_mate[1].board[7][2] = Rook('black')
        self.one_move_mate[1].board[7][3] = Queen('black')
        self.one_move_mate[1].board[3][0] = Pawn('black')
        self.one_move_mate[1].board[4][1] = Pawn('black')
        self.one_move_mate[1].board[1][5] = Pawn('black')
        self.one_move_mate[1].board[1][7] = Pawn('black')
        self.one_move_mate[1].board[0][5] = King('black')

        self.one_move_mate[1].board[6][4] = Rook('white')
        self.one_move_mate[1].board[3][4] = Queen('white')
        self.one_move_mate[1].board[4][0] = Pawn('white')
        self.one_move_mate[1].board[6][1] = Pawn('white')
        self.one_move_mate[1].board[6][5] = Pawn('white')
        self.one_move_mate[1].board[5][6] = Pawn('white')
        self.one_move_mate[1].board[6][7] = Pawn('white')

        self.one_move_mate_answer.append("e5 h8")

        self.one_move_mate[2].board[0][2] = Rook('black')
        self.one_move_mate[2].board[0][7] = Rook('black')
        self.one_move_mate[2].board[0][4] = King('black')
        self.one_move_mate[2].board[0][5] = Bishop('black')
        self.one_move_mate[2].board[1][3] = Bishop('black')
        self.one_move_mate[2].board[2][5] = Knight('black')
        self.one_move_mate[2].board[3][4] = Knight('black')
        self.one_move_mate[2].board[2][3] = Queen('black')
        self.one_move_mate[2].board[1][4] = Pawn('black')
        self.one_move_mate[2].board[1][5] = Pawn('black')
        self.one_move_mate[2].board[1][6] = Pawn('black')
        self.one_move_mate[2].board[1][7] = Pawn('black')


        self.one_move_mate[2].board[7][1] = Rook('white')
        self.one_move_mate[2].board[7][7] = Rook('white')
        self.one_move_mate[2].board[1][1] = Queen('white')
        self.one_move_mate[2].board[3][1] = Bishop('white')
        self.one_move_mate[2].board[6][4] = Knight('white')
        self.one_move_mate[2].board[7][4] = King('white')
        self.one_move_mate[2].board[6][0] = Pawn('white')
        self.one_move_mate[2].board[6][2] = Pawn('white')
        self.one_move_mate[2].board[6][3] = Pawn('white')
        self.one_move_mate[2].board[6][5] = Pawn('white')
        self.one_move_mate[2].board[6][6] = Pawn('white')
        self.one_move_mate[2].board[6][7] = Pawn('white')

        self.one_move_mate_answer.append("b7 c8")

        return self.one_move_mate


def testing_model(model, puzzles):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    state = torch.tensor([0,0,0,0,0], dtype=torch.float32).to(device)

    answer_num = 0

    for i, puzzle in enumerate(puzzles.makeOneMatePuzzle()):
        puzzle.view_board()
        input_board = making_input_board(puzzle.board, puzzle.en_passant_target).to(device)
        state[0] = 0
        
        state[1:] = torch.tensor(puzzle.get_castling_rights(), dtype=torch.float32)

        policy, value = model(input_board.unsqueeze(0), state.unsqueeze(0))  # Add batch dimension
                    
        valid_mask = making_mask(puzzle, 'white').to(device)
        policy = policy.masked_fill(~valid_mask, -torch.inf)  # Mask invalid moves

        action = torch.argmax(policy, dim=-1)  # Select the move with the highest probability

        start_net, end_net, new_piece_id_net = action_parser(action)
        print(f"Turn: 'white', Move: {chr(ord('a')+start_net[1])}{8 - int(start_net[0])} to {chr(ord('a')+end_net[1])}{8 - int(end_net[0])}, Promotion: {new_piece_id_net}, Value: {value.item()}")

        print()
        if f"{chr(ord('a')+start_net[1])}{8 - int(start_net[0])} {chr(ord('a')+end_net[1])}{8 - int(end_net[0])}" == puzzles.one_move_mate_answer[i]:
            print("correct\n")
            answer_num += 1
        else:
            print("wrong\n")

    print(f"Total Correct Num: {answer_num}/{puzzles.one_move_mate_num}")



def main():
    args = parse_args()

    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

    puzzle = Puzzle()

    if args.model1_type=="cnn":
        chess_net1 = ChessNet().to(device)
    else:
        chess_net1 = ChessNetTransformer().to(device)
    
    chess_net1.load_state_dict(torch.load(args.model1_weight, map_location=device))
    chess_net1.to(device)

    chess_net1.eval()  # Set the model to evaluation mode

    testing_model(chess_net1, puzzle)

if __name__ == '__main__':
    main()