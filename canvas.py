from PyQt6.QtWidgets import QGraphicsView, QGraphicsSceneMouseEvent
from PyQt6.QtCore import Qt, pyqtSignal, QPointF
from PyQt6.QtGui import QMouseEvent, QPainter, QColor, QPen, QBrush
import math
from gear_item import GearItem

class CogwheelCanvas(QGraphicsView):
    # Signals
    settings_changed = pyqtSignal()

    def __init__(self, scene, parent_window):
        super().__init__(scene)
        self.parent_window = parent_window

        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        # Use drag mode only when not adding a gear
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.scale(96, 96) # 1 inch = 96 px

        self.ghost_gear = None
        self.is_adding = False

        # Keep track of mouse tracking explicitly
        self.setMouseTracking(True)

    def start_adding_gear(self, spacing, depth, bevel, gear_type, target_dia, target_width, target_height):
        self.is_adding = True
        self.setDragMode(QGraphicsView.DragMode.NoDrag)

        if self.ghost_gear:
            self.scene().removeItem(self.ghost_gear)

        self.ghost_gear = GearItem(self.scene(), gear_type, target_dia, target_width, target_height)
        self.ghost_gear.rebuild_geometry(spacing, depth, bevel)

        # Style as glowing green ghost
        self.ghost_gear.setPen(QPen(QColor(0, 255, 0, 200), 0.05))
        self.ghost_gear.setBrush(QBrush(QColor(0, 255, 0, 50)))

        self.scene().addItem(self.ghost_gear)

    def mouseMoveEvent(self, event: QMouseEvent):
        super().mouseMoveEvent(event)

        if self.is_adding and self.ghost_gear:
            scene_pos = self.mapToScene(event.pos())

            # Snapping logic
            snapped = False
            best_dist = float('inf')
            best_parent = None
            snap_angle = 0.0

            if self.ghost_gear.gear_type == 'rectangle':
                # Skip snapping for rectangle
                self.ghost_gear.setPos(scene_pos)
                self.ghost_gear.setRotation(0)
                self.ghost_gear.parent_gear = None
                self.ghost_gear.snapped = False
                return

            # Snap distance threshold (in inches)
            SNAP_THRESHOLD = 1.0

            for gear in self.parent_window.gears:
                if gear == self.ghost_gear:
                    continue

                dx = scene_pos.x() - gear.pos().x()
                dy = scene_pos.y() - gear.pos().y()
                dist = math.hypot(dx, dy)

                # Target distance is r1 + r2
                r1 = gear.actual_dia / 2.0
                r2 = self.ghost_gear.actual_dia / 2.0
                target_dist = r1 + r2

                # If we are close to the ideal mesh distance
                if abs(dist - target_dist) < SNAP_THRESHOLD:
                    if abs(dist - target_dist) < best_dist:
                        best_dist = abs(dist - target_dist)
                        best_parent = gear
                        snap_angle = math.atan2(dy, dx)
                        snapped = True

            if snapped and best_parent:
                r1 = best_parent.actual_dia / 2.0
                r2 = self.ghost_gear.actual_dia / 2.0
                dist = r1 + r2

                # Calculate absolute snapped position
                snap_x = best_parent.pos().x() + dist * math.cos(snap_angle)
                snap_y = best_parent.pos().y() + dist * math.sin(snap_angle)
                self.ghost_gear.setPos(QPointF(snap_x, snap_y))

                # Calculate perfect mesh rotation
                # Angle of contact = snap_angle
                # The teeth need to interlock.
                # A simple approximation:
                # Distance turned along pitch circle = r * theta
                # At contact point, the phase of parent gear tooth:
                # Parent gear angle = parent.rotation() + degrees(snap_angle)
                # We need the ghost gear's tooth phase at contact point to be exactly out of phase (shifted by half a tooth pitch)

                # Let's use a robust meshing calculation:
                # Total angle of a full tooth is 360 / teeth
                p_teeth = best_parent.teeth
                g_teeth = self.ghost_gear.teeth

                # Contact point angle from parent's center
                contact_angle_parent_deg = math.degrees(snap_angle)

                # Contact point angle from ghost's center is snap_angle + 180
                contact_angle_ghost_deg = math.degrees(snap_angle) + 180.0

                # Phase of parent at contact (in degrees of a full circle)
                # How many teeth have we passed?
                parent_rot = best_parent.rotation()
                parent_phase = (contact_angle_parent_deg - parent_rot) % (360.0 / p_teeth)

                # Convert phase to percentage of a tooth (0.0 to 1.0)
                phase_pct = parent_phase / (360.0 / p_teeth)

                # We want ghost gear phase at its contact point to be (0.5 - phase_pct)
                # (shifted by half a tooth so gap meets solid)
                target_ghost_phase_pct = 0.5 - phase_pct

                target_ghost_phase_deg = target_ghost_phase_pct * (360.0 / g_teeth)

                # ghost_rot = contact_angle_ghost_deg - target_ghost_phase_deg
                ghost_rot = contact_angle_ghost_deg - target_ghost_phase_deg

                self.ghost_gear.setRotation(ghost_rot)

                # Temporarily store parent info on ghost gear for placement
                self.ghost_gear.parent_gear = best_parent
                self.ghost_gear.angle_offset_from_parent = snap_angle
                self.ghost_gear.snapped = True
            else:
                self.ghost_gear.setPos(scene_pos)
                self.ghost_gear.setRotation(0)
                self.ghost_gear.parent_gear = None
                self.ghost_gear.snapped = False

    def mousePressEvent(self, event: QMouseEvent):
        if self.is_adding and self.ghost_gear and event.button() == Qt.MouseButton.LeftButton:
            # Confirm placement
            self.is_adding = False
            self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)

            # Finalize style
            self.ghost_gear.setPen(QPen(QColor("#4CAF50"), 0.02))
            self.ghost_gear.setBrush(QBrush(QColor("#2d2d2d")))

            # Link hierarchy if snapped
            if self.ghost_gear.parent_gear and self.ghost_gear.snapped:
                self.ghost_gear.parent_gear.child_gears.append(self.ghost_gear)

            # Register to parent window
            self.parent_window.gears.append(self.ghost_gear)

            self.ghost_gear = None
            return

        super().mousePressEvent(event)
