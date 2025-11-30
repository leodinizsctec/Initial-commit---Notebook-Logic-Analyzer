#!/usr/bin/env python3
from datetime import datetime
from parser import CaptureParser
class VCDExporter:
    def __init__(self,parser,names=None): self.parser=parser; self.names=names or [f"CH{i}" for i in range(16)]
    def export(self,out):
        with open(out,'w') as f:
            f.write(f"$date {datetime.now()} $end\n$version NLA 1.0 $end\n")
            ns=int(1e9/self.parser.config['sample_rate']); f.write(f"$timescale {ns}ns $end\n$scope module logic $end\n")
            ids=[chr(33+i) for i in range(self.parser.config['num_channels'])]
            for i in range(self.parser.config['num_channels']): f.write(f"$var wire 1 {ids[i]} {self.names[i]} $end\n")
            f.write("$upscope $end\n$enddefinitions $end\n$dumpvars\n")
            for i in range(self.parser.config['num_channels']): f.write(f"{self.parser.samples[0,i]}{ids[i]}\n")
            f.write("$end\n"); last=self.parser.samples[0,:].copy()
            for idx in range(1,len(self.parser.samples)):
                curr=self.parser.samples[idx,:]
                if (curr!=last).any():
                    f.write(f"#{idx}\n")
                    for ch in range(self.parser.config['num_channels']):
                        if curr[ch]!=last[ch]: f.write(f"{curr[ch]}{ids[ch]}\n")
                    last=curr.copy()
        print(f"[+] VCD: {out}")
