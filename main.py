import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QRadioButton, QPushButton,
    QVBoxLayout, QHBoxLayout, QTextEdit, QScrollArea, QGroupBox
)
from PyQt5.QtCore import Qt

from expert_system import TechSupport, preprocess, _yn

class TroubleshooterApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("TechBot Diagnostic System")
        self.questions = {
            "pwr": "PC powers on?",
            "beep": "POST beep codes?",
            "slow": "Slow boot?",
            "bsod": "Blue screen?",
            "heat": "Overheating?",
            "rst": "Random restarts?",
            "net": "No internet?",
            "frz": "System freezes?",
            "disk": "Disk errors?",
            "usb": "USB not recognized?",
            "fan": "Fans noisy?",
            "slw": "General sluggish?"
        }
        self.answers = {}
        self.initUI()

    def initUI(self):
        layout = QVBoxLayout()
        self.setLayout(layout)

        for key, question in self.questions.items():
            group = QGroupBox(question)
            hbox = QHBoxLayout()
            btn_y = QRadioButton("Yes")
            btn_n = QRadioButton("No")
            btn_n.setChecked(True)
            hbox.addWidget(btn_y)
            hbox.addWidget(btn_n)
            group.setLayout(hbox)
            layout.addWidget(group)
            self.answers[key] = (btn_y, btn_n)

        self.result_area = QTextEdit()
        self.result_area.setReadOnly(True)
        layout.addWidget(self.result_area)

        self.btn = QPushButton("Diagnose")
        self.btn.clicked.connect(self.diagnose)
        layout.addWidget(self.btn)

    def diagnose(self):
        engine = TechSupport()
        engine.reset()

        for key, (btn_y, btn_n) in self.answers.items():
            engine.declare_fact(key, 'y' if btn_y.isChecked() else 'n')

        engine.run()

        result = engine.get_result()
        self.result_area.setText(result)


# ----- Extend Expert System -----
class TechSupport(TechSupport):  # Inherits your base class
    def __init__(self):
        super().__init__()
        self.result = ""

    def declare_fact(self, key, value):
        self.declare(Fact(**{key: value}))

    def get_result(self):
        return self.result if self.result else "Couldn’t diagnose the issue clearly."

    def show(self, i):
        self.result = f"\nMost probable issue: {i}\n\n{get_details(i)}\n\n{get_solutions(i)}"
        self.halt()

    def fallback(self):
        self.result = "Couldn’t pin it down exactly. Try refining your answers."
        self.halt()


if __name__ == "__main__":
    preprocess()
    app = QApplication(sys.argv)
    win = TroubleshooterApp()
    win.show()
    sys.exit(app.exec_())
