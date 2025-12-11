def compute(a, b):
    """Example function with code smells."""
    x = 10  # unused variable
    if a > 0:
        if b > 0:
            return a + b
    return 0
