"""
Simple Test - Just verify basic parsing works
"""

import sys
sys.path.insert(0, 'src')

from math_engine.environment import MathEnvironment


def test_basic():
    """Test basic equation parsing"""
    print("Testing Math Engine")
    print("=" * 50)
    
    env = MathEnvironment()
    
    # Test 1: Circle
    print("\n1. Circle: x^2 + y^2 = 25")
    try:
        eq = env.parse("x^2 + y^2 = 25")
        print(f"   ✓ Parsed: {eq}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    # Test 2: Diamond
    print("\n2. Diamond: abs(x) + abs(y) = 1")
    try:
        eq = env.parse("abs(x) + abs(y) = 1")
        print(f"   ✓ Parsed: {eq}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    # Test 3: Solving
    print("\n3. Solve: x^2 + y^2 = 25 for y")
    try:
        solutions = env.solve_equation("x^2 + y^2 = 25", "y")
        print(f"   ✓ Solutions: {solutions}")
    except Exception as e:
        print(f"   ✗ Error: {e}")
        return False
    
    print("\n" + "=" * 50)
    print("✓ ALL TESTS PASSED")
    print("=" * 50)
    return True


if __name__ == "__main__":
    test_basic()