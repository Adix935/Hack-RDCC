# math_utils.py

def lerp(current, target, alpha):
    """
    Interpolare Liniară (Linear Interpolation).
    Calculează poziția intermediară pentru a oferi mișcare fluidă.
    'alpha' este factorul de netezire (0.0 - 1.0).
    """
    return current + (target - current) * alpha

def map_to_screen(raw_val, min_bound, max_bound, max_res):
    """
    Transformă o valoare brută de la cameră într-un pixel absolut pe ecran.
    Folosește marginile 'zonei active' pentru ca utilizatorul să nu fie
    nevoit să își rotească gâtul la extrem.
    """
    # 1. Limităm (clamp) valoarea brută pentru a nu ieși din zona activă
    if raw_val < min_bound:
        raw_val = min_bound
    elif raw_val > max_bound:
        raw_val = max_bound
        
    # 2. Transformăm valoarea într-un procentaj (0.0 - 1.0) strict în interiorul zonei active
    percentage = (raw_val - min_bound) / (max_bound - min_bound)
    
    # 3. Calculăm pixelul final
    return int(percentage * max_res)