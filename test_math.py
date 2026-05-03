import math
from gear_math import calculate_gear_math, create_gear_path, calculate_rack_math, create_rack_path

print("Testing Circle:")
teeth, actual_dia = calculate_gear_math(3.0, 0.5)
print(f"Teeth: {teeth}, Actual Dia: {actual_dia:.4f}")
path = create_gear_path(teeth, 0.5, 0.2, 0.1, actual_dia)
print(f"Path elements: {path.elementCount()}")

print("\nTesting Rectangle:")
teeth_rack, actual_width = calculate_rack_math(3.0, 0.5)
print(f"Teeth: {teeth_rack}, Actual Width: {actual_width:.4f}")
path_rack = create_rack_path(teeth_rack, 0.5, 0.2, 0.1, actual_width, 1.0)
print(f"Path elements: {path_rack.elementCount()}")
