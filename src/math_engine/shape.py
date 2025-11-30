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
        translation: (x, y, z) offset (z unused in 2D)
        rotation_euler: (pitch, roll, yaw) in degrees
        rotation_quat: (w, x, y, z) quaternion (auto-calculated from euler)
        dimension: Working dimension (2 or 3)
        visible: Whether to render this shape
        color: Display color (matplotlib color string)
    """
    equation_str: str
    equation: Eq
    name: str = "Shape"
    translation: Tuple[float, float, float] = (0.0, 0.0, 0.0)
    rotation_euler: Tuple[float, float, float] = (0.0, 0.0, 0.0)  # pitch, roll, yaw (degrees)
    rotation_quat: Tuple[float, float, float, float] = (1.0, 0.0, 0.0, 0.0)  # w, x, y, z
    dimension: int = 2
    visible: bool = True
    color: str = "blue"
    
    def set_rotation_euler(self, pitch: float = 0.0, roll: float = 0.0, yaw: float = 0.0):
        """
        Set rotation using Euler angles (degrees) and auto-calculate quaternion
        
        In 2D: only yaw matters (rotation around z-axis)
        In 3D: all three angles used
        """
        import math
        
        self.rotation_euler = (pitch, roll, yaw)
        
        # Convert to radians
        p = math.radians(pitch)
        r = math.radians(roll)
        y_rad = math.radians(yaw)
        
        # Convert Euler to quaternion (ZYX order)
        # For 2D, we only care about yaw (rotation around Z)
        if self.dimension == 2:
            # Simple 2D rotation quaternion
            w = math.cos(y_rad / 2)
            x = 0.0
            y = 0.0
            z = math.sin(y_rad / 2)
        else:
            # Full 3D quaternion from Euler angles
            cy = math.cos(y_rad * 0.5)
            sy = math.sin(y_rad * 0.5)
            cp = math.cos(p * 0.5)
            sp = math.sin(p * 0.5)
            cr = math.cos(r * 0.5)
            sr = math.sin(r * 0.5)
            
            w = cr * cp * cy + sr * sp * sy
            x = sr * cp * cy - cr * sp * sy
            y = cr * sp * cy + sr * cp * sy
            z = cr * cp * sy - sr * sp * cy
        
        self.rotation_quat = (w, x, y, z)
    
    def get_rotation_angle_2d(self) -> float:
        """Get the 2D rotation angle in degrees (just the yaw component)"""
        return self.rotation_euler[2]  # yaw
    
    def quat_to_euler(self) -> Tuple[float, float, float]:
        """
        Convert quaternion to Euler angles (degrees)
        Returns: (pitch, roll, yaw) in degrees
        """
        import math
        
        w, x, y, z = self.rotation_quat
        
        # Roll (x-axis rotation)
        sinr_cosp = 2 * (w * x + y * z)
        cosr_cosp = 1 - 2 * (x * x + y * y)
        roll = math.atan2(sinr_cosp, cosr_cosp)
        
        # Pitch (y-axis rotation)
        sinp = 2 * (w * y - z * x)
        if abs(sinp) >= 1:
            pitch = math.copysign(math.pi / 2, sinp)  # use 90 degrees if out of range
        else:
            pitch = math.asin(sinp)
        
        # Yaw (z-axis rotation)
        siny_cosp = 2 * (w * z + x * y)
        cosy_cosp = 1 - 2 * (y * y + z * z)
        yaw = math.atan2(siny_cosp, cosy_cosp)
        
        # Convert to degrees
        return (math.degrees(pitch), math.degrees(roll), math.degrees(yaw))
    
    def get_transformed_equation(self):
        """
        Get the BASE equation without transforms
        
        NOTE: For implicit functions, transforms CANNOT be applied by substitution.
        The rotation/translation must be applied during RENDERING by transforming
        the evaluation grid points, not the equation itself.
        
        This method now just returns the original equation.
        Transforms are handled in the plotter.
        """
        if isinstance(self.equation, Eq):
            expr = self.equation.lhs - self.equation.rhs
            return Eq(expr, 0)
        else:
            return self.equation
    
    def __repr__(self):
        vis = "✓" if self.visible else "✗"
        if self.dimension == 2:
            return f"Shape({self.name}, {vis}, pos={self.translation[:2]}, rot={self.get_rotation_angle_2d()}°)"
        else:
            return f"Shape({self.name}, {vis}, pos={self.translation}, euler={self.rotation_euler}°)"


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