#!/usr/bin/env python3
import struct, numpy as np
from pathlib import Path
class CaptureParser:
    def __init__(self, fp): self.filepath=Path(fp); self.config={}; self.samples=None; self.timestamps=None
    def load(self):
        with open(self.filepath,'rb') as f:
            d=f.read(28); v=struct.unpack('IIIIBBI',d)
            self.config={'num_channels':v[0],'sample_rate':v[1],'duration_samples':v[2],'pretrigger_samples':v[3],'trigger_channel':v[4],'trigger_type':v[5]}
            total=self.config['duration_samples']+self.config['pretrigger_samples']
            raw=np.frombuffer(f.read(total*2),dtype=np.uint16)
            self.samples=np.zeros((len(raw),16),dtype=np.uint8)
            for i in range(16): self.samples[:,i]=(raw>>i)&1
            self.timestamps=np.arange(len(self.samples))/self.config['sample_rate']
        print(f"[+] Loaded: {len(self.samples)} samples"); return True
    def get_channel(self,ch): return self.samples[:,ch] if self.samples is not None else None
    def detect_edges(self,ch,edge='both'):
        d=self.get_channel(ch); edges=[]
        if d is None: return edges
        for i in range(1,len(d)):
            if edge in['rising','both'] and d[i-1]==0 and d[i]==1: edges.append(('rising',i,self.timestamps[i]))
            elif edge in['falling','both'] and d[i-1]==1 and d[i]==0: edges.append(('falling',i,self.timestamps[i]))
        return edges
    def print_summary(self): print(f"Canais: {self.config['num_channels']}\nTaxa: {self.config['sample_rate']/1e6:.2f} MHz\nSamples: {len(self.samples)}")
