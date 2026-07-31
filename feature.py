FEATURE_NAMES = [
    "l_ratio", "w_ratio", "h_ratio",        
    "x_ratio", "y_ratio", "z_ratio",         
    "vol_ratio",                         
    "orig_ratio",                
    "weight_ratio",                          
    "capratio",              
    "uld_utilization",                       
    "is_priority",                           
    "uld_has_priority",                    
    "match",                        
    "wall_contacts",                        
    "support_ratio",                     
    "cog_deviation_ratio",
    "delaycost"
    ]
FEATURE_DIM = len(FEATURE_NAMES)

def compute_cog_deviation(node):
    uld=node.uld
    pkg= node.package 
    total_weight= pkg.weight
    weighted_x =(node.x + node.l/2)* pkg.weight
    weighted_y = (node.y + node.w/2)* pkg.weight
    weighted_z =(node.z + node.h/2)* pkg.weight

    for placed in uld.placed_packages:
        px, py, pz = placed.pos
        pl, pw, ph = placed.ori
        cx, cy,cz= px + pl / 2, py + pw/2,pz+ph/2
        weighted_x += cx * placed.weight
        weighted_y += cy * placed.weight
        weighted_z += cz * placed.weight
        total_weight += placed.weight

    if total_weight == 0:
        return 0.0

    cog_x = weighted_x/total_weight
    cog_y = weighted_y/total_weight
    cog_z = weighted_z/total_weight

    floor_center_x = uld.length/2
    floor_center_y = uld.width/2

    dev=((cog_x - floor_center_x) ** 2 + (cog_y - floor_center_y) ** 2 +(cog_z)**2) ** 0.5
    max_dev= ((uld.length / 2) ** 2 + (uld.width / 2) ** 2 + (uld.height)**2) ** 0.5 

    return dev/max_dev if max_dev> 0 else 0.0

def extracter(node, supported_area=None):
    
    pkg = node.package
    uld = node.uld

    volume_ratio=(node.l * node.w * node.h) / uld.volume()
    dist_ratio=(node.x + node.y + node.z) / (uld.length + uld.width + uld.height)
    weight_ratio=pkg.weight / uld.weight_limit
    remaining_capacity_ratio = (uld.weight_limit - uld.current_weight) / uld.weight_limit

    is_prior= 1.0 if pkg.package_type=="Priority" else 0.0
    uld_has_priority = 1.0 if uld.has_priority else 0.0
    priority_match = 1.0 if (is_prior and uld_has_priority) else 0.0

    contact=(node.x == 0) + (node.y == 0) + (node.z == 0)
    cog_dev = compute_cog_deviation(node)
    if node.z == 0:
        support_ratio = 1.0
    else:
        support_ratio = (supported_area/(node.l*node.w)) if supported_area else 0

    return [
        node.l/uld.length,node.w/uld.width,node.h/uld.height,
        node.x/uld.length,node.y/uld.width,node.z/uld.height,
        volume_ratio,
        dist_ratio,
        weight_ratio,
        remaining_capacity_ratio,
        uld.utilization(),
        is_prior,
        uld_has_priority,
        priority_match,
        contact,
        support_ratio,
        cog_dev,
        pkg.delay_cost if pkg.package_type=="Economy" else 0.0
    ]