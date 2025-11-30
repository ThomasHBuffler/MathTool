"""
Simple Plotter - Using numpy grid + contour
More reliable than sympy's plot_implicit
"""

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from mpl_toolkits.mplot3d import Axes3D
from sympy import lambdify, Eq
from sympy.abc import x, y, z
import numpy as np


class QtPlotWidget(FigureCanvasQTAgg):
    """
    Qt widget for plotting implicit equations
    Uses numpy grid evaluation + contour plotting
    """
    
    def __init__(self, parent=None, bounds=(-10, 10, -10, 10), mode='2d'):
        self.figure = Figure(figsize=(8, 8))
        super().__init__(self.figure)
        self.setParent(parent)
        
        self.bounds = bounds
        self.mode = mode  # '2d' or '3d'
        
        if mode == '3d':
            self.ax = self.figure.add_subplot(111, projection='3d')
            self.ax.set_xlabel('x', fontsize=12)
            self.ax.set_ylabel('y', fontsize=12)
            self.ax.set_zlabel('z', fontsize=12)
            self.ax.set_xlim(bounds[0], bounds[1])
            self.ax.set_ylim(bounds[2], bounds[3])
            self.ax.set_zlim(bounds[2], bounds[3])
        else:
            self.ax = self.figure.add_subplot(111)
            # Configure initial appearance
            self.ax.set_xlabel('x', fontsize=12)
            self.ax.set_ylabel('y', fontsize=12)
            self.ax.grid(True, alpha=0.3)
            self.ax.set_aspect('equal')
            self.ax.set_xlim(bounds[0], bounds[1])
            self.ax.set_ylim(bounds[2], bounds[3])
            self.ax.axhline(y=0, color='k', linewidth=0.5)
            self.ax.axvline(x=0, color='k', linewidth=0.5)
    
    def plot_shapes(self, shapes, clear=True, resolution=500):
        """
        Plot multiple shapes (2D or 3D based on mode)
        
        Args:
            shapes: List of Shape objects
            clear: Whether to clear previous plots
            resolution: Number of points in each direction
        """
        print(f"\n[PLOTTER] Plotting {len(shapes)} shapes in {self.mode.upper()} mode")
        
        if self.mode == '2d':
            self._plot_shapes_2d(shapes, clear, resolution)
        else:
            self._plot_shapes_3d(shapes, clear, resolution)
    
    def _plot_shapes_2d(self, shapes, clear, resolution):
        """Plot 2D implicit curves"""
        if clear:
            self.ax.clear()
            self.ax.set_xlabel('x', fontsize=12)
            self.ax.set_ylabel('y', fontsize=12)
            self.ax.grid(True, alpha=0.3)
            self.ax.set_aspect('equal')
            self.ax.axhline(y=0, color='k', linewidth=0.5)
            self.ax.axvline(x=0, color='k', linewidth=0.5)
        
        x_min, x_max, y_min, y_max = self.bounds
        
        # Create grid once (shared by all shapes)
        x_vals = np.linspace(x_min, x_max, resolution)
        y_vals = np.linspace(y_min, y_max, resolution)
        X, Y = np.meshgrid(x_vals, y_vals)
        
        for shape in shapes:
            if not shape.visible:
                print(f"[PLOTTER] Skipping hidden shape: {shape.name}")
                continue
            
            try:
                print(f"[PLOTTER] Plotting {shape.name}: {shape.equation_str}")
                print(f"[PLOTTER]   Translation: {shape.translation[:2]}")
                print(f"[PLOTTER]   Rotation: {shape.get_rotation_angle_2d()}° (quat: {shape.rotation_quat})")
                print(f"[PLOTTER]   Color: {shape.color}")
                
                # Get the BASE equation (no transforms)
                base_eq = shape.get_transformed_equation()
                
                # Convert to expression
                if isinstance(base_eq, Eq):
                    expr = base_eq.lhs - base_eq.rhs
                else:
                    expr = base_eq
                
                # Convert to numpy function
                f = lambdify([x, y], expr, modules=['numpy'])
                
                # Apply INVERSE transforms to the grid points
                tx, ty, _ = shape.translation
                X_transformed = X - tx
                Y_transformed = Y - ty
                
                # Rotation (inverse = rotate by -theta)
                theta_deg = shape.get_rotation_angle_2d()
                if theta_deg != 0:
                    import math
                    theta_rad = math.radians(-theta_deg)
                    cos_theta = np.cos(theta_rad)
                    sin_theta = np.sin(theta_rad)
                    
                    X_rotated = X_transformed * cos_theta - Y_transformed * sin_theta
                    Y_rotated = X_transformed * sin_theta + Y_transformed * cos_theta
                    
                    X_transformed = X_rotated
                    Y_transformed = Y_rotated
                
                # Evaluate
                Z = f(X_transformed, Y_transformed)
                
                # Plot contour
                self.ax.contour(X, Y, Z, levels=[0], 
                              colors=shape.color, 
                              linewidths=2,
                              label=shape.name)
                
                print(f"[PLOTTER] ✓ {shape.name} plotted")
            
            except Exception as e:
                print(f"[PLOTTER] ✗ Error plotting {shape.name}: {e}")
                import traceback
                traceback.print_exc()
        
        # Set limits
        self.ax.set_xlim(x_min, x_max)
        self.ax.set_ylim(y_min, y_max)
        
        # Add legend if multiple shapes
        if len(shapes) > 1:
            self.ax.legend()
        
        self.draw()
        print(f"[PLOTTER] ✓ All shapes rendered")
    
    def _plot_shapes_3d(self, shapes, clear, resolution=30):
        """Plot 3D implicit surfaces using isosurfaces (OPTIMIZED)"""
        if clear:
            self.ax.clear()
            self.ax.set_xlabel('x', fontsize=12)
            self.ax.set_ylabel('y', fontsize=12)
            self.ax.set_zlabel('z', fontsize=12)
        
        x_min, x_max, y_min, y_max = self.bounds
        z_min, z_max = y_min, y_max
        
        # Create 3D grid ONCE (shared by all shapes)
        print(f"[PLOTTER] Creating {resolution}x{resolution}x{resolution} 3D grid...")
        x_vals = np.linspace(x_min, x_max, resolution)
        y_vals = np.linspace(y_min, y_max, resolution)
        z_vals = np.linspace(z_min, z_max, resolution)
        X, Y, Z = np.meshgrid(x_vals, y_vals, z_vals, indexing='ij')
        
        for shape in shapes:
            if not shape.visible:
                print(f"[PLOTTER] Skipping hidden shape: {shape.name}")
                continue
            
            try:
                print(f"[PLOTTER] Plotting 3D {shape.name}: {shape.equation_str}")
                
                # Get base equation
                base_eq = shape.get_transformed_equation()
                
                if isinstance(base_eq, Eq):
                    expr = base_eq.lhs - base_eq.rhs
                else:
                    expr = base_eq
                
                # Convert to numpy function (3D) - CACHED
                from sympy.abc import z as z_sym
                print(f"[PLOTTER] Compiling function...")
                f = lambdify([x, y, z_sym], expr, modules=['numpy'])
                
                # Apply transforms
                tx, ty, tz = shape.translation
                X_t = X - tx
                Y_t = Y - ty
                Z_t = Z - tz
                
                # Evaluate on grid
                print(f"[PLOTTER] Evaluating function on grid...")
                values = f(X_t, Y_t, Z_t)
                
                # Extract isosurface using marching cubes
                try:
                    from skimage import measure
                    print(f"[PLOTTER] Running marching cubes...")
                    
                    verts, faces, _, _ = measure.marching_cubes(
                        values, 
                        level=0,
                        spacing=(
                            (x_max - x_min) / resolution,
                            (y_max - y_min) / resolution,
                            (z_max - z_min) / resolution
                        ),
                        allow_degenerate=False
                    )
                    
                    # Offset vertices
                    verts[:, 0] += x_min
                    verts[:, 1] += y_min
                    verts[:, 2] += z_min
                    
                    # Plot surface with reduced detail for performance
                    print(f"[PLOTTER] Rendering surface ({len(verts)} vertices)...")
                    self.ax.plot_trisurf(
                        verts[:, 0], verts[:, 1], faces, verts[:, 2],
                        color=shape.color, 
                        alpha=0.8,
                        linewidth=0.2,
                        antialiased=True,
                        shade=True
                    )
                    
                    print(f"[PLOTTER] ✓ {shape.name} plotted (3D isosurface)")
                
                except ImportError:
                    print(f"[PLOTTER] ✗ scikit-image not installed - install with: pip install scikit-image")
            
            except Exception as e:
                print(f"[PLOTTER] ✗ Error plotting 3D {shape.name}: {e}")
                import traceback
                traceback.print_exc()
        
        # Set limits
        self.ax.set_xlim(x_min, x_max)
        self.ax.set_ylim(y_min, y_max)
        self.ax.set_zlim(z_min, z_max)
        
        self.draw()
        print(f"[PLOTTER] ✓ All 3D shapes rendered")
    
    def plot_equation(self, equation, clear=True, resolution=500):
        """
        Plot a single implicit equation (backward compatibility)
        
        Args:
            equation: SymPy Eq object
            clear: Whether to clear previous plots
            resolution: Number of points in each direction
        """
        print(f"\n[PLOTTER] Single equation plot (legacy mode)")
        print(f"[PLOTTER] Equation: {equation}")
        
        if clear:
            self.ax.clear()
            self.ax.set_xlabel('x', fontsize=12)
            self.ax.set_ylabel('y', fontsize=12)
            self.ax.grid(True, alpha=0.3)
            self.ax.set_aspect('equal')
            self.ax.axhline(y=0, color='k', linewidth=0.5)
            self.ax.axvline(x=0, color='k', linewidth=0.5)
        
        x_min, x_max, y_min, y_max = self.bounds
        
        try:
            # Convert equation to expression
            if isinstance(equation, Eq):
                expr = equation.lhs - equation.rhs
            else:
                expr = equation
            
            # Convert to numpy function
            f = lambdify([x, y], expr, modules=['numpy'])
            
            # Create grid
            x_vals = np.linspace(x_min, x_max, resolution)
            y_vals = np.linspace(y_min, y_max, resolution)
            X, Y = np.meshgrid(x_vals, y_vals)
            
            # Evaluate
            Z = f(X, Y)
            
            # Plot contour
            self.ax.contour(X, Y, Z, levels=[0], colors='blue', linewidths=2)
            
            # Set limits
            self.ax.set_xlim(x_min, x_max)
            self.ax.set_ylim(y_min, y_max)
            
            self.draw()
            print(f"[PLOTTER] ✓ Plot complete")
        
        except Exception as e:
            print(f"[PLOTTER] ✗ ERROR: {e}")
            import traceback
            traceback.print_exc()
            
            # Show error
            self.ax.text(0, 0, f"Error:\n{str(e)}", 
                        ha='center', va='center',
                        fontsize=10,
                        bbox=dict(boxstyle='round', facecolor='red', alpha=0.7))
            self.draw()
    
    def set_bounds(self, x_min, x_max, y_min, y_max):
        """Update plot bounds"""
        self.bounds = (x_min, x_max, y_min, y_max)
        self.ax.set_xlim(x_min, x_max)
        self.ax.set_ylim(y_min, y_max)
        self.draw()
    
    def clear_plot(self):
        """Clear the plot"""
        self.ax.clear()
        
        if self.mode == '2d':
            self.ax.set_xlabel('x', fontsize=12)
            self.ax.set_ylabel('y', fontsize=12)
            self.ax.grid(True, alpha=0.3)
            self.ax.set_aspect('equal')
            self.ax.axhline(y=0, color='k', linewidth=0.5)
            self.ax.axvline(x=0, color='k', linewidth=0.5)
            x_min, x_max, y_min, y_max = self.bounds
            self.ax.set_xlim(x_min, x_max)
            self.ax.set_ylim(y_min, y_max)
        else:
            self.ax.set_xlabel('x', fontsize=12)
            self.ax.set_ylabel('y', fontsize=12)
            self.ax.set_zlabel('z', fontsize=12)
            x_min, x_max, y_min, y_max = self.bounds
            self.ax.set_xlim(x_min, x_max)
            self.ax.set_ylim(y_min, y_max)
            self.ax.set_zlim(y_min, y_max)
        
        self.draw()