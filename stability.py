#part of solver, which checks for validity of solution arrangement.

def calculate_overlap_area(x1, y1, l1, w1, x2, y2, l2, w2):
    overlap_x = max(0, min(x1 + l1, x2 + l2) - max(x1, x2))
    overlap_y = max(0, min(y1 + w1, y2 + w2) - max(y1, y2))
    return overlap_x * overlap_y


def is_package_stable(package, all_placed_packages, support_threshold=0.5):
    x, y, z = package.pos
    l, w, h = package.ori

    if z == 0:
        return True

    package_base_area = l * w
    total_supported_area = 0

    for other_package in all_placed_packages:
        if other_package.id == package.id:
            continue

        px, py, pz = other_package.pos
        pl, pw, ph = other_package.ori

        if pz + ph == z:
            supported_area = calculate_overlap_area(x, y, l, w, px, py, pl, pw)
            total_supported_area += supported_area

    if total_supported_area >= (package_base_area * support_threshold):
        return True

    return False


def validate_uld_stability(uld, support_threshold=0.5):
    unstable_packages = []

    for package in uld.placed_packages:
        if not is_package_stable(package, uld.placed_packages, support_threshold):
            unstable_packages.append(package.id)

    is_stable = len(unstable_packages) == 0
    return is_stable, unstable_packages