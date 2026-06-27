from src.analytics.cagr import calculate_cagr

def test_cagr_normal():
    # 100 to 200 in 3 years
    val, flag = calculate_cagr(100, 200, 3)
    assert val == pytest.approx(25.99, 0.01)
    assert flag is None

def test_cagr_zero_base():
    val, flag = calculate_cagr(0, 100, 3)
    assert flag == "ZERO_BASE"

def test_cagr_decline_to_loss():
    val, flag = calculate_cagr(100, -50, 3)
    assert flag == "DECLINE_TO_LOSS"

def test_cagr_turnaround():
    val, flag = calculate_cagr(-50, 100, 3)
    assert flag == "TURNAROUND"

def test_cagr_both_negative():
    val, flag = calculate_cagr(-100, -50, 3)
    assert flag == "BOTH_NEGATIVE"

def test_cagr_insufficient_data():
    val, flag = calculate_cagr(100, 200, 0)
    assert flag == "INSUFFICIENT"