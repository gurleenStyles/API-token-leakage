import math
import collections

def shannon_entropy(data):
    """Calculates the Shannon entropy of a string."""
    if not data:
        return 0
    entropy = 0
    for x in set(data):
        p_x = float(data.count(x)) / len(data)
        entropy += - p_x * math.log(p_x, 2)
    return entropy

def investigate_entropy(string_val):
    """
    Determine if a string has high entropy.
    A base64 string usually has an alphabet of 64 chars, max entropy is 6.
    A hex string usually has an alphabet of 16 chars, max entropy is 4.
    """
    if len(string_val) < 16 or len(string_val) > 100:
        return False, 0
    
    entropy_val = shannon_entropy(string_val)
    
    # Simple heuristic
    is_high_entropy = False
    
    # Hex string
    if all(c in '0123456789abcdefABCDEF-' for c in string_val):
        if entropy_val > 3.0:
            is_high_entropy = True
            
    # Base64 string
    elif all(c in 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789+/=' for c in string_val):
        if entropy_val > 4.5:
            is_high_entropy = True
            
    return is_high_entropy, entropy_val
