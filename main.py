import sys
import math
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QFormLayout, QDoubleSpinBox, QPushButton, QLabel, QGroupBox,
    QGraphicsView, QGraphicsScene, QGraphicsPathItem, QGraphicsItem
)
from PyQt6.QtGui import QPainter, QColor, QPen, QBrush, QPainterPath
from PyQt6.QtCore import Qt, QPointF

# Dark mode stylesheet
DARK_STYLESHEET = """
QMainWindow, QWidget {
    background-color: #1e1e1e;
    color: #ffffff;
    font-family: 'Segoe UI', Arial, sans-serif;
}
QGroupBox {
    border: 1px solid #333333;
    border-radius: 5px;
    margin-top: 1ex;
    font-weight: bold;
}
QGroupBox::title {
    subcontrol-origin: margin;
    subcontrol-position: top center;
    padding: 0 3px;
    color: #4CAF50;
}
QDoubleSpinBox {
    background-color: #2d2d2d;
    color: #ffffff;
    border: 1px solid #444444;
    border-radius: 3px;
    padding: 2px;
}
QDoubleSpinBox::up-button, QDoubleSpinBox::down-button {
    background-color: #3d3d3d;
}
QPushButton {
    background-color: #4CAF50;
    color: white;
    border: none;
    border-radius: 4px;
    padding: 8px 16px;
    font-weight: bold;
}
QPushButton:hover {
    background-color: #45a049;
}
QPushButton:pressed {
    background-color: #3d8b40;
}
QLabel {
    color: #cccccc;
}
QGraphicsView {
    border: 1px solid #333333;
    background-color: #121212;
}
"""

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Sleek Cogwheel Designer")
        self.resize(1200, 800)
        self.setStyleSheet(DARK_STYLESHEET)

        # Main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout(central_widget)

        # Left panel: Controls
        control_panel = QWidget()
        control_panel.setFixedWidth(300)
        control_layout = QVBoxLayout(control_panel)

        # Global Settings
        global_group = QGroupBox("Global Settings")
        global_layout = QFormLayout()

        self.spacing_spin = QDoubleSpinBox()
        self.spacing_spin.setRange(0.01, 5.0)
        self.spacing_spin.setSingleStep(0.1)
        self.spacing_spin.setValue(0.5)
        self.spacing_spin.setSuffix(" in")
        global_layout.addRow("Tooth Spacing (Pitch):", self.spacing_spin)

        self.depth_spin = QDoubleSpinBox()
        self.depth_spin.setRange(0.01, 2.0)
        self.depth_spin.setSingleStep(0.05)
        self.depth_spin.setValue(0.2)
        self.depth_spin.setSuffix(" in")
        global_layout.addRow("Tooth Depth:", self.depth_spin)

        self.bevel_spin = QDoubleSpinBox()
        self.bevel_spin.setRange(0.0, 1.0)
        self.bevel_spin.setSingleStep(0.05)
        self.bevel_spin.setValue(0.1)
        self.bevel_spin.setSuffix(" in")
        global_layout.addRow("Tooth Bevel:", self.bevel_spin)

        global_group.setLayout(global_layout)
        control_layout.addWidget(global_group)

        # New Gear Settings
        gear_group = QGroupBox("New Gear")
        gear_layout = QVBoxLayout()
        form_layout = QFormLayout()

        self.target_dia_spin = QDoubleSpinBox()
        self.target_dia_spin.setRange(0.5, 50.0)
        self.target_dia_spin.setSingleStep(0.5)
        self.target_dia_spin.setValue(3.0)
        self.target_dia_spin.setSuffix(" in")
        form_layout.addRow("Target Outer Dia:", self.target_dia_spin)

        self.actual_dia_label = QLabel("3.00 in")
        form_layout.addRow("Actual Outer Dia:", self.actual_dia_label)

        self.teeth_count_label = QLabel("18")
        form_layout.addRow("Teeth Count:", self.teeth_count_label)

        gear_layout.addLayout(form_layout)

        self.add_btn = QPushButton("Add to Canvas")
        gear_layout.addWidget(self.add_btn)

        gear_group.setLayout(gear_layout)
        control_layout.addWidget(gear_group)

        # Spacer
        control_layout.addStretch()

        # Export
        self.export_btn = QPushButton("Export to SVG")
        control_layout.addWidget(self.export_btn)

        main_layout.addWidget(control_panel)

        # Right panel: Canvas
        self.scene = QGraphicsScene()
        from canvas import CogwheelCanvas
        self.view = CogwheelCanvas(self.scene, self)

        main_layout.addWidget(self.view)

        self.gears = [] # Keep track of all gears

        # Signal connections
        self.target_dia_spin.valueChanged.connect(self.update_gear_preview)
        self.spacing_spin.valueChanged.connect(self.update_gear_preview)
        self.spacing_spin.valueChanged.connect(self.update_all_gears)
        self.depth_spin.valueChanged.connect(self.update_all_gears)
        self.bevel_spin.valueChanged.connect(self.update_all_gears)

        self.add_btn.clicked.connect(self.add_gear_to_canvas)
        self.export_btn.clicked.connect(self.export_to_svg)

        # Initialize preview
        self.update_gear_preview()

    def update_all_gears(self):
        spacing = self.spacing_spin.value()
        depth = self.depth_spin.value()
        bevel = self.bevel_spin.value()

        # First rebuild all geometries
        for gear in self.gears:
            gear.rebuild_geometry(spacing, depth, bevel)

        # Then update positions for the connected tree
        # We only need to start with root gears (those with no parent)
        for gear in self.gears:
            if not gear.parent_gear:
                # Update all its children recursively
                for child in gear.child_gears:
                    child.update_position_from_parent()

    def add_gear_to_canvas(self):
        target_dia = self.target_dia_spin.value()
        spacing = self.spacing_spin.value()
        depth = self.depth_spin.value()
        bevel = self.bevel_spin.value()

        # Delegate to the canvas to start the interactive placement
        self.view.start_adding_gear(spacing, depth, bevel, target_dia)

    def export_to_svg(self):
        from PyQt6.QtWidgets import QFileDialog
        from PyQt6.QtSvg import QSvgGenerator
        from PyQt6.QtCore import QSize, QRectF

        if not self.gears:
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "Export SVG", "", "SVG Files (*.svg)")
        if not file_path:
            return

        # Get bounding rect of all gears
        rect = self.scene.itemsBoundingRect()

        # Add a little padding (0.5 inches)
        padding = 0.5
        rect.adjust(-padding, -padding, padding, padding)

        generator = QSvgGenerator()
        generator.setFileName(file_path)

        # The resolution attribute of QSvgGenerator sets pixels per meter.
        # But commonly we just want dimensions explicitly in inches.
        # By setting the physical size in mm, we can force 1:1 scale.
        # 1 inch = 25.4 mm
        width_in = rect.width()
        height_in = rect.height()

        # We can set size and viewBox so that user units = inches
        generator.setSize(QSize(int(width_in * 96), int(height_in * 96))) # 96 DPI pixel size
        generator.setViewBox(rect)

        # Optionally set physical size if supported, to tell laser software exact inches.
        # However, QSvgGenerator in PyQt doesn't easily set `width="10in"` string natively.
        # We can write it out, then do a quick string replace to guarantee it.

        painter = QPainter(generator)
        self.scene.render(painter, target=QRectF(), source=rect)
        painter.end()

        # Post-process the SVG to ensure dimensions are explicitly in inches
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            # Replace the generic width/height attributes with explicit inches
            import re
            content = re.sub(r'width="\d+"', f'width="{width_in}in"', content, count=1)
            content = re.sub(r'height="\d+"', f'height="{height_in}in"', content, count=1)

            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
        except Exception as e:
            print(f"Error modifying SVG headers: {e}")

    def update_gear_preview(self):
        from gear_math import calculate_gear_math
        target_dia = self.target_dia_spin.value()
        spacing = self.spacing_spin.value()

        teeth, actual_dia = calculate_gear_math(target_dia, spacing)

        self.teeth_count_label.setText(str(teeth))
        self.actual_dia_label.setText(f"{actual_dia:.2f} in")

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
