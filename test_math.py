import math
from gear_math import calculate_gear_math, create_gear_path
teeth, actual_dia = calculate_gear_math(3.0, 0.5)
print(f"Teeth: {teeth}, Actual Dia: {actual_dia:.4f}")
path = create_gear_path(teeth, 0.5, 0.2, 0.1, actual_dia)
print(f"Path elements: {path.elementCount()}")
