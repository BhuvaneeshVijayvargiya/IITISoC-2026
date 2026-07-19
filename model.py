FEATURE_NAMES = [
    #to be decided
]
FEATURE_DIM = len(FEATURE_NAMES)
import torch
import torch.nn as nn
class AI(nn.Module):
 
    def __init__(self, in_dim: int = FEATURE_DIM, hidden: int = 64):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(in_dim, hidden),
            nn.ReLU(),
            nn.Linear(hidden, hidden),
            nn.ReLU(),
            nn.Linear(hidden, 1),
        )
 
    def forward(self, x: torch.Tensor):
        return self.net(x)
 
    def rank(self, candidates: List[placs]):
        x = torch.tensor([c.features for c in candidates], dtype=torch.float32)
        with torch.no_grad():
            scores = self.forward(x)
        return int(torch.argmax(scores).item())
 
 