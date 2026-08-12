import torch
import torch.nn as nn


class ChessNet(nn.Module):
    def __init__(self):
        super().__init__()

        # --------------------------------
        # Board input
        # 12 piece channels
        # + 1 en-passant channel
        # = 13 channels
        # --------------------------------
        self.board_backbone = nn.Sequential(
            nn.Conv2d(13, 64, kernel_size=3, padding=1),
            nn.ReLU(),

            nn.Conv2d(64, 64, kernel_size=3, padding=1),
            nn.ReLU(),

            nn.Conv2d(64, 128, kernel_size=3, padding=1),
            nn.ReLU(),

            nn.Flatten()
        )

        # 128 * 8 * 8
        board_feature_dim = 128 * 8 * 8

        # --------------------------------
        # Game state
        #
        # 0: side to move
        # 1: white kingside castling
        # 2: white queenside castling
        # 3: black kingside castling
        # 4: black queenside castling
        # --------------------------------
        self.state_encoder = nn.Sequential(
            nn.Linear(5, 32),
            nn.ReLU(),
            nn.Linear(32, 32),
            nn.ReLU()
        )

        # --------------------------------
        # Combine board + state
        # --------------------------------
        combined_dim = board_feature_dim + 32

        # --------------------------------
        # Policy head
        # 8*8*8*8 = 4096
        # --------------------------------
        self.policy_head = nn.Sequential(
            nn.Linear(combined_dim, 512),
            nn.ReLU(),
            nn.Linear(512, 4096)
        )

        # --------------------------------
        # Value head
        # --------------------------------
        self.value_head = nn.Sequential(
            nn.Linear(combined_dim, 512),
            nn.ReLU(),
            nn.Linear(512, 1),
            nn.Tanh()
        )

    def forward(self, board, state):
        """
        board:
            [batch, 13, 8, 8]

        state:
            [batch, 5]

        returns:
            policy: [batch, 4096]
            value:  [batch, 1]
        """

        board_feature = self.board_backbone(board)

        state_feature = self.state_encoder(state)

        feature = torch.cat(
            [board_feature, state_feature],
            dim=1
        )

        policy = self.policy_head(feature)
        value = self.value_head(feature)

        return policy, value