#  TechBot - PC Diagnosis Expert System

TechBot is an expert system that helps diagnose common PC issues based on user responses.  
It uses a rule-based inference engine (`experta`) and a GUI built with `PyQt5`.

##  Features
- Diagnoses issues like:
  - No Power
  - Overheating
  - POST Beep Codes
  - Blue Screen (BSOD)
  - Disk Errors
  - USB Not Recognized
- Rule-based knowledge system
- Interactive Yes/No GUI for troubleshooting

##  Tech Stack
- Python 3.x
- `experta`
- `PyQt5`

##  How to Run

Install required libraries:
```bash
pip install pyqt5 experta
```

Then run:
```bash
python techbot_gui.py
```

##  Notes
- The system is designed for demo and educational purposes.
- You can extend the rules to include more technical cases.
