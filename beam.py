import copy
from solver import generate_pct,score_node,place
def beam_search_label(package, uld, beam_width=5, depth=2):
    """
    Returns the index (into the CURRENT step's candidate list) of the
    candidate that leads to the best outcome after simulating `depth`
    steps ahead, keeping `beam_width` best partial paths alive at each level.
    """
    nodes = generate_pct(package, uld)
    if len(nodes) == 0:
        return None

    for node in nodes:
        node.score = score_node(node)

    # initial beam: one branch per candidate at step 1,
    # each branch = (cumulative_score, simulated_uld_state, first_choice_index)
    beam = []
    for i, node in enumerate(nodes):
        sim_uld = copy.deepcopy(uld)
        sim_node = _find_matching_node(sim_uld, node)  # see note below
        place(package, sim_node)
        beam.append((node.score, sim_uld, i))

    # keep only the top beam_width branches to expand further
    beam.sort(key=lambda b: b[0], reverse=True)
    beam = beam[:beam_width]

    # expand each surviving branch `depth - 1` more steps
    for _ in range(depth - 1):
        next_beam = []
        for cum_score, sim_uld, first_choice in beam:
            next_package = _pick_next_package()   # needs a "what comes next" source
            if next_package is None:
                next_beam.append((cum_score, sim_uld, first_choice))
                continue

            next_nodes = generate_pct(next_package, sim_uld)
            if len(next_nodes) == 0:
                next_beam.append((cum_score, sim_uld, first_choice))
                continue

            for nn in next_nodes:
                nn.score = score_node(nn)
            best_next = max(next_nodes, key=lambda n: n.score)

            new_uld = copy.deepcopy(sim_uld)
            new_node = _find_matching_node(new_uld, best_next)
            place(next_package, new_node)

            next_beam.append((cum_score + best_next.score, new_uld, first_choice))

        next_beam.sort(key=lambda b: b[0], reverse=True)
        beam = next_beam[:beam_width]

    # whichever surviving branch has the highest cumulative score wins —
    # its first_choice tells us which of the ORIGINAL candidates to pick
    best_branch = max(beam, key=lambda b: b[0])
    return best_branch[2]   # index into the original `nodes` list