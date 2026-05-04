from PyQt6.QtWidgets import QGraphicsPathItem, QGraphicsItem
from PyQt6.QtGui import QPen, QBrush, QColor, QPainterPath
from PyQt6.QtCore import Qt, QPointF
from gear_math import calculate_gear_math, create_gear_path, calculate_rack_math, create_rack_path

class GearItem(QGraphicsPathItem):
    def __init__(self, parent_scene, gear_type='circle', target_dia=3.0, target_width=3.0, target_height=1.0):
        super().__init__()
        self.gear_type = gear_type
        self.target_dia = target_dia
        self.target_width = target_width
        self.target_height = target_height
        self.parent_scene = parent_scene

        # Geometry data
        self.teeth = 0
        self.actual_dia = 0.0
        self.spacing = 0.0
        self.depth = 0.0
        self.bevel = 0.0

        # Hierarchy / snapping data
        self.parent_gear = None  # Which gear this one is snapped to
        self.child_gears = []    # Gears snapped to this one
        self.angle_offset_from_parent = 0.0  # Physical angle from parent center to this center
        self.snapped = False

        self._is_updating = False  # Flag to prevent severing bonds on programmatic updates

        # Style
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)

        self.setPen(QPen(QColor("#4CAF50"), 0.02)) # 0.02 inches thick
        self.setBrush(QBrush(QColor("#2d2d2d")))

    def rebuild_geometry(self, spacing, depth, bevel):
        self.spacing = spacing
        self.depth = depth
        self.bevel = bevel

        if self.gear_type == 'circle':
            self.teeth, self.actual_dia = calculate_gear_math(self.target_dia, spacing)
            path = create_gear_path(self.teeth, spacing, depth, bevel, self.actual_dia)
        else:
            self.teeth, self.actual_dia = calculate_rack_math(self.target_width, spacing)
            path = create_rack_path(self.teeth, spacing, depth, bevel, self.actual_dia, self.target_height)
        self.setPath(path)

    def update_position_from_parent(self):
        if not self.parent_gear:
            return

        self._is_updating = True
        try:
            # If settings changed, radius changed. Center distance = r1 + r2
            r1 = self.parent_gear.actual_dia / 2.0
            r2 = self.actual_dia / 2.0
            distance = r1 + r2

            import math
            # Calculate new center position based on original snap angle
            new_x = self.parent_gear.pos().x() + distance * math.cos(self.angle_offset_from_parent)
            new_y = self.parent_gear.pos().y() + distance * math.sin(self.angle_offset_from_parent)
            self.setPos(QPointF(new_x, new_y))

            # Calculate perfect mesh rotation based on new geometries
            p_teeth = self.parent_gear.teeth
            g_teeth = self.teeth

            contact_angle_parent_deg = math.degrees(self.angle_offset_from_parent)
            contact_angle_ghost_deg = math.degrees(self.angle_offset_from_parent) + 180.0

            parent_rot = self.parent_gear.rotation()
            parent_phase = (contact_angle_parent_deg - parent_rot) % (360.0 / p_teeth)
            phase_pct = parent_phase / (360.0 / p_teeth)

            target_ghost_phase_pct = 0.5 - phase_pct
            target_ghost_phase_deg = target_ghost_phase_pct * (360.0 / g_teeth)

            ghost_rot = contact_angle_ghost_deg - target_ghost_phase_deg
            self.setRotation(ghost_rot)

            # Update children recursively (copy list to avoid issues if a child manually disconnects, though they shouldn't here)
            for child in list(self.child_gears):
                child.update_position_from_parent()
        finally:
            self._is_updating = False

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange and self.scene():
            # If manually moved, it breaks its snapping bond
            if not self._is_updating and self.snapped and self.parent_gear:
                # Disconnect from parent
                if self in self.parent_gear.child_gears:
                    self.parent_gear.child_gears.remove(self)
                self.parent_gear = None
                self.snapped = False

        return super().itemChange(change, value)
