import torch
import torch.nn as nn
import torch.optim as optim
import torch.nn.functional as F
import os
import random

class PolicyNetwork(nn.Module):
    # def __init__(self, num_users=100, embedding_dim=8, state_dim=3, hidden_dim=32, num_actions=7):
    def __init__(self, num_users=100, embedding_dim=8, state_dim=3, hidden_dim=32, num_actions=5):
        super().__init__()

        # User embedding
        self.user_embedding = nn.Embedding(num_users, embedding_dim)

        # State encoder
        self.fc1 = nn.Linear(state_dim + embedding_dim, hidden_dim)
        self.fc2 = nn.Linear(hidden_dim, hidden_dim)

        # Policy output
        self.policy_head = nn.Linear(hidden_dim, num_actions)

    def forward(self, user_id, state):

        user_embed = self.user_embedding(user_id)

        x = torch.cat([state, user_embed], dim=-1)

        x = F.relu(self.fc1(x))
        x = F.relu(self.fc2(x))

        logits = self.policy_head(x)

        return logits

class DeepPolicyBandit:

    # def __init__(self):

    #     self.actions = [
    #         "breathing",
    #         "joke",
    #         "brain_teaser",
    #         "motivation"
    #     ]

    #     self.model = PolicyNetwork()
    #     self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)

    #     self.last_log_prob = None
    #     self.last_user = None
    #     self.last_state = None
    def __init__(self):

        self.actions = [
            "breathing",
            "joke",
            "brain_teaser",
            "motivation",
            "sliding_puzzle",
            # "memory_sequence",
            # "mini_sudoko"
        ]

        self.model = PolicyNetwork()
        self.optimizer = optim.Adam(self.model.parameters(), lr=0.001)

        self.model_path = "policy_model.pth"

        print("INIT WORKING DIRECTORY:", os.getcwd())
        print("Looking for model at:", os.path.abspath(self.model_path))

        # 🔥 Load existing model if available
        if os.path.exists(self.model_path):
            self.model.load_state_dict(torch.load(self.model_path))
            print("Loaded existing policy model")

        self.last_log_prob = None
        self.last_user = None
        self.last_state = None

    def encode_emotion(self, emotion):
        mapping = {
            "neutral": 0,
            "frustrated": 1,
            "distracted": 2,
            "stressed": 3
        }
        return mapping.get(emotion, 0)

    def select_action(self, focus_score, digital_score, emotion, user_id):

        self.model.train()

        user_tensor = torch.tensor([user_id], dtype=torch.long)

        emotion_val = self.encode_emotion(emotion) / 3.0

        state = torch.tensor([[focus_score, digital_score, emotion_val]], dtype=torch.float32)

        logits = self.model(user_tensor, state)

        probs = F.softmax(logits, dim=-1)

        dist = torch.distributions.Categorical(probs)
        action_idx = dist.sample()

        self.last_log_prob = dist.log_prob(action_idx)
        self.last_user = user_tensor
        self.last_state = state

        return self.actions[action_idx.item()]

    def update(self, reward):

        print("UPDATE FUNCTION CALLED")
        print("Saving model to:", os.path.abspath(self.model_path))

        if self.last_log_prob is None:
            return

        loss = -self.last_log_prob * reward

        self.optimizer.zero_grad()
        loss.backward()
        self.optimizer.step()
        torch.save(self.model.state_dict(), self.model_path)

        print("Policy updated with reward:", reward)

        self.last_log_prob = None  