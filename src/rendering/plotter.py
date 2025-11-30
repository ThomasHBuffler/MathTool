"""
Simple Plotter - Using numpy grid + contour
More reliable than sympy's plot_implicit
"""

import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from sympy import lambdify, Eq
from sympy.abc import x, y
import numpy as np


class QtPlotWidget(FigureCanvasQTAgg):
    """
    Qt widget for plotting implicit equations
    Uses numpy grid evaluation + contour plotting
    """
    
    def __init__(self, parent=None, bounds=(-10, 10, -10, 10)):
        self.figure = Figure(figsize=(8, 8))
        super().__init__(self.figure)
        self.setParent(parent)
        
        self.ax = self.figure.add_subplot(111)
        self.bounds = bounds
        
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
        Plot multiple shapes
        
        Args:
            shapes: List of Shape objects
            clear: Whether to clear previous plots
            resolution: Number of points in each direction
        """
        print(f"\n[PLOTTER] Plotting {len(shapes)} shapes")
        
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
                print(f"[PLOTTER]   Translation: {shape.translation}")
                print(f"[PLOTTER]   Rotation: {shape.rotation}°")
                print(f"[PLOTTER]   Color: {shape.color}")
                
                # Get transformed equation
                transformed_eq = shape.get_transformed_equation()
                print(f"[PLOTTER]   Transformed: {transformed_eq}")
                
                # Convert to expression
                if isinstance(transformed_eq, Eq):
                    expr = transformed_eq.lhs - transformed_eq.rhs
                else:
                    expr = transformed_eq
                
                # Convert to numpy function
                f = lambdify([x, y], expr, modules=['numpy'])
                
                # Evaluate on grid
                Z = f(X, Y)
                
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
        self.ax.set_xlabel('x', fontsize=12)
        self.ax.set_ylabel('y', fontsize=12)
        self.ax.grid(True, alpha=0.3)
        self.ax.set_aspect('equal')
        self.ax.axhline(y=0, color='k', linewidth=0.5)
        self.ax.axvline(x=0, color='k', linewidth=0.5)
        x_min, x_max, y_min, y_max = self.bounds
        self.ax.set_xlim(x_min, x_max)
        self.ax.set_ylim(y_min, y_max)
        self.draw()