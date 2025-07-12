# ==== compatibility shim for Python ≥3.10 ====
import collections, collections.abc
collections.Mapping = collections.abc.Mapping
collections.MutableMapping = collections.abc.MutableMapping
collections.Sequence = collections.abc.Sequence
# ============================================

from experta import *
import re

# ---------- helpers ----------
def _slug(text: str) -> str:
    """Turn 'Blue Screen of Death (BSOD)' → 'blue_screen_of_death_bsod'."""
    text = text.lower()
    text = re.sub(r'[()/]', '', text)          # drop () /
    text = re.sub(r'[^a-z0-9]+', '_', text)    # spaces etc → _
    return text.strip('_')

def _yn(ans: str) -> str:                      # yes/No → y/n
    ans = ans.strip().lower()
    return 'y' if ans in ('y', 'yes') else 'n'

# ---------- data stores ----------
issues_list      = []
issues_symptoms  = []
symptom_map      = {}
i_desc_map       = {}
i_solution_map   = {}

# ---------- load all txt files ----------
def preprocess():
    global issues_list, issues_symptoms, symptom_map
    with open('issues.txt', encoding='utf-8') as fh:
        issues_list[:] = [ln.strip() for ln in fh if ln.strip()]

    for issue in issues_list:
        fn = _slug(issue)                            # maps to filename

        with open(f'issue symptoms/{fn}.txt', encoding='utf-8') as fh:
            sym = fh.read().strip().splitlines()
            issues_symptoms.append(sym)
            symptom_map[str(sym)] = issue

        with open(f'issue descriptions/{fn}.txt', encoding='utf-8') as fh:
            i_desc_map[issue] = fh.read().strip()

        with open(f'issue solutions/{fn}.txt', encoding='utf-8') as fh:
            i_solution_map[issue] = fh.read().strip()

def get_details(issue):   return i_desc_map.get(issue, '⚠️  missing description')
def get_solutions(issue): return i_solution_map.get(issue, '⚠️  missing solution')

# ---------- expert system ----------
class TechSupport(KnowledgeEngine):
    @DefFacts()
    def _boot(self):
        print("\nHello! I’m TechBot. Answer a few questions (y/n or yes/no).")
        yield Fact(action='find')

    # 12 questions ---------------------------------------------------
    @Rule(Fact(action='find'), NOT(Fact(pwr=W())))  
    def q1(self): self.declare(Fact(pwr=_yn(input("PC powers on? : "))))
    @Rule(Fact(action='find'), NOT(Fact(beep=W()))) 
    def q2(self): self.declare(Fact(beep=_yn(input("POST beep codes? : "))))
    @Rule(Fact(action='find'), NOT(Fact(slow=W()))) 
    def q3(self): self.declare(Fact(slow=_yn(input("Slow boot? : "))))
    @Rule(Fact(action='find'), NOT(Fact(bsod=W()))) 
    def q4(self): self.declare(Fact(bsod=_yn(input("Blue screen? : "))))
    @Rule(Fact(action='find'), NOT(Fact(heat=W()))) 
    def q5(self): self.declare(Fact(heat=_yn(input("Overheating? : "))))
    @Rule(Fact(action='find'), NOT(Fact(rst=W())))  
    def q6(self): self.declare(Fact(rst=_yn(input("Random restarts? : "))))
    @Rule(Fact(action='find'), NOT(Fact(net=W())))  
    def q7(self): self.declare(Fact(net=_yn(input("No internet? : "))))
    @Rule(Fact(action='find'), NOT(Fact(frz=W())))  
    def q8(self): self.declare(Fact(frz=_yn(input("System freezes? : "))))
    @Rule(Fact(action='find'), NOT(Fact(disk=W()))) 
    def q9(self): self.declare(Fact(disk=_yn(input("Disk errors? : "))))
    @Rule(Fact(action='find'), NOT(Fact(usb=W())))  
    def q10(self): self.declare(Fact(usb=_yn(input("USB not recognized? : "))))
    @Rule(Fact(action='find'), NOT(Fact(fan=W())))  
    def q11(self): self.declare(Fact(fan=_yn(input("Fans noisy? : "))))
    @Rule(Fact(action='find'), NOT(Fact(slw=W())))  
    def q12(self): self.declare(Fact(slw=_yn(input("General sluggish? : "))))

    # diagnosis rules -----------------------------------------------
    @Rule(Fact(action='find'), Fact(pwr='n'))                    
    def r0(self): self.declare(Fact(issue='No Power'))
    @Rule(Fact(action='find'), Fact(pwr='y'), Fact(beep='y'))    
    def r1(self): self.declare(Fact(issue='POST Beep Codes at Startup'))
    @Rule(Fact(action='find'), Fact(pwr='y'), Fact(slow='y'), Fact(heat='n'))
    def r2(self): self.declare(Fact(issue='Slow Boot'))
    @Rule(Fact(action='find'), Fact(bsod='y'))              
    def r3(self): self.declare(Fact(issue='Blue Screen of Death (BSOD)'))
    @Rule(Fact(action='find'), Fact(heat='y'), Fact(fan='y'))  
    def r4(self): self.declare(Fact(issue='Overheating'))
    @Rule(Fact(action='find'), Fact(rst='y'), Fact(heat='n'))  
    def r5(self): self.declare(Fact(issue='Random Shutdowns / Restarts'))
    @Rule(Fact(action='find'), Fact(net='y'))                  
    def r6(self): self.declare(Fact(issue='No Internet Connection'))
    @Rule(Fact(action='find'), Fact(frz='y'), Fact(bsod='n'))  
    def r7(self): self.declare(Fact(issue='System Freezes / Unresponsive Applications'))
    @Rule(Fact(action='find'), Fact(disk='y'))                 
    def r8(self): self.declare(Fact(issue='Disk Read/Write Errors'))
    @Rule(Fact(action='find'), Fact(usb='y'))                  
    def r9(self): self.declare(Fact(issue='USB Devices Not Recognized'))

    # show result ----------------------------------------------------
    @Rule(Fact(action='find'), Fact(issue=MATCH.i), salience=-998)
    def show(self, i):
        print(f"\n  Most probable issue: {i}\n")
        print(get_details(i), "\n")
        print(get_solutions(i), "\n")
        self.halt()

    # fallback -------------------------------------------------------
    @Rule(Fact(action='find'), NOT(Fact(issue=W())), salience=-999)
    def fallback(self):
        print("\n  Couldn’t pin it down exactly. Try refining your answers.")

# ---------- main ----------
if __name__ == '__main__':
    preprocess()
    bot = TechSupport()
    while True:
        bot.reset(); bot.run()
        if _yn(input("Troubleshoot another problem? (y/n): ")) == 'n':
            break
