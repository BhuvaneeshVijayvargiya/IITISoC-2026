import json
import os

#we are storing the best 3 branches based on scoring
def save_beam_branches(final_results, best_branch, out_dir="output"):
    os.makedirs(out_dir, exist_ok=True)

    branch_number = 1
    for branch in final_results:
        file_name = "beam_branch_" + str(branch_number) + ".json"
        path = os.path.join(out_dir, file_name)
        with open(path, "w") as f:
            json.dump(branch["result"], f, indent=2)
        branch_number += 1

    best_branch_path = os.path.join(out_dir, "best_branch.json")
    with open(best_branch_path, "w") as f:
        json.dump(best_branch, f)


#this is to load the best branch for further use
def load_best_branch(path="output/best_branch.json"):
    with open(path, "r") as f:
        best_branch = json.load(f)
    return best_branch
