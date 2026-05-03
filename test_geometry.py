import sys
from PyQt6.QtWidgets import QApplication
from main import MainWindow

app = QApplication(sys.argv)
window = MainWindow()

# Initial circle
assert window.shape_combo.currentText() == "Circle"
window.target_dia_spin.setValue(4.0)
window.spacing_spin.setValue(0.5)

# Wait for preview update implicitly done by valueChanged
assert window.teeth_count_label.text() == "25"  # 4 * pi / 0.5 = 25.13 -> 25

# Switch to rectangle
window.shape_combo.setCurrentText("Rectangle")
window.target_width_spin.setValue(5.0)

# Teeth should be 5 / 0.5 = 10
assert window.teeth_count_label.text() == "10"
assert window.actual_dia_label.text() == "5.00 in"
print("Geometry UI test passed!")
