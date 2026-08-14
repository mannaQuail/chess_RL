import torch

from model import ChessNet, ChessNetTransformer
from ppo import PPOTrainer
from chess_board import ChessBoard, making_input_board, making_mask, action_parser


def make_state(board, turn):
    state = torch.zeros(5, dtype=torch.float32)

    # white = 0, black = 1
    state[0] = 0 if turn == "white" else 1

    state[1:] = torch.tensor(
        board.get_castling_rights(),
        dtype=torch.float32
    )

    return state


def create_trajectory():
    return {
        "boards": [],
        "states": [],
        "masks": [],
        "actions": [],
        "log_probs": [],
        "values": [],
        "rewards": [],
        "dones": [],
    }


def play_game(trainer, device, max_moves=200):

    board = ChessBoard()
    turn = "white"

    # White / Black trajectory를 따로 관리
    trajectories = {
        "white": create_trajectory(),
        "black": create_trajectory(),
    }

    # Threefold repetition
    position_history = {}

    position_key = board.get_position_key(turn)
    position_history[position_key] = 1

    for move_idx in range(max_moves):

        # -----------------------------------
        # State
        # -----------------------------------

        input_board = making_input_board(
            board.board,
            board.en_passant_target
        )

        state = make_state(board, turn)

        # -----------------------------------
        # Legal action mask
        # -----------------------------------

        valid_mask = making_mask(
            board,
            turn
        )

        if not valid_mask.any():
            print("No legal moves.")
            break

        # -----------------------------------
        # Select action
        # -----------------------------------

        (
            action,
            log_prob,
            value
        ) = trainer.select_action(
            input_board.to(device),
            state.to(device),
            valid_mask.to(device)
        )

        # -----------------------------------
        # Save transition
        # -----------------------------------

        trajectory = trajectories[turn]

        trajectory["boards"].append(
            input_board
        )

        trajectory["states"].append(
            state
        )

        trajectory["masks"].append(
            valid_mask
        )

        trajectory["actions"].append(
            action.detach().cpu()
        )

        trajectory["log_probs"].append(
            log_prob.detach().cpu()
        )

        trajectory["values"].append(
            value.detach().cpu()
        )

        trajectory["rewards"].append(0.0)
        trajectory["dones"].append(False)

        # -----------------------------------
        # Execute action
        # -----------------------------------

        start, end, promotion = action_parser(
            action.item()
        )

        success = board.move_piece(
            turn,
            start,
            end,
            promotion
        )

        if not success:
            raise RuntimeError(
                f"Invalid action sampled: {turn}, {action.item()}"
            )

        # -----------------------------------
        # Switch turn
        # -----------------------------------

        player = turn

        turn = (
            "black"
            if turn == "white"
            else "white"
        )

        # -----------------------------------
        # Check terminal state
        # -----------------------------------

        done = False
        winner = None


        threefold_repetition = False

        # Checkmate
        if board.is_checkmate(turn):

            done = True
            winner = player

        # Stalemate
        elif board.is_stalemate(turn):

            done = True
            winner = None

            print("Stalemate!")

        # Threefold repetition
        else:

            position_key = board.get_position_key(turn)

            position_history[position_key] = (
                position_history.get(position_key, 0) + 1
            )

            if position_history[position_key] >= 3:

                done = True
                winner = None
                threefold_repetition = True

                print("Threefold repetition!")

        # -----------------------------------
        # Game finished
        # -----------------------------------

        if done:

            if winner == "white":

                # White 승리
                trajectories["white"]["rewards"][-1] = 1.0
                trajectories["black"]["rewards"][-1] = -1.0

                board.view_board()

            elif winner == "black":

                # Black 승리
                trajectories["white"]["rewards"][-1] = -1.0
                trajectories["black"]["rewards"][-1] = 1.0

                board.view_board()

            else:
                # Draw
                if threefold_repetition:
                    # Threefold repetition
                    trajectories["white"]["rewards"][-1] = -0.01
                    trajectories["black"]["rewards"][-1] = 0.01
                else:
                    trajectories["white"]["rewards"][-1] = -0.01
                    trajectories["black"]["rewards"][-1] = 0.01

            # 실제 게임 종료
            trajectories["white"]["dones"][-1] = True
            trajectories["black"]["dones"][-1] = True

            

            break

        # -----------------------------------
        # Continue game
        # -----------------------------------


    return trajectories, winner, move_idx + 1


def convert_trajectory(trajectory):

    boards = torch.stack(
        trajectory["boards"]
    )

    states = torch.stack(
        trajectory["states"]
    )

    masks = torch.stack(
        trajectory["masks"]
    )

    actions = torch.stack(
        trajectory["actions"]
    )

    log_probs = torch.stack(
        trajectory["log_probs"]
    )

    values = torch.stack(
        trajectory["values"]
    ).squeeze(-1)

    rewards = torch.tensor(
        trajectory["rewards"],
        dtype=torch.float32
    )

    dones = torch.tensor(
        trajectory["dones"],
        dtype=torch.float32
    )

    return (
        boards,
        states,
        actions,
        log_probs,
        values,
        rewards,
        dones,
        masks
    )


def main():
    print("Starting training...")
    # -----------------------------------
    # Device
    # -----------------------------------

    device = torch.device(
        "cuda"
        if torch.cuda.is_available()
        else "cpu"
    )

    print("Device:", device)

    # -----------------------------------
    # Model
    # -----------------------------------

    starting_step = 1400
    weight_name = f"./weights/transformer/chess_ppo_{starting_step}.pth"

    # model = ChessNet().to(device)
    model = ChessNetTransformer().to(device)
    model.load_state_dict(
        torch.load(weight_name, map_location=device)
    )

    # -----------------------------------
    # PPO
    # -----------------------------------

    trainer = PPOTrainer(
        model=model,
        lr=3e-4,
        gamma=0.99,
        gae_lambda=0.95,
        clip_eps=0.2,
        value_coef=0.5,
        entropy_coef=0.04,
        update_epochs=4,
    )

    # -----------------------------------
    # Training
    # -----------------------------------

    num_games = 40000
    num_white_wins = 0
    num_black_wins = 0
    num_draws = 0

    for game in range(starting_step, num_games):

        trajectories, winner, num_moves = play_game(
            trainer,
            device
        )

        print(
            f"Game {game + 1:05d} | "
            f"Winner: {winner} | "
            f"Moves: {num_moves}"
        )
            

        # -----------------------------------
        # PPO update
        # -----------------------------------

        for player in ["white", "black"]:

            trajectory = trajectories[player]

            if len(trajectory["actions"]) == 0:
                continue

            (
                boards,
                states,
                actions,
                old_log_probs,
                values,
                rewards,
                dones,
                masks
            ) = convert_trajectory(
                trajectory
            )

            # GAE
            advantages, returns = trainer.compute_gae(
                rewards,
                values,
                dones
            )

            # Advantage normalization
            advantages = (
                advantages - advantages.mean()
            ) / (
                advantages.std() + 1e-8
            )

            # PPO update
            loss_info = trainer.update(
                boards.to(device),
                states.to(device),
                actions.to(device),
                old_log_probs.to(device),
                returns.to(device),
                advantages.to(device),
                masks.to(device)
            )

        # -----------------------------------
        # Save model
        # -----------------------------------

        if (game + 1) % 800 == 0:

            torch.save(
                model.state_dict(),
                f"./weights/transformer/chess_ppo_{game + 1}.pth"
            )

            print(
                f"Model saved: ./weights/transformer/chess_ppo_{game + 1}.pth"
            )



if __name__ == "__main__":
    main()