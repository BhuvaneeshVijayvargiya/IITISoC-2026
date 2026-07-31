#this is the command to run the file in terminal
#python run.py

import torch
from input import load
from model import AI
from solver import solve_beam
from output import write_single
from pct_store import save_pct
from beam_store import save_beam_branches

# change this to change beam width
beam_width = 3
packages, ulds, K = load("inputs/sample_input (1).csv") #for mac
# packages, ulds, K = load(r"inputs\sample_input (1).csv") #for windows

# load the trained model to help rank candidates 
model = AI()
model.load_state_dict(torch.load("pretrained.pt", map_location="cpu"))
model.eval()

final_results, best_branch = solve_beam(packages, ulds, K, model, beam_width=beam_width)


write_single(best_branch["result"], out_dir="output")
save_pct(best_branch["pct_log"], out_dir="output")
save_beam_branches(final_results, best_branch["result"], out_dir="output")

print(f"Done! Ran beam search with beam_width={beam_width}")
print("Best cost:", best_branch["result"]["summary"]["total_cost"])
print("Feasible:", best_branch["result"]["summary"]["is_feasible"])
