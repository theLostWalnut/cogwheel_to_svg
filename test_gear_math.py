import math
from gear_math import calculate_gear_math, create_gear_path, calculate_rack_math, create_rack_path

def test_calculate_gear_math():
    teeth, actual_dia = calculate_gear_math(3.0, 0.5)
    assert teeth == 19

def test_calculate_rack_math():
    teeth, actual_width = calculate_rack_math(3.0, 0.5)
    assert teeth == 6
    assert actual_width == 3.0

def test_create_rack_path():
    teeth_rack, actual_width = calculate_rack_math(3.0, 0.5)
    path_rack = create_rack_path(teeth_rack, 0.5, 0.2, 0.1, actual_width, 1.0)
    assert path_rack.elementCount() == 29
