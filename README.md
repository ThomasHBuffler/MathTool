# Math Tool - Implicit Function Plotter

A dimension-agnostic mathematical visualization tool built with Python, SymPy, and PyQt6.

## Features

- **Dimension-Agnostic Notation**: Define shapes that work in any dimension
  - `sum(abs(n)) = 1` → Square in 2D, Octahedron in 3D
  - `sum(n^2) = 25` → Circle in 2D, Sphere in 3D
  
- **Implicit Function Plotting**: Plot any equation of the form `F(x,y) = c`
  - Circles, ellipses, hyperbolas
  - Custom implicit surfaces
  
- **User-Defined Functions**: Create reusable function definitions
  - `Circle(r) = sum(n^2) - r^2`
  - `Square(s) = sum(abs(n)) - s`

## Installation

### 1. Prerequisites
- Python 3.11+ installed
- Virtual environment activated

### 2. Install Dependencies

```bash
# Make sure venv is activated
# You should see (venv) in your prompt

pip install sympy numpy PyQt6 matplotlib scikit-image
```

### 3. Verify Installation

```bash
# Test the math engine
python test_engine.py
```

You should see all tests pass.

## Usage

### Launch the Application

```bash
python src/main.py
```

### Example Equations

Try entering these in the function editor:

**Basic Shapes:**
```
x^2 + y^2 = 25          # Circle
abs(x) + abs(y) = 1     # Diamond
x^2 - y^2 = 1           # Hyperbola
```

**Dimension-Agnostic:**
```
sum(n^2) = 25           # Circle (expands to x^2 + y^2 = 25)
sum(abs(n)) = 1         # Square/Diamond
max(abs(n)) = 1         # Actual square (L∞ norm)
```

**Complex:**
```
x^2 + sin(x*y) + y^3 = 1
abs(x)^2.5 + abs(y)^2.5 = 1
```

## Project Structure

```
math-engine/
├── src/
│   ├── main.py                 # Application entry point
│   ├── math_engine/
│   │   ├── __init__.py
│   │   └── environment.py      # Core math engine (SymPy integration)
│   ├── rendering/
│   │   ├── __init__.py
│   │   └── plotter.py          # Matplotlib plotting
│   └── ui/
│       ├── __init__.py
│       └── main_window.py      # PyQt6 UI
├── test_engine.py              # Math engine tests
├── requirements.txt            # Python dependencies
└── README.md                   # This file
```

## How It Works

### Math Engine
- Uses **SymPy** for symbolic mathematics
- Preprocesses dimension-agnostic notation (`sum(n)`, `product(n)`, etc.)
- Parses equations into SymPy expressions
- Solves equations symbolically when possible

### Rendering
- Uses **matplotlib's `plot_implicit`** for 2D visualization
- Automatically handles complex implicit equations
- Uses contour finding and marching squares algorithm

### UI
- **PyQt6** for the interface
- Split view: Function editor + Plot viewport
- Real-time plotting on button click

## Dimension-Agnostic Notation

Special notation that expands based on current dimension:

| Notation | 2D Expansion | 3D Expansion |
|----------|-------------|--------------|
| `sum(abs(n))` | `abs(x) + abs(y)` | `abs(x) + abs(y) + abs(z)` |
| `sum(n^2)` | `x^2 + y^2` | `x^2 + y^2 + z^2` |
| `product(n)` | `x * y` | `x * y * z` |
| `max(abs(n))` | `Max(abs(x), abs(y))` | `Max(abs(x), abs(y), abs(z))` |
| `n[0]` | `x` | `x` |
| `n[1]` | `y` | `y` |

## Next Steps

Current version is a simple 2D plotter. Future enhancements:

1. **3D Visualization** - Add 3D implicit surface rendering
2. **Function Libraries** - Plugin system for custom function packs
3. **Path Functions** - Local space curve definitions between points
4. **GPU Rendering** - Fast real-time rendering with OpenGL shaders
5. **Animation** - Scrub through parameter space
6. **4D Support** - Visualize 4D shapes via 3D slices

## Troubleshooting

**ImportError for PyQt6:**
```bash
pip install PyQt6
```

**Plotting is slow:**
- Matplotlib's implicit plotter can be slow for complex equations
- Future versions will use GPU rendering for better performance

**Syntax errors in equations:**
- Use `**` for exponents, not `^` (though parser converts it)
- Absolute value: `abs(x)` not `|x|`
- Multiplication: `2*x` not `2x`

## Development

**Run tests:**
```bash
python test_engine.py
```

**Activate virtual environment:**
```bash
# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

**Update dependencies:**
```bash
pip freeze > requirements.txt
```

## License

MIT License - Free to use and modify
