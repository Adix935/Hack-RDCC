def lerp(current, target, alpha):
    """Interpolare liniară pentru a elimina tremuratul camerei."""
    return current + (target - current) * alpha

def map_to_screen(raw_val, min_bound, max_bound, max_res):
    """Transformă X/Y-ul de pe cameră în pixel absolut pe monitor."""
    if raw_val < min_bound: raw_val = min_bound
    elif raw_val > max_bound: raw_val = max_bound
        
    percentage = (raw_val - min_bound) / (max_bound - min_bound)
    return int(percentage * max_res)