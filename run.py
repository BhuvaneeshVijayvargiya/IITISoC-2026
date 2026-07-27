#this is the command to run the file in terminal
#python run.py

from input import load
from solver import solve
from output import write_single
from pct_store import save_pct
from beam_store import save_beam_branches
import torch
from model import AI

packages, ulds, K = load(r"IITISoC-2026\inputs\sample_input (1).csv")
model = AI()
model.load_state_dict(torch.load("pretrained.pt"))
model.eval()

result, pct_store = solve(packages, ulds, K, model)
write_single(result, out_dir="output")
save_pct(pct_store, out_dir="output")

print("Done! Best cost:", best_branch["result"]["summary"]["total_cost"])
print("Feasible:", best_branch["result"]["summary"]["is_feasible"])

from visualize import visualize_ulds
visualize_ulds(best_branch["ulds"])
