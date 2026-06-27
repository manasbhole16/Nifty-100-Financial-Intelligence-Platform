import math

def calculate_cagr(start_value, end_value, n):
    """
    Calculates CAGR: ((end/start)^(1/n) - 1) * 100.
    Returns (cagr_value, flag).
    """
    if n <= 0:
        return None, "INSUFFICIENT"
    
    # 1. Zero base case
    if start_value == 0:
        return None, "ZERO_BASE"
    
    # 2. Positive to Positive: Standard calculation
    if start_value > 0 and end_value > 0:
        cagr = ((end_value / start_value) ** (1 / n) - 1) * 100
        return cagr, None
        
    # 3. Positive to Negative: Decline to Loss
    if start_value > 0 and end_value < 0:
        return None, "DECLINE_TO_LOSS"
        
    # 4. Negative to Positive: Turnaround
    if start_value < 0 and end_value > 0:
        return None, "TURNAROUND"
        
    # 5. Negative to Negative: Both Negative
    if start_value < 0 and end_value < 0:
        return None, "BOTH_NEGATIVE"

    return None, "INSUFFICIENT"

# Usage for windows (3, 5, 10 years):
# revenue_cagr_3yr, revenue_cagr_3yr_flag = calculate_cagr(rev_t_minus_3, rev_current, 3)