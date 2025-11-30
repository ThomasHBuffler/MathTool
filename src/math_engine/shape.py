"""
Shape - Represents a mathematical shape with transforms
"""

from sympy import Eq
from dataclasses import dataclass
from typing import Tuple, Optional


@dataclass
class Shape:
    """
    A mathematical shape with transform properties
    
    Attributes:
        equation_str: The equation as string (e.g., "x^2 + y^2 = 25")
        equation: Parsed SymPy equation
        name: Display name (e.g., "Circle 1")
        translation: (x, y) offset
        rotation: Rotation angle in degrees
        visible: Whether to render this shape
        color: Display color (matplotlib color string)
    """
    equation_str: str
    equation: Eq
    name: str = "Shape"
    translation: Tuple[float, float] = (0.0, 0.0)
    rotation: float = 0.0  # Degrees
    visible: bool = True
    color: str = "blue"
    
    def get_transformed_equation(self):
        """
        Get the equation with translation and rotation applied
        
        For translation (tx, ty) and rotation (θ degrees), we:
        1. Translate: x → (x - tx), y → (y - ty)
        2. Rotate: Apply inverse rotation matrix
        
        Rotation matrix (inverse):
        x' = x*cos(θ) + y*sin(θ)
        y' = -x*sin(θ) + y*cos(θ)
        
        Example:
            Original: x^2 + y^2 = 25
            Translation: (3, 2), Rotation: 45°
            Result: Rotated and translated circle
        """
        from sympy import symbols, cos, sin, pi
        from sympy.abc import x, y
        
        tx, ty = self.translation
        theta_deg = self.rotation
        
        # Get the equation expression
        if isinstance(self.equation, Eq):
            expr = self.equation.lhs - self.equation.rhs
        else:
            expr = self.equation
        
        # Apply translation
        if tx != 0 or ty != 0:
            expr = expr.subs({x: x - tx, y: y - ty})
        
        # Apply rotation (if not zero)
        if theta_deg != 0:
            # Convert degrees to radians
            theta_rad = theta_deg * pi / 180
            
            # Inverse rotation: rotate coordinates by -theta
            # x' = x*cos(-θ) - y*sin(-θ) = x*cos(θ) + y*sin(θ)
            # y' = x*sin(-θ) + y*cos(-θ) = -x*sin(θ) + y*cos(θ)
            x_rot = x * cos(theta_rad) + y * sin(theta_rad)
            y_rot = -x * sin(theta_rad) + y * cos(theta_rad)
            
            expr = expr.subs({x: x_rot, y: y_rot})
        
        return Eq(expr, 0)
    
    def __repr__(self):
        vis = "✓" if self.visible else "✗"
        return f"Shape({self.name}, {vis}, pos={self.translation}, rot={self.rotation}°)"


class ShapeManager:
    """
    Manages a collection of shapes
    """
    
    def __init__(self):
        self.shapes = []
        self._shape_counter = 0
    
    def add_shape(self, equation_str: str, equation: Eq, name: Optional[str] = None) -> Shape:
        """
        Add a new shape to the collection
        
        Args:
            equation_str: Equation as string
            equation: Parsed SymPy equation
            name: Optional custom name
        
        Returns:
            The created Shape object
        """
        if name is None:
            self._shape_counter += 1
            name = f"Shape {self._shape_counter}"
        
        # Assign color (cycle through colors)
        colors = ['blue', 'red', 'green', 'purple', 'orange', 'cyan', 'magenta']
        color = colors[len(self.shapes) % len(colors)]
        
        shape = Shape(
            equation_str=equation_str,
            equation=equation,
            name=name,
            color=color
        )
        
        self.shapes.append(shape)
        return shape
    
    def remove_shape(self, shape: Shape):
        """Remove a shape from the collection"""
        if shape in self.shapes:
            self.shapes.remove(shape)
    
    def get_visible_shapes(self):
        """Get all visible shapes"""
        return [s for s in self.shapes if s.visible]
    
    def clear_all(self):
        """Remove all shapes"""
        self.shapes.clear()
        self._shape_counter = 0
    
    def __len__(self):
        return len(self.shapes)
    
    def __iter__(self):
        return iter(self.shapes)