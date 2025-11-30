#!/usr/bin/env python3
"""Template Manager"""
import json, sys
from pathlib import Path
TDIR = Path(__file__).parent / "src" / "templates"
class TM:
    def __init__(self): self.tdir=TDIR; self.tdir.mkdir(parents=True,exist_ok=True)
    def list(self):
        print("\n📋 Templates:\n"+"-"*50)
        for f in sorted(self.tdir.glob("*.json")):
            if f.name.startswith("_"): continue
            with open(f) as fp: t=json.load(fp)
            print(f"📄 {f.name}\n   {t.get('name','')}\n   Fab: {t.get('manufacturer','')} | Modelo: {t.get('model','')}\n   Canais: {len(t.get('channels',{}))} | Eventos: {len(t.get('expected_sequence',[]))}\n")
    def add(self):
        print("\n➕ NOVO TEMPLATE\n")
        t={"channels":{},"expected_sequence":[],"common_issues":{}}
        t["manufacturer"]=input("Fabricante: ").strip()
        t["model"]=input("Modelo: ").strip()
        t["board"]=input("Placa: ").strip()
        t["name"]=f"{t['manufacturer']} {t['model']} Power Sequence"
        print("\nCanais (Enter para parar):")
        for ch in range(16):
            s=input(f"CH{ch}: ").strip()
            if not s: break
            t["channels"][str(ch)]=s.upper()
        print("\nSequência (Enter para parar):")
        tm=0
        for sig in t["channels"].values():
            edge=input(f"{sig} edge (r/f) [r]: ").strip() or "rising"
            edge="rising" if edge.startswith("r") else "falling"
            ms=float(input(f"{sig} tempo ms [{tm+5}]: ").strip() or tm+5)
            t["expected_sequence"].append({"signal":sig,"edge":edge,"time_ms":ms,"tolerance_ms":5})
            tm=ms
        fn=f"{t['manufacturer']}_{t['model']}_{t['board']}".lower().replace(" ","_")+".json"
        with open(self.tdir/fn,"w") as f: json.dump(t,f,indent=2)
        print(f"\n✅ Salvo: {fn}")
    def validate(self,fn):
        fp=self.tdir/fn
        if not fp.exists(): print(f"❌ {fn} não existe"); return
        with open(fp) as f: t=json.load(f)
        errs=[]
        for r in["name","channels","expected_sequence"]:
            if r not in t: errs.append(f"Falta: {r}")
        if errs: print("❌ Erros:\n  "+("\n  ".join(errs)))
        else: print(f"✅ {fn} válido!")
def main():
    tm=TM()
    if len(sys.argv)<2: print("Uso: list | add | validate <file>"); return
    cmd=sys.argv[1]
    if cmd=="list": tm.list()
    elif cmd=="add": tm.add()
    elif cmd=="validate" and len(sys.argv)>2: tm.validate(sys.argv[2])
if __name__=="__main__": main()
