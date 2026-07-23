#this is the command to run the file in terminal
#python run.py

from input import load
from solver import solve_beam
from output import write_single
from pct_store import save_pct
from beam_store import save_beam_branches

packages, ulds, K = load("sample_input.csv")
final_results, best_branch = solve_beam(packages, ulds, K, beam_width=3)

write_single(best_branch["result"], out_dir="output")
save_pct(best_branch["pct_log"], out_dir="output")
save_beam_branches(final_results, best_branch, out_dir="output")

print("Done! Best cost:", best_branch["result"]["summary"]["total_cost"])
print("Feasible:", best_branch["result"]["summary"]["is_feasible"])

from visualize import visualize_ulds
visualize_ulds(best_branch["ulds"])
