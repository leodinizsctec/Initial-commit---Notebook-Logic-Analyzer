#!/usr/bin/env python3
from parser import CaptureParser
class SequenceAnalyzer:
    def __init__(self,parser,template): self.parser=parser; self.template=template; self.results=[]
    def analyze(self):
        print("\n"+"="*60+"\nANÁLISE DE SEQUÊNCIA\n"+"="*60+"\n")
        ch_map={name:int(idx) for idx,name in self.template['channels'].items()}
        for ev in self.template['expected_sequence']:
            sig,exp_ms,tol,edge=ev['signal'],ev['time_ms'],ev.get('tolerance_ms',5),ev['edge']
            if sig not in ch_map: print(f"⚠️  {sig}: não mapeado"); continue
            edges=self.parser.detect_edges(ch_map[sig],edge)
            if not edges: print(f"❌ {sig}: AUSENTE"); self.results.append({'signal':sig,'status':'missing'}); continue
            closest=min([e[2]*1000 for e in edges],key=lambda t:abs(t-exp_ms)); delta=closest-exp_ms
            if abs(delta)<=tol: print(f"✅ {sig} ({closest:.1f}ms): OK"); self.results.append({'signal':sig,'status':'ok'})
            else: print(f"⚠️  {sig} ({closest:.1f}ms): FORA ({delta:+.1f}ms)"); self.results.append({'signal':sig,'status':'timing'})
        ok=sum(1 for r in self.results if r['status']=='ok'); print(f"\nResultado: {ok}/{len(self.results)} OK")
