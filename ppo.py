import torch
import torch.nn.functional as F
from torch.distributions import Categorical

class PPOTrainer:
    def __init__(
        self,
        model,
        lr=3e-4,
        gamma=0.99,
        gae_lambda=0.95,
        clip_eps=0.2,
        value_coef=0.5,
        entropy_coef=0.01,
        update_epochs=4,
    ):
        self.model = model

        self.optimizer = torch.optim.Adam(
            self.model.parameters(),
            lr=lr
        )

        self.gamma = gamma
        self.gae_lambda = gae_lambda
        self.clip_eps = clip_eps
        self.value_coef = value_coef
        self.entropy_coef = entropy_coef
        self.update_epochs = update_epochs

    def select_action(
        self,
        board,
        state,
        valid_mask
    ):
        policy, value = self.model(
            board.unsqueeze(0),
            state.unsqueeze(0)
        )

        valid_mask = valid_mask.unsqueeze(0)

        policy = policy.masked_fill(
            ~valid_mask,
            -torch.inf
        )

        dist = Categorical(logits=policy)

        action = dist.sample()

        log_prob = dist.log_prob(action)

        return (
            action.squeeze(0),
            log_prob.squeeze(0),
            value.squeeze(-1).squeeze(0)
        )

    def compute_gae(
        self,
        rewards,
        values,
        dones
    ):
        advantages = torch.zeros_like(rewards)
        last_advantage = 0.0

        for t in reversed(range(len(rewards))):

            if t == len(rewards) - 1:
                next_value = 0.0
            else:
                next_value = values[t + 1]

            next_non_terminal = 1.0 - dones[t]

            delta = (
                rewards[t]
                + self.gamma * next_value * next_non_terminal
                - values[t]
            )

            last_advantage = (
                delta
                + self.gamma
                * self.gae_lambda
                * next_non_terminal
                * last_advantage
            )

            advantages[t] = last_advantage

        returns = advantages + values

        return advantages, returns

    def update(
        self,
        boards,
        states,
        actions,
        log_probs_old,
        returns,
        advantages,
        valid_masks
    ):
        for _ in range(self.update_epochs):

            policy, values = self.model(
                boards,
                states
            )

            policy = policy.masked_fill(
                ~valid_masks,
                -torch.inf
            )

            dist = Categorical(
                logits=policy
            )

            log_probs_new = dist.log_prob(
                actions
            )

            entropy = dist.entropy().mean()

            ratios = torch.exp(
                log_probs_new - log_probs_old
            )

            surr1 = ratios * advantages

            surr2 = torch.clamp(
                ratios,
                1.0 - self.clip_eps,
                1.0 + self.clip_eps
            ) * advantages

            policy_loss = -torch.min(
                surr1,
                surr2
            ).mean()

            values = values.squeeze(-1)

            value_loss = F.mse_loss(
                values,
                returns
            )

            loss = (
                policy_loss
                + self.value_coef * value_loss
                - self.entropy_coef * entropy
            )

            self.optimizer.zero_grad()

            loss.backward()

            torch.nn.utils.clip_grad_norm_(
                self.model.parameters(),
                0.5
            )

            self.optimizer.step()