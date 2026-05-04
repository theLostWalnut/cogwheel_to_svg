import math
from PyQt6.QtGui import QPainterPath
from PyQt6.QtCore import QPointF

def calculate_gear_math(target_outer_dia, spacing):
    """
    Given a target outer diameter and spacing (pitch), calculate the
    proper number of teeth and the resulting actual outer diameter.

    Formula:
    Pitch Circumference (approx) = target_outer_dia * pi
    Number of Teeth = round(Pitch Circumference / spacing)
    Actual Pitch Circumference = Number of Teeth * spacing
    Actual Outer Dia (approx) = Actual Pitch Circumference / pi
    """
    # Circumference roughly = pi * diameter
    circumference = math.pi * target_outer_dia
    teeth = max(3, round(circumference / spacing))
    actual_circumference = teeth * spacing
    actual_dia = actual_circumference / math.pi

    return teeth, actual_dia

def create_gear_path(teeth, spacing, depth, bevel, actual_outer_dia):
    """
    Creates a QPainterPath representing a gear centered at (0, 0).
    Everything is returned in 'inches' units.
    """
    path = QPainterPath()

    if teeth < 3:
        return path

    # actual_outer_dia computed in calculate_gear_math is actually the *Pitch Diameter*
    # The true pitch radius where gears intersect.
    pitch_radius = actual_outer_dia / 2.0

    # Teeth extend outward by half the depth, and inward by half the depth
    outer_radius = pitch_radius + (depth / 2.0)
    inner_radius = max(0.1, pitch_radius - (depth / 2.0))

    # Calculate angles
    # Each tooth + gap = 360 / teeth
    angle_per_tooth = 360.0 / teeth

    # We'll divide each tooth section into 4 parts:
    # 1. Bottom flat
    # 2. Rising edge (bevel)
    # 3. Top flat
    # 4. Falling edge (bevel)

    # Let's say tooth width at top is (spacing/2) - (bevel*2) roughly in arc length
    # It's easier to define in angles

    # Let's use simple angular fractions for visual appeal, but constrained by physical spacing
    # For a perfect pitch gear, the tooth and the gap should be roughly equal on the pitch circle.
    # So the angle of a full tooth is angle_per_tooth.
    # Half is gap, half is solid tooth.

    angle_solid = angle_per_tooth / 2.0
    angle_gap = angle_per_tooth / 2.0

    # Convert bevel (in inches) to angle along the pitch circle
    pitch_radius = actual_outer_dia / 2.0
    bevel_angle_deg = math.degrees(bevel / pitch_radius) if pitch_radius > 0 else 0

    # Make sure bevel isn't too large (can't exceed half the solid or gap angle)
    max_bevel = min(angle_solid / 2.0, angle_gap / 2.0)
    bevel_angle_deg = min(bevel_angle_deg, max_bevel)

    # A full tooth is:
    # Top flat -> Falling bevel -> Bottom flat -> Rising bevel
    # Note: bevel happens once falling and once rising, so we subtract bevel_angle_deg once from solid and once from gap.
    # Total solid arc = top_flat_angle + 2*(bevel_angle_deg/2) ? No, the bevel is a transition.
    # Let's say top flat takes (angle_solid - bevel_angle_deg) and falling bevel takes bevel_angle_deg.
    # Bottom flat takes (angle_gap - bevel_angle_deg) and rising bevel takes bevel_angle_deg.
    # Sum = (angle_solid - bevel_angle_deg) + bevel_angle_deg + (angle_gap - bevel_angle_deg) + bevel_angle_deg
    # Sum = angle_solid + angle_gap = angle_per_tooth. Correct.
    top_flat_angle = angle_solid - bevel_angle_deg
    bottom_flat_angle = angle_gap - bevel_angle_deg

    current_angle = -top_flat_angle / 2.0

    # Start at the top flat
    start_x = outer_radius * math.cos(math.radians(current_angle))
    start_y = outer_radius * math.sin(math.radians(current_angle))
    path.moveTo(start_x, start_y)

    for i in range(teeth):
        # 1. Top flat
        current_angle += top_flat_angle
        x = outer_radius * math.cos(math.radians(current_angle))
        y = outer_radius * math.sin(math.radians(current_angle))
        path.lineTo(x, y)

        # 2. Falling edge (bevel down to inner radius)
        current_angle += bevel_angle_deg
        x = inner_radius * math.cos(math.radians(current_angle))
        y = inner_radius * math.sin(math.radians(current_angle))
        path.lineTo(x, y)

        # 3. Bottom flat (gap)
        current_angle += bottom_flat_angle
        x = inner_radius * math.cos(math.radians(current_angle))
        y = inner_radius * math.sin(math.radians(current_angle))
        path.lineTo(x, y)

        # 4. Rising edge (bevel up to outer radius)
        current_angle += bevel_angle_deg
        x = outer_radius * math.cos(math.radians(current_angle))
        y = outer_radius * math.sin(math.radians(current_angle))
        path.lineTo(x, y)

    path.closeSubpath()
    return path

def calculate_rack_math(target_width, spacing):
    """
    Given a target width and spacing (pitch), calculate the
    proper number of teeth and the resulting actual width.
    """
    teeth = max(1, round(target_width / spacing))
    actual_width = teeth * spacing
    return teeth, actual_width

def create_rack_path(teeth, spacing, depth, bevel, actual_width, height):
    """
    Creates a QPainterPath representing a rectangular gear (rack).
    The teeth are placed on the top edge, and the main body extends downward.
    Centered horizontally at x=0, and top edge at y=0.
    """
    path = QPainterPath()

    if teeth < 1:
        return path

    # A full tooth length is spacing.
    # The logic here mirrors create_gear_path.
    # We divide the linear tooth into 4 parts:
    # 1. Top flat
    # 2. Falling edge (bevel)
    # 3. Bottom flat (gap)
    # 4. Rising edge (bevel)

    length_per_tooth = spacing
    length_solid = length_per_tooth / 2.0
    length_gap = length_per_tooth / 2.0

    # Ensure bevel is not too large
    max_bevel = min(length_solid / 2.0, length_gap / 2.0)
    actual_bevel = min(bevel, max_bevel)

    top_flat_length = length_solid - actual_bevel
    bottom_flat_length = length_gap - actual_bevel

    start_x = -actual_width / 2.0
    current_x = start_x - top_flat_length / 2.0

    # Start at top flat
    path.moveTo(current_x, 0)

    for i in range(teeth):
        current_x += top_flat_length
        path.lineTo(current_x, 0)
        current_x += actual_bevel
        path.lineTo(current_x, depth)
        current_x += bottom_flat_length
        path.lineTo(current_x, depth)
        current_x += actual_bevel
        path.lineTo(current_x, 0)

    # Finish top flat on the right side
    current_x += top_flat_length / 2.0
    path.lineTo(current_x, 0)

    # Draw the rest of the rectangle
    path.lineTo(actual_width / 2.0, depth + height)
    path.lineTo(-actual_width / 2.0, depth + height)

    path.closeSubpath()
    return path
