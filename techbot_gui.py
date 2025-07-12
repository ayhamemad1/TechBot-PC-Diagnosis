# ==== compatibility shim for Python ≥3.10 ====
import collections, collections.abc
collections.Mapping = collections.abc.Mapping
collections.MutableMapping = collections.abc.MutableMapping
collections.Sequence = collections.abc.Sequence
# ============================================

import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QLabel, QRadioButton, QPushButton,
    QVBoxLayout, QHBoxLayout, QTextEdit, QGroupBox
)
from PyQt5.QtCore import Qt

from experta import Fact, KnowledgeEngine, Rule, NOT, W, MATCH
from expert_system import preprocess, get_details, get_solutions


# ---------- GUI-friendly expert system engine ----------
class GUIWrapper(KnowledgeEngine):
    def __init__(self):
        super().__init__()
        self.result = ""

    def declare_fact(self, key, value):
        self.declare(Fact(**{key: value}))

    def get_result(self):
        return self.result if self.result else "Couldn’t diagnose the issue clearly."

    # ---------- Rules (copied from expert_system.py, without CLI prompts) ----------

    @Rule(Fact(pwr='n'))
    def r0(self): self.set_result('No Power')

    @Rule(Fact(pwr='y'), Fact(beep='y'))
    def r1(self): self.set_result('POST Beep Codes at Startup')

    @Rule(Fact(pwr='y'), Fact(slow='y'), Fact(heat='n'))
    def r2(self): self.set_result('Slow Boot')

    @Rule(Fact(bsod='y'))
    def r3(self): self.set_result('Blue Screen of Death (BSOD)')

    @Rule(Fact(heat='y'), Fact(fan='y'))
    def r4(self): self.set_result('Overheating')

    @Rule(Fact(rst='y'), Fact(heat='n'))
    def r5(self): self.set_result('Random Shutdowns / Restarts')

    @Rule(Fact(net='y'))
    def r6(self): self.set_result('No Internet Connection')

    @Rule(Fact(frz='y'), Fact(bsod='n'))
    def r7(self): self.set_result('System Freezes / Unresponsive Applications')

    @Rule(Fact(disk='y'))
    def r8(self): self.set_result('Disk Read/Write Errors')

    @Rule(Fact(usb='y'))
    def r9(self): self.set_result('USB Devices Not Recognized')

    @Rule(Fact(slw='y'))
    def r10(self): self.set_result('General Sluggishness')

    @Rule(NOT(Fact(issue=W())), salience=-999)
    def fallback(self): self.result = " Couldn’t pin it down exactly. Try refining your answers."

    def set_result(self, issue):
        self.result = f" Most probable issue: {issue}\n\nDescription:\n{get_details(issue)}\n\n Solution:\n{get_solutions(issue)}"
        self.halt()


# ---------- GUI Class ----------
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
        engine = GUIWrapper()
        engine.reset()

        for key, (btn_y, btn_n) in self.answers.items():
            engine.declare_fact(key, 'y' if btn_y.isChecked() else 'n')

        engine.run()
        self.result_area.setText(engine.get_result())


# ---------- Main ----------
if __name__ == "__main__":
    preprocess()
    app = QApplication(sys.argv)
    win = TroubleshooterApp()
    win.resize(750, 600)
    win.show()
    sys.exit(app.exec_())
