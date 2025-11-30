"""
Dimension-Agnostic Expression Builder

Notation:
    sum(expr)       → x_expr + y_expr + z_expr + ...
    prod(expr)      → x_expr * y_expr * z_expr * ...
    max(expr)       → max(x_expr, y_expr, z_expr, ...)
    min(expr)       → min(x_expr, y_expr, z_expr, ...)
    
Examples:
    sum(Dim^2) = 25              → x^2 + y^2 + z^2 = 25 (sphere)
    sum(|Dim|) = 1               → |x| + |y| + |z| = 1 (diamond)
    sum(Dim^2)^0.5 = 5           → sqrt(x^2+y^2+z^2) = 5 (sphere via norm)
    max(|Dim|) = 1               → max(|x|,|y|,|z|) = 1 (cube)
    sum(Dim^2/a^2) = 1           → x^2/a^2 + y^2/a^2 + z^2/a^2 = 1 (ellipsoid)
    
Parameters:
    Use lowercase letters as parameters (a, b, r, p, etc.)
    Dim is reserved for dimension variable
"""

from sympy import symbols, sqrt, Abs, Max, Min, sympify, parse_expr
from sympy.abc import x, y, z, w, v, u, t, s, r, q
import re
from typing import Dict, List


class DimensionAgnosticBuilder:
    """
    Build dimension-agnostic expressions using function notation
    """
    
    def __init__(self):
        self.coord_symbols = [x, y, z, w, v, u, t, s, r, q]
        self.coord_names = ['x', 'y', 'z', 'w', 'v', 'u', 't', 's', 'r', 'q']
        
        # Identity library - common shapes
        self.identities = {
            # 2D & 3D Shapes
            "Circle/Sphere": {
                "expr": "sum(Dim^2) = r^2",
                "params": {"r": 5},
                "description": "Circle (2D) or Sphere (3D)"
            },
            "Diamond/Octahedron": {
                "expr": "sum(|Dim|) = r",
                "params": {"r": 1},
                "description": "Diamond (2D) or Octahedron (3D)"
            },
            "Square/Cube": {
                "expr": "max(|Dim|) = r",
                "params": {"r": 1},
                "description": "Square (2D) or Cube (3D)"
            },
            
            # Ellipsoids
            "Ellipse/Ellipsoid": {
                "expr": "sum(Dim^2/a^2) = 1",
                "params": {"a": 2},
                "description": "Ellipse (2D) or Ellipsoid (3D) - uniform scaling"
            },
            "Scaled Ellipsoid": {
                "expr": "Dim[0]^2/a^2 + Dim[1]^2/b^2 + Dim[2]^2/c^2 = 1",
                "params": {"a": 3, "b": 2, "c": 1},
                "description": "Ellipsoid with different axis scales (3D only)",
                "min_dim": 3
            },
            
            # Superquadrics
            "Superellipse/Superquadric": {
                "expr": "sum(|Dim|^p) = r^p",
                "params": {"r": 1, "p": 2.5},
                "description": "Rounded square (p>2) or pinched diamond (p<2)"
            },
            
            # Hyperboloids
            "Hyperbola/Hyperboloid (1-sheet)": {
                "expr": "Dim[0]^2 + Dim[1]^2 - Dim[2]^2 = 1",
                "params": {},
                "description": "Hyperboloid of one sheet (3D)",
                "min_dim": 3
            },
            "Hyperboloid (2-sheet)": {
                "expr": "Dim[0]^2 + Dim[1]^2 - Dim[2]^2 = -1",
                "params": {},
                "description": "Hyperboloid of two sheets (3D)",
                "min_dim": 3
            },
            
            # Planes & Hyperplanes
            "Line/Plane/Hyperplane": {
                "expr": "sum(Dim) = 0",
                "params": {},
                "description": "Line (2D), Plane (3D), or Hyperplane (nD)"
            },
            
            # Torus (3D only)
            "Torus": {
                "expr": "(sqrt(Dim[0]^2 + Dim[1]^2) - R)^2 + Dim[2]^2 = r^2",
                "params": {"R": 3, "r": 1},
                "description": "Torus (3D) - donut shape",
                "min_dim": 3
            },
            
            # Products
            "Hyperbolic Paraboloid": {
                "expr": "Dim[0]^2 - Dim[1]^2 = Dim[2]",
                "params": {},
                "description": "Saddle surface (3D)",
                "min_dim": 3
            },
            
            # Norm-based
            "Norm Ball": {
                "expr": "sum(Dim^2)^0.5 = r",
                "params": {"r": 5},
                "description": "Same as sphere, using explicit norm"
            },
            
            # Custom
            "Astroid": {
                "expr": "sum(|Dim|^(2/3)) = 1",
                "params": {},
                "description": "Star-like shape"
            },
        }
    
    def get_coords(self, n: int) -> List:
        """Get n coordinate symbols"""
        if n > len(self.coord_symbols):
            raise ValueError(f"Maximum {len(self.coord_symbols)} dimensions supported")
        return self.coord_symbols[:n]
    
    def expand(self, expr_str: str, dimension: int, params: Dict[str, float] = None) -> str:
        """
        Expand a dimension-agnostic expression
        
        Args:
            expr_str: Expression with dimension functions (e.g., "sum(Dim^2) = r^2")
            dimension: Target dimension (2, 3, 4, ...)
            params: Parameter values (e.g., {"r": 5, "a": 2})
        
        Returns:
            Expanded expression string
        
        Examples:
            expand("sum(Dim^2) = r^2", 3, {"r": 5})
                → "x**2 + y**2 + z**2 = 25"
            
            expand("sum(|Dim|) = 1", 2)
                → "Abs(x) + Abs(y) = 1"
            
            expand("max(|Dim|) = 1", 3)
                → "Max(Abs(x), Abs(y), Abs(z)) = 1"
        """
        if params is None:
            params = {}
        
        # Step 1: Replace indexed Dim (e.g., Dim[0], Dim[1])
        expr_str = self._replace_indexed_dims(expr_str, dimension)
        
        # Step 2: Expand dimension functions (sum, prod, max, min)
        expr_str = self._expand_functions(expr_str, dimension)
        
        # Step 3: Replace parameters with values
        expr_str = self._replace_params(expr_str, params)
        
        return expr_str
    
    def _replace_indexed_dims(self, expr_str: str, dimension: int) -> str:
        """Replace Dim[i] with actual coordinates"""
        def replacer(match):
            idx = int(match.group(1))
            if idx >= dimension:
                raise ValueError(f"Index Dim[{idx}] out of range for {dimension}D")
            return self.coord_names[idx]
        
        return re.sub(r'Dim\[(\d+)\]', replacer, expr_str)
    
    def _expand_functions(self, expr_str: str, dimension: int) -> str:
        """Expand sum(), prod(), max(), min() functions"""
        
        # Find all function calls recursively (innermost first)
        while True:
            # Match function(expression) where expression doesn't contain nested functions
            match = re.search(r'(sum|prod|max|min)\(([^()]+)\)', expr_str)
            if not match:
                break
            
            func_name = match.group(1)
            inner_expr = match.group(2)
            
            # Generate terms for each dimension
            coords = self.coord_names[:dimension]
            terms = []
            
            for coord in coords:
                # Replace 'Dim' with actual coordinate
                term = inner_expr.replace('Dim', coord)
                terms.append(term)
            
            # Combine terms based on function type
            if func_name == 'sum':
                replacement = ' + '.join(f'({t})' for t in terms)
            elif func_name == 'prod':
                replacement = ' * '.join(f'({t})' for t in terms)
            elif func_name == 'max':
                replacement = f'Max({", ".join(terms)})'
            elif func_name == 'min':
                replacement = f'Min({", ".join(terms)})'
            
            # Replace the function call with expanded version
            expr_str = expr_str[:match.start()] + f'({replacement})' + expr_str[match.end():]
        
        return expr_str
    
    def _replace_params(self, expr_str: str, params: Dict[str, float]) -> str:
        """Replace parameter placeholders with actual values"""
        for param_name, param_value in params.items():
            # Replace whole-word parameters only (not inside other words)
            pattern = r'\b' + param_name + r'\b'
            expr_str = re.sub(pattern, str(param_value), expr_str)
        
        return expr_str
    
    def get_identity(self, name: str) -> Dict:
        """Get an identity from the library"""
        return self.identities.get(name)
    
    def get_identity_names(self) -> List[str]:
        """Get all identity names"""
        return list(self.identities.keys())
    
    def expand_identity(self, name: str, dimension: int, params: Dict[str, float] = None) -> str:
        """
        Expand a named identity
        
        Args:
            name: Identity name (e.g., "Circle/Sphere")
            dimension: Target dimension
            params: Override default parameters
        
        Returns:
            Expanded expression string
        """
        identity = self.identities.get(name)
        if not identity:
            raise ValueError(f"Unknown identity: {name}")
        
        # Check dimension requirement
        min_dim = identity.get('min_dim', 1)
        if dimension < min_dim:
            raise ValueError(f"{name} requires at least {min_dim}D (got {dimension}D)")
        
        # Use provided params or defaults
        final_params = identity['params'].copy()
        if params:
            final_params.update(params)
        
        return self.expand(identity['expr'], dimension, final_params)


if __name__ == "__main__":
    builder = DimensionAgnosticBuilder()
    
    print("=" * 70)
    print("DIMENSION-AGNOSTIC EXPRESSION BUILDER")
    print("=" * 70)
    
    print("\n📖 IDENTITY LIBRARY:")
    print("-" * 70)
    for name, identity in builder.identities.items():
        print(f"\n{name}:")
        print(f"  Expression: {identity['expr']}")
        print(f"  Params: {identity['params']}")
        print(f"  Description: {identity['description']}")
        
        # Show 2D and 3D expansions
        min_dim = identity.get('min_dim', 1)
        if min_dim <= 2:
            try:
                expanded_2d = builder.expand_identity(name, 2)
                print(f"  2D: {expanded_2d}")
            except:
                pass
        
        if min_dim <= 3:
            try:
                expanded_3d = builder.expand_identity(name, 3)
                print(f"  3D: {expanded_3d}")
            except:
                pass
    
    print("\n" + "=" * 70)
    print("CUSTOM EXPRESSIONS:")
    print("-" * 70)
    
    tests = [
        ("sum(Dim^2) = 25", 2, {}),
        ("sum(Dim^2) = 25", 3, {}),
        ("sum(|Dim|) = 1", 3, {}),
        ("max(|Dim|) = 1", 3, {}),
        ("sum(Dim^2/a^2) = 1", 2, {"a": 3}),
        ("sum(|Dim|^p) = 1", 2, {"p": 2.5}),
    ]
    
    for expr, dim, params in tests:
        expanded = builder.expand(expr, dim, params)
        print(f"\n{dim}D: {expr}")
        if params:
            print(f"  Params: {params}")
        print(f"  → {expanded}")
    
    print("\n" + "=" * 70)