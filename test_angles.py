import math
from gear_math import calculate_gear_math
from gear_math import create_gear_path

def test_angles(teeth, spacing, depth, bevel, actual_outer_dia):
    pitch_radius = actual_outer_dia / 2.0
    angle_per_tooth = 360.0 / teeth
    angle_solid = angle_per_tooth / 2.0
    angle_gap = angle_per_tooth / 2.0

    bevel_angle_deg = math.degrees(bevel / pitch_radius) if pitch_radius > 0 else 0
    max_bevel = min(angle_solid / 2.0, angle_gap / 2.0)
    bevel_angle_deg = min(bevel_angle_deg, max_bevel)

    top_flat_angle = angle_solid - bevel_angle_deg
    bottom_flat_angle = angle_gap - bevel_angle_deg

    total_tooth_angle = top_flat_angle + bevel_angle_deg + bottom_flat_angle + bevel_angle_deg
    print(f"Angle per tooth: {angle_per_tooth}")
    print(f"Calculated tooth angle: {total_tooth_angle}")
    print(f"Current math ends at angle: {teeth * total_tooth_angle}")

teeth, actual_dia = calculate_gear_math(3.0, 0.5)
test_angles(teeth, 0.5, 0.2, 0.1, actual_dia)
