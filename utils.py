import argparse

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "--model1_type",
        type=str,
        default="transformer"
    )

    parser.add_argument(
        "--model1_weight",
        type=str,
        default="./weights/transformer/chess_ppo_1600.pth"
    )

    parser.add_argument(
        "--model2_type",
        type=str,
        default=None
    )

    parser.add_argument(
        "--model2_weight",
        type=str,
        default=None
    )

    parser.add_argument(
        "--ai_role",
        type=str,
        default="white"
    )

    parser.add_argument(
        "--train_start_num",
        type=int,
        default=0
    )

    return parser.parse_args()