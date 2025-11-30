"""
Math Environment - Core symbolic math engine
Handles parsing, function definitions, and equation management
Fully compatible with Python 3.12
"""

from sympy import *
from sympy.parsing.sympy_parser import parse_expr
from sympy import Eq, Max, Min, Abs, sin, cos, tan
import re
from typing import Dict, List, Optional, Tuple


class MathEnvironment:
    """
    Core math engine that handles:
    - Dimension-agnostic notation (sum(n), product(n), etc.)
    - User-defined functions
    - Equation parsing and solving
    - Multiple coordinate systems
    """

    def __init__(self, dimension: int = 2):
        self.dimension = dimension
        self.user_functions = {}  # User-defined functions
        self.coord_symbols = self._make_coord_symbols(dimension)

    def _make_coord_symbols(self, dim: int) -> List[Symbol]:
        coord_names = ['x', 'y', 'z', 'w', 'u', 'v']
        if dim <= len(coord_names):
            return symbols(' '.join(coord_names[:dim]))
        else:
            return symbols(' '.join(f'n{i}' for i in range(dim)))

    def set_dimension(self, dimension: int):
        self.dimension = dimension
        self.coord_symbols = self._make_coord_symbols(dimension)

    def parse(self, expr_str: str):
        expr_str = expr_str.replace('^', '**')
        expr = self._replace_dimension_agnostic(expr_str)

        if isinstance(expr, str):
            local_dict = {str(s): s for s in self.coord_symbols}
            local_dict.update({'Abs': Abs, 'Max': Max, 'Min': Min, 'sin': sin, 'cos': cos, 'tan': tan})
            if '=' in expr:
                parts = expr.split('=')
                if len(parts) != 2:
                    raise ValueError(f"Invalid equation: {expr_str} (multiple = signs)")
                left = parse_expr(parts[0].strip(), evaluate=False, local_dict=local_dict)
                right = parse_expr(parts[1].strip(), evaluate=False, local_dict=local_dict)
                return Eq(left, right)
            else:
                return parse_expr(expr, evaluate=False, local_dict=local_dict)
        else:
            return expr

    def _replace_dimension_agnostic(self, expr_str: str):
        """
        Convert sum(n), product(n), max(n), min(n) directly into SymPy objects.
        Returns either a SymPy expression or string (if no replacement was needed).
        """
        coord_names = self.coord_symbols

        # sum(...)
        sum_pattern = re.compile(r'sum\((.*?)\)')
        while True:
            m = sum_pattern.search(expr_str)
            if not m:
                break
            inner = m.group(1)
            terms = [sympify(inner.replace('n', str(c))) for c in coord_names]
            expr = sum(terms)
            expr_str = expr_str[:m.start()] + f'@@SUM@@' + expr_str[m.end():]
            self._temp_replacements = getattr(self, '_temp_replacements', {})
            self._temp_replacements['@@SUM@@'] = expr

        # product(...)
        prod_pattern = re.compile(r'product\((.*?)\)')
        while True:
            m = prod_pattern.search(expr_str)
            if not m:
                break
            inner = m.group(1)
            terms = [sympify(inner.replace('n', str(c))) for c in coord_names]
            expr = 1
            for t in terms:
                expr *= t
            expr_str = expr_str[:m.start()] + f'@@PROD@@' + expr_str[m.end():]
            self._temp_replacements['@@PROD@@'] = expr

        # max(...)
        max_pattern = re.compile(r'max\((.*?)\)')
        while True:
            m = max_pattern.search(expr_str)
            if not m:
                break
            inner = m.group(1)
            terms = [sympify(inner.replace('n', str(c))) for c in coord_names]
            expr = Max(*terms)
            expr_str = expr_str[:m.start()] + f'@@MAX@@' + expr_str[m.end():]
            self._temp_replacements['@@MAX@@'] = expr

        # min(...)
        min_pattern = re.compile(r'min\((.*?)\)')
        while True:
            m = min_pattern.search(expr_str)
            if not m:
                break
            inner = m.group(1)
            terms = [sympify(inner.replace('n', str(c))) for c in coord_names]
            expr = Min(*terms)
            expr_str = expr_str[:m.start()] + f'@@MIN@@' + expr_str[m.end():]
            self._temp_replacements['@@MIN@@'] = expr

        # n[i] replacement
        for i, c in enumerate(coord_names):
            expr_str = expr_str.replace(f'n[{i}]', str(c))

        # Replace placeholders with SymPy objects
        if hasattr(self, '_temp_replacements') and self._temp_replacements:
            parts = re.split(r'(@@SUM@@|@@PROD@@|@@MAX@@|@@MIN@@)', expr_str)
            expr_final = None
            for p in parts:
                if p in self._temp_replacements:
                    e = self._temp_replacements[p]
                else:
                    if p.strip() == '':
                        continue
                    e = sympify(p)
                expr_final = e if expr_final is None else expr_final + 0 + e
            self._temp_replacements.clear()
            return expr_final

        return expr_str

    def define_function(self, definition: str):
        match = re.match(r'(\w+)\((.*?)\)\s*=\s*(.+)', definition)
        if not match:
            raise ValueError(f"Invalid function definition: {definition}")
        func_name = match.group(1)
        params = [p.strip() for p in match.group(2).split(',') if p.strip()]
        expr = self.parse(match.group(3))
        self.user_functions[func_name] = {
            'name': func_name,
            'params': params,
            'expr': expr,
            'definition': definition
        }
        return func_name

    def get_function(self, name: str) -> Optional[Dict]:
        return self.user_functions.get(name)

    def list_functions(self) -> List[str]:
        return list(self.user_functions.keys())

    def evaluate(self, expr_str: str, **values) -> float:
        expr = self.parse(expr_str)
        return float(expr.subs(values).evalf())

    def solve_equation(self, equation_str: str, solve_for: str):
        equation = self.parse(equation_str)
        variable = symbols(solve_for)
        expr = equation.lhs - equation.rhs if isinstance(equation, Equality) else equation
        return solve(expr, variable)

    def parse_multi_form(self, equation_str: str):
        parts = equation_str.split('=')
        if len(parts) < 2:
            raise ValueError("Not a multi-form equation (needs at least one =)")
        parsed_parts = [self.parse(p.strip()) for p in parts]
        return [Eq(parsed_parts[i], parsed_parts[i + 1]) for i in range(len(parsed_parts) - 1)]

    def solve_system(self, equation_str: str, *variables):
        if isinstance(equation_str, str):
            equations = self.parse_multi_form(equation_str) if equation_str.count('=') > 1 else [self.parse(equation_str)]
        else:
            equations = [self.parse(eq) for eq in equation_str]
        var_symbols = [symbols(v) for v in variables]
        return solve(equations, var_symbols, dict=True)

    def evaluate_multi_form(self, equation_str: str, **values):
        parts = equation_str.split('=')
        results = [float(self.parse(p.strip()).subs(values).evalf()) for p in parts]
        return results
