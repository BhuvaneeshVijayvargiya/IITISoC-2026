#this is the command to run the file in terminal
#python run.py

from input import load
from solver import solve
from output import write_single

packages, ulds, K = load("sample_input.csv")
result = solve(packages, ulds, K)
write_single(result, out_dir="output")
pct_store.save(out_dir="output")

print("Done! Cost:", result["summary"]["total_cost"])
print("Feasible:", result["summary"]["is_feasible"])

from visualize import visualize_ulds
visualize_ulds(ulds)
