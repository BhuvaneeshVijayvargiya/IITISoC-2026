def calculate_overlap_area(x1, y1, w1, h1, x2, y2, w2, h2):
    overlap_x = max(0, min(x1 + w1, x2 + w2) - max(x1, x2))
    overlap_y = max(0, min(y1 + h1, y2 + h2) - max(y1, y2))
    return overlap_x * overlap_y


def is_item_stable(item, all_packed_items, support_threshold=0.5):
    x, y, z = [int(v) for v in item.position]
    w, h, d = [int(v) for v in item.get_dimension()]

    if z == 0:
        return True

    item_base_area = w * h
    total_supported_area = 0

    for other_item in all_packed_items:
        if other_item.name == item.name:
            continue

        ox, oy, oz = [int(v) for v in other_item.position]
        ow, oh, od = [int(v) for v in other_item.get_dimension()]

        if (oz + od) == z:
            supported_area = calculate_overlap_area(x, y, w, h, ox, oy, ow, oh)
            total_supported_area += supported_area

    if total_supported_area >= (item_base_area * support_threshold):
        return True

    return False


def validate_uld_stability(packed_uld, support_threshold=0.5):
    unstable_packages = []

    for item in packed_uld.items:
        if not is_item_stable(item, packed_uld.items, support_threshold):
            unstable_packages.append(item.name)

    is_stable = len(unstable_packages) == 0
    return is_stable, unstable_packages