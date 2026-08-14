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
            nn.Linear(512, 4272)  # 4096 for moves + 176 for promotions
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
            policy: [batch, 4272]
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

class ChessNetTransformer(nn.Module):
    def __init__(
        self,
        d_model=128,
        nhead=8,
        num_layers=4,
        dim_feedforward=512,
        dropout=0.1
    ):
        super().__init__()

        # =========================================================
        # Board
        # =========================================================
        # Input:
        #   [B, 13, 8, 8]
        #
        # 13 channels:
        #   0~5   white pieces
        #   6~11  black pieces
        #   12    en-passant
        #
        # 각 square를 하나의 token으로 사용
        # → 64 tokens
        # =========================================================

        self.square_embedding = nn.Linear(
            13,
            d_model
        )

        # 8 x 8 positional embedding
        self.position_embedding = nn.Parameter(
            torch.randn(1, 64, d_model) * 0.02
        )

        # =========================================================
        # Game state
        # =========================================================
        #
        # state:
        #   [side_to_move,
        #    white_kingside,
        #    white_queenside,
        #    black_kingside,
        #    black_queenside]
        #
        # 하나의 additional token으로 사용
        # =========================================================

        self.state_encoder = nn.Sequential(
            nn.Linear(5, d_model),
            nn.ReLU(),
            nn.Linear(d_model, d_model)
        )

        # =========================================================
        # CLS token
        # =========================================================

        self.cls_token = nn.Parameter(
            torch.randn(1, 1, d_model) * 0.02
        )

        # =========================================================
        # Transformer
        # =========================================================

        encoder_layer = nn.TransformerEncoderLayer(
            d_model=d_model,
            nhead=nhead,
            dim_feedforward=dim_feedforward,
            dropout=dropout,
            activation="gelu",
            batch_first=True,
            norm_first=True
        )

        self.transformer = nn.TransformerEncoder(
            encoder_layer,
            num_layers=num_layers
        )

        self.norm = nn.LayerNorm(d_model)

        # =========================================================
        # Policy head
        # =========================================================
        #
        # CLS feature → 4272 actions
        #
        # 4096 normal moves
        # + 176 promotion moves
        # =========================================================

        self.policy_head = nn.Sequential(
            nn.Linear(d_model, 512),
            nn.GELU(),
            nn.Linear(512, 4272)
        )

        # =========================================================
        # Value head
        # =========================================================

        self.value_head = nn.Sequential(
            nn.Linear(d_model, 256),
            nn.GELU(),
            nn.Linear(256, 1),
            nn.Tanh()
        )

    def forward(self, board, state):

        # =========================================================
        # Board → square tokens
        # =========================================================

        # [B, 13, 8, 8]
        B = board.shape[0]

        # [B, 8, 8, 13]
        board = board.permute(
            0, 2, 3, 1
        )

        # [B, 64, 13]
        board = board.reshape(
            B,
            64,
            13
        )

        # [B, 64, d_model]
        board_tokens = self.square_embedding(
            board
        )

        # Position embedding
        board_tokens = (
            board_tokens
            + self.position_embedding
        )

        # =========================================================
        # State token
        # =========================================================

        # [B, d_model]
        state_token = self.state_encoder(
            state
        )

        # [B, 1, d_model]
        state_token = state_token.unsqueeze(1)

        # =========================================================
        # CLS token
        # =========================================================

        # [B, 1, d_model]
        cls_token = self.cls_token.expand(
            B,
            -1,
            -1
        )

        # =========================================================
        # Transformer input
        # =========================================================

        # [B, 66, d_model]
        #
        #   0   : CLS
        #   1~64: board squares
        #   65  : game state
        #
        tokens = torch.cat(
            [
                cls_token,
                board_tokens,
                state_token
            ],
            dim=1
        )

        # =========================================================
        # Transformer
        # =========================================================

        tokens = self.transformer(
            tokens
        )

        tokens = self.norm(tokens)

        # CLS representation
        feature = tokens[:, 0]

        # =========================================================
        # Policy
        # =========================================================

        policy = self.policy_head(
            feature
        )

        # =========================================================
        # Value
        # =========================================================

        value = self.value_head(
            feature
        )

        return policy, value