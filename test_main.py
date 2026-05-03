import sys
from PyQt6.QtWidgets import QApplication
from main import MainWindow

app = QApplication(sys.argv)
window = MainWindow()
window.show() # Make sure it is actually visible to test visibility

# test initial state
assert window.shape_combo.currentText() == "Circle"
assert not window.target_width_spin.isVisible()
assert not window.target_height_spin.isVisible()
assert window.target_dia_spin.isVisible()

# test change state
window.shape_combo.setCurrentText("Rectangle")
assert window.shape_combo.currentText() == "Rectangle"
assert window.target_width_spin.isVisible()
assert window.target_height_spin.isVisible()
assert not window.target_dia_spin.isVisible()

print("UI state test passed!")
