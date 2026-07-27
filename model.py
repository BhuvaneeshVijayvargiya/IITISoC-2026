import torch
import torch.nn as nn
from feature import FEATURE_DIM  


class AI(nn.Module):
    def __init__(self,in_dim=FEATURE_DIM, hidden=64):
        super().__init__()
        self.net = nn.Sequential(nn.Linear(in_dim, hidden),
            nn.ReLU(),nn.Linear(hidden, hidden),
            nn.ReLU(),nn.Linear(hidden, 1))

    def forward(self, x: torch.Tensor):
        return self.net(x).squeeze(-1)   

    def rank(self, candidates: torch.Tensor):
        with torch.no_grad():
            scores=self.forward(candidates)
        return int(torch.argmax(scores).item())