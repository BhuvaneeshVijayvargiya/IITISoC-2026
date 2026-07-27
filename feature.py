FEATURE_NAMES = [
    "l_ratio", "w_ratio", "h_ratio",        # chosen orientation / ULD dims
    "x_ratio", "y_ratio", "z_ratio",         # position / ULD dims
    "volume_ratio",                          # package volume / ULD volume
    "dist_from_origin_ratio",                # (x+y+z) / (uld.length+width+height)
    "weight_ratio",                          # package.weight / uld.weight_limit
    "remaining_capacity_ratio",              # unused capacity / weight_limit
    "uld_utilization",                       # uld.utilization() before this placement
    "is_priority",                           # 1 if this package is Priority
    "uld_has_priority",                      # 1 if uld already holds a Priority pkg
    "priority_match",                        # 1 if both of the above are true
    "wall_contacts",                         # count of x==0, y==0, z==0 (0-3)
    "support_ratio",                         # supported_area / (l*w), 1.0 if z==0
    "delay_cost_ratio",                      # package.delay_cost / DELAY_COST_NORM
    "cog_deviation_ratio"
    ]
FEATURE_DIM = len(FEATURE_NAMES)

DELAY_COST_NORM = 1000.0  # placeholder — set this to your actual max/typical delay_cost
# feature_extraction.py — add this function

def compute_cog_deviation(node):
    uld = node.uld
    pkg = node.package

    # weighted sum of (position * weight) for everything already placed,
    # using each package's own center point, not its corner
    total_weight = pkg.weight
    weighted_x = (node.x + node.l / 2) * pkg.weight
    weighted_y = (node.y + node.w / 2) * pkg.weight

    for placed in uld.placed_packages:
        px, py, pz = placed.pos
        pl, pw, ph = placed.ori
        cx, cy = px + pl / 2, py + pw / 2
        weighted_x += cx * placed.weight
        weighted_y += cy * placed.weight
        total_weight += placed.weight

    if total_weight == 0:
        return 0.0

    cog_x = weighted_x / total_weight
    cog_y = weighted_y / total_weight

    floor_center_x = uld.length / 2
    floor_center_y = uld.width / 2

    deviation = ((cog_x - floor_center_x) ** 2 + (cog_y - floor_center_y) ** 2) ** 0.5
    max_deviation = ((uld.length / 2) ** 2 + (uld.width / 2) ** 2) ** 0.5  # corner-to-center distance

    return deviation / max_deviation if max_deviation > 0 else 0.0

def extracter(node, supported_area=None):
    
    pkg = node.package
    uld = node.uld

    volume_ratio = (node.l * node.w * node.h) / uld.volume()
    dist_ratio = (node.x + node.y + node.z) / (uld.length + uld.width + uld.height)
    weight_ratio = pkg.weight / uld.weight_limit
    remaining_capacity_ratio = (uld.weight_limit - uld.current_weight) / uld.weight_limit

    is_priority = 1.0 if pkg.package_type == "Priority" else 0.0
    uld_has_priority = 1.0 if uld.has_priority else 0.0
    priority_match = 1.0 if (is_priority and uld_has_priority) else 0.0

    wall_contacts = float((node.x == 0) + (node.y == 0) + (node.z == 0))
    cog_deviation_ratio = compute_cog_deviation(node)
    if node.z == 0:
        support_ratio = 1.0
    else:
        support_ratio = (supported_area / (node.l * node.w)) if supported_area else 0.0

    delay_cost_ratio = getattr(pkg, "delay_cost", 0.0) / DELAY_COST_NORM

    return [
        node.l / uld.length, node.w / uld.width, node.h / uld.height,
        node.x / uld.length, node.y / uld.width, node.z / uld.height,
        volume_ratio,
        dist_ratio,
        weight_ratio,
        remaining_capacity_ratio,
        uld.utilization(),
        is_priority,
        uld_has_priority,
        priority_match,
        wall_contacts,
        support_ratio,
        delay_cost_ratio,
        cog_deviation_ratio
    ]