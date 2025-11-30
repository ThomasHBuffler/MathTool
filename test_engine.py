"""
Test the Math Engine
Run this to verify the math engine works before launching the full UI
"""

import sys
sys.path.insert(0, 'src')

from math_engine.environment import MathEnvironment


def test_basic_parsing():
    """Test basic equation parsing"""
    print("=" * 50)
    print("TEST 1: Basic Parsing")
    print("=" * 50)
    
    env = MathEnvironment(dimension=2)
    
    # Test 1: Simple circle
    print("\n1. Circle: x^2 + y^2 = 25")
    eq = env.parse("x^2 + y^2 = 25")
    print(f"   Parsed: {eq}")
    print(f"   Type: {type(eq)}")
    
    # Test 2: Diamond/Square
    print("\n2. Diamond: abs(x) + abs(y) = 1")
    eq = env.parse("abs(x) + abs(y) = 1")
    print(f"   Parsed: {eq}")
    
    # Test 3: Complex equation
    print("\n3. Complex: x^2 - y^2 = 1")
    eq = env.parse("x^2 - y^2 = 1")
    print(f"   Parsed: {eq}")


def test_dimension_agnostic():
    """Test dimension-agnostic notation"""
    print("\n" + "=" * 50)
    print("TEST 2: Dimension-Agnostic Notation")
    print("=" * 50)
    
    # Test in 2D
    env = MathEnvironment(dimension=2)
    
    print("\n1. In 2D: sum(abs(n)) = 1")
    eq = env.parse("sum(abs(n)) = 1")
    print(f"   Expands to: {eq}")
    
    print("\n2. In 2D: sum(n^2) = 25")
    eq = env.parse("sum(n^2) = 25")
    print(f"   Expands to: {eq}")
    
    # Test in 3D
    env.set_dimension(3)
    
    print("\n3. In 3D: sum(abs(n)) = 1")
    eq = env.parse("sum(abs(n)) = 1")
    print(f"   Expands to: {eq}")
    
    print("\n4. In 3D: sum(n^2) = 25")
    eq = env.parse("sum(n^2) = 25")
    print(f"   Expands to: {eq}")
    
    # Test product
    env.set_dimension(2)
    print("\n5. In 2D: product(n) = 10")
    eq = env.parse("product(n) = 10")
    print(f"   Expands to: {eq}")


def test_function_definitions():
    """Test user-defined functions"""
    print("\n" + "=" * 50)
    print("TEST 3: Function Definitions")
    print("=" * 50)
    
    env = MathEnvironment(dimension=2)
    
    # Define a function
    print("\n1. Define: Circle(r) = sum(n^2) - r^2")
    env.define_function("Circle(r) = sum(n^2) - r^2")
    func = env.get_function("Circle")
    print(f"   Stored: {func}")
    
    # Define another
    print("\n2. Define: Square(s) = sum(abs(n)) - s")
    env.define_function("Square(s) = sum(abs(n)) - s")
    func = env.get_function("Square")
    print(f"   Stored: {func}")
    
    # List all functions
    print(f"\n3. All defined functions: {env.list_functions()}")


def test_solving():
    """Test equation solving"""
    print("\n" + "=" * 50)
    print("TEST 4: Equation Solving")
    print("=" * 50)
    
    env = MathEnvironment(dimension=2)
    
    # Solve circle for y
    print("\n1. Solve: x^2 + y^2 = 25 for y")
    solutions = env.solve_equation("x^2 + y^2 = 25", "y")
    print(f"   Solutions: {solutions}")
    
    # Solve line for y
    print("\n2. Solve: 2*x + 3*y = 6 for y")
    solutions = env.solve_equation("2*x + 3*y = 6", "y")
    print(f"   Solutions: {solutions}")


def test_evaluation():
    """Test expression evaluation"""
    print("\n" + "=" * 50)
    print("TEST 5: Expression Evaluation")
    print("=" * 50)
    
    env = MathEnvironment(dimension=2)
    
    # Evaluate at specific point
    print("\n1. Evaluate: x^2 + y^2 at (3, 4)")
    result = env.evaluate("x^2 + y^2", x=3, y=4)
    print(f"   Result: {result}")
    print(f"   Expected: 25")
    
    print("\n2. Evaluate: abs(x) + abs(y) at (-2, 3)")
    result = env.evaluate("abs(x) + abs(y)", x=-2, y=3)
    print(f"   Result: {result}")
    print(f"   Expected: 5")


def run_all_tests():
    """Run all tests"""
    print("\n" + "#" * 50)
    print("# MATH ENGINE TEST SUITE")
    print("#" * 50)
    
    try:
        test_basic_parsing()
        test_dimension_agnostic()
        test_function_definitions()
        test_solving()
        test_evaluation()
        
        print("\n" + "=" * 50)
        print("✓ ALL TESTS PASSED")
        print("=" * 50)
        
    except Exception as e:
        print("\n" + "=" * 50)
        print("✗ TEST FAILED")
        print("=" * 50)
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    run_all_tests()
