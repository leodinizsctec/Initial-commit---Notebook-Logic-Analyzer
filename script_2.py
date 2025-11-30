
import zipfile
import os
import json
from pathlib import Path

base_dir = Path("notebook-logic-analyzer")

# Recriar todos os arquivos de código necessários
# CLI
cli_py = '''#!/usr/bin/env python3
"""Notebook Logic Analyzer - CLI"""
import argparse, subprocess, sys, json
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent / 'src' / 'analysis'))

def cmd_capture(args):
    bin = Path(__file__).parent / 'src' / 'capture' / 'capture'
    if not bin.exists(): print("❌ Compile: cd src/capture && make"); return 1
    return subprocess.run(['sudo', str(bin), args.output]).returncode

def cmd_export(args):
    from parser import CaptureParser
    from export_vcd import VCDExporter
    p = CaptureParser(args.input); p.load()
    names = None
    if args.template:
        with open(args.template) as f: t = json.load(f)
        names = [t['channels'].get(str(i), f"CH{i}") for i in range(16)]
    VCDExporter(p, names).export(args.output)
    return 0

def cmd_analyze(args):
    from parser import CaptureParser
    from compare import SequenceAnalyzer
    p = CaptureParser(args.input); p.load()
    with open(args.template) as f: t = json.load(f)
    SequenceAnalyzer(p, t).analyze()
    return 0

def cmd_info(args):
    from parser import CaptureParser
    p = CaptureParser(args.input); p.load(); p.print_summary()
    return 0

def cmd_templates(args):
    d = Path(__file__).parent / 'src' / 'templates'
    print("\\n📋 Templates:\\n")
    for f in sorted(d.glob('*.json')):
        if f.name.startswith('_'): continue
        with open(f) as fp: t = json.load(fp)
        print(f"  📄 {f.name}\\n     {t.get('name','')}\\n     Canais: {len(t.get('channels',{}))}\\n")
    return 0

def main():
    p = argparse.ArgumentParser(description='Notebook Logic Analyzer')
    s = p.add_subparsers(dest='cmd')
    c = s.add_parser('capture'); c.add_argument('-o','--output',required=True); c.set_defaults(func=cmd_capture)
    e = s.add_parser('export'); e.add_argument('-i','--input',required=True); e.add_argument('-o','--output',required=True); e.add_argument('-t','--template'); e.set_defaults(func=cmd_export)
    a = s.add_parser('analyze'); a.add_argument('-i','--input',required=True); a.add_argument('-t','--template',required=True); a.set_defaults(func=cmd_analyze)
    i = s.add_parser('info'); i.add_argument('-i','--input',required=True); i.set_defaults(func=cmd_info)
    t = s.add_parser('templates'); t.set_defaults(func=cmd_templates)
    args = p.parse_args()
    if not args.cmd: p.print_help(); return 1
    return args.func(args)

if __name__ == '__main__': sys.exit(main())
'''
(base_dir / "cli.py").write_text(cli_py, encoding="utf-8")

# setup.sh
(base_dir / "setup.sh").write_text('''#!/bin/bash
echo "=== Notebook Logic Analyzer - Setup ==="
[ "$EUID" -ne 0 ] && echo "❌ Use: sudo ./setup.sh" && exit 1
apt-get update && apt-get install -y build-essential python3 python3-pip
pip3 install numpy
cd src/capture && make && cd ../..
echo "✅ Pronto!"
''', encoding="utf-8")

# requirements.txt
(base_dir / "requirements.txt").write_text("numpy>=1.21.0\n", encoding="utf-8")

# C files
(base_dir / "src" / "capture" / "gpio_dma.h").write_text('''#ifndef GPIO_DMA_H
#define GPIO_DMA_H
#include <stdint.h>
typedef struct { uint32_t num_channels, sample_rate, duration_samples, pretrigger_samples; uint8_t trigger_channel, trigger_type; uint32_t gpio_mask; } capture_config_t;
int gpio_dma_init(void);
int gpio_dma_configure(capture_config_t *cfg);
int gpio_dma_start_capture(void);
void gpio_dma_cleanup(void);
#endif
''', encoding="utf-8")

(base_dir / "src" / "capture" / "gpio_dma.c").write_text('''#include "gpio_dma.h"
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <fcntl.h>
#include <sys/mman.h>
#include <unistd.h>
#include <time.h>
#define GPIO_BASE 0x3F200000
#define GPLEV0 13
static volatile uint32_t *gpio=NULL; static int fd=-1; static uint8_t *buf=NULL; static uint32_t bufsz=0; static capture_config_t cfg;
int gpio_dma_init(void){fd=open("/dev/mem",O_RDWR|O_SYNC);if(fd<0){perror("open");return -1;}void*m=mmap(NULL,4096,PROT_READ|PROT_WRITE,MAP_SHARED,fd,GPIO_BASE);if(m==MAP_FAILED){perror("mmap");close(fd);return -1;}gpio=(volatile uint32_t*)m;printf("[+] GPIO OK\\n");return 0;}
int gpio_dma_configure(capture_config_t *c){memcpy(&cfg,c,sizeof(cfg));bufsz=c->duration_samples+c->pretrigger_samples;buf=malloc(bufsz*2);if(!buf){perror("malloc");return -1;}printf("[+] Config: %dch %dHz\\n",c->num_channels,c->sample_rate);return 0;}
int gpio_dma_start_capture(void){if(!gpio||!buf)return -1;uint32_t ns=1000000000/cfg.sample_rate;struct timespec ts={0,ns};uint8_t last=0;int trig=0;uint32_t i=0;printf("[*] Waiting trigger...\\n");while(i<bufsz){uint32_t st=gpio[GPLEV0];uint16_t s=(uint16_t)(st&0xFFFF);uint8_t b=(s>>cfg.trigger_channel)&1;if(!trig){if(cfg.trigger_type==2&&last&&!b)trig=1;else if(cfg.trigger_type==1&&!last&&b)trig=1;last=b;if(trig)printf("[+] Trigger!\\n");else{nanosleep(&ts,NULL);continue;}}buf[i*2]=s&0xFF;buf[i*2+1]=(s>>8)&0xFF;i++;nanosleep(&ts,NULL);}printf("[+] Done: %d samples\\n",i);return 0;}
void gpio_dma_cleanup(void){if(buf)free(buf);if(gpio)munmap((void*)gpio,4096);if(fd>=0)close(fd);}
int main(int c,char**v){if(c<2){printf("Usage: %s <out.bin>\\n",v[0]);return 1;}if(gpio_dma_init()<0)return 1;capture_config_t cf={8,1000000,1000000,100000,0,2,0xFFFF};if(gpio_dma_configure(&cf)<0){gpio_dma_cleanup();return 1;}gpio_dma_start_capture();FILE*f=fopen(v[1],"wb");if(f){fwrite(&cf,sizeof(cf),1,f);fwrite(buf,bufsz*2,1,f);fclose(f);}printf("[+] Saved: %s\\n",v[1]);gpio_dma_cleanup();return 0;}
''', encoding="utf-8")

(base_dir / "src" / "capture" / "Makefile").write_text('''CC=gcc
CFLAGS=-Wall -O2
all: capture
capture: gpio_dma.c
\t$(CC) $(CFLAGS) -o $@ $< -lrt
clean:
\trm -f capture
''', encoding="utf-8")

# Python analysis
(base_dir / "src" / "analysis" / "parser.py").write_text('''#!/usr/bin/env python3
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
    def print_summary(self): print(f"Canais: {self.config['num_channels']}\\nTaxa: {self.config['sample_rate']/1e6:.2f} MHz\\nSamples: {len(self.samples)}")
''', encoding="utf-8")

(base_dir / "src" / "analysis" / "export_vcd.py").write_text('''#!/usr/bin/env python3
from datetime import datetime
from parser import CaptureParser
class VCDExporter:
    def __init__(self,parser,names=None): self.parser=parser; self.names=names or [f"CH{i}" for i in range(16)]
    def export(self,out):
        with open(out,'w') as f:
            f.write(f"$date {datetime.now()} $end\\n$version NLA 1.0 $end\\n")
            ns=int(1e9/self.parser.config['sample_rate']); f.write(f"$timescale {ns}ns $end\\n$scope module logic $end\\n")
            ids=[chr(33+i) for i in range(self.parser.config['num_channels'])]
            for i in range(self.parser.config['num_channels']): f.write(f"$var wire 1 {ids[i]} {self.names[i]} $end\\n")
            f.write("$upscope $end\\n$enddefinitions $end\\n$dumpvars\\n")
            for i in range(self.parser.config['num_channels']): f.write(f"{self.parser.samples[0,i]}{ids[i]}\\n")
            f.write("$end\\n"); last=self.parser.samples[0,:].copy()
            for idx in range(1,len(self.parser.samples)):
                curr=self.parser.samples[idx,:]
                if (curr!=last).any():
                    f.write(f"#{idx}\\n")
                    for ch in range(self.parser.config['num_channels']):
                        if curr[ch]!=last[ch]: f.write(f"{curr[ch]}{ids[ch]}\\n")
                    last=curr.copy()
        print(f"[+] VCD: {out}")
''', encoding="utf-8")

(base_dir / "src" / "analysis" / "compare.py").write_text('''#!/usr/bin/env python3
from parser import CaptureParser
class SequenceAnalyzer:
    def __init__(self,parser,template): self.parser=parser; self.template=template; self.results=[]
    def analyze(self):
        print("\\n"+"="*60+"\\nANÁLISE DE SEQUÊNCIA\\n"+"="*60+"\\n")
        ch_map={name:int(idx) for idx,name in self.template['channels'].items()}
        for ev in self.template['expected_sequence']:
            sig,exp_ms,tol,edge=ev['signal'],ev['time_ms'],ev.get('tolerance_ms',5),ev['edge']
            if sig not in ch_map: print(f"⚠️  {sig}: não mapeado"); continue
            edges=self.parser.detect_edges(ch_map[sig],edge)
            if not edges: print(f"❌ {sig}: AUSENTE"); self.results.append({'signal':sig,'status':'missing'}); continue
            closest=min([e[2]*1000 for e in edges],key=lambda t:abs(t-exp_ms)); delta=closest-exp_ms
            if abs(delta)<=tol: print(f"✅ {sig} ({closest:.1f}ms): OK"); self.results.append({'signal':sig,'status':'ok'})
            else: print(f"⚠️  {sig} ({closest:.1f}ms): FORA ({delta:+.1f}ms)"); self.results.append({'signal':sig,'status':'timing'})
        ok=sum(1 for r in self.results if r['status']=='ok'); print(f"\\nResultado: {ok}/{len(self.results)} OK")
''', encoding="utf-8")

# Template manager
tm = '''#!/usr/bin/env python3
"""Template Manager"""
import json, sys
from pathlib import Path
TDIR = Path(__file__).parent / "src" / "templates"
class TM:
    def __init__(self): self.tdir=TDIR; self.tdir.mkdir(parents=True,exist_ok=True)
    def list(self):
        print("\\n📋 Templates:\\n"+"-"*50)
        for f in sorted(self.tdir.glob("*.json")):
            if f.name.startswith("_"): continue
            with open(f) as fp: t=json.load(fp)
            print(f"📄 {f.name}\\n   {t.get('name','')}\\n   Fab: {t.get('manufacturer','')} | Modelo: {t.get('model','')}\\n   Canais: {len(t.get('channels',{}))} | Eventos: {len(t.get('expected_sequence',[]))}\\n")
    def add(self):
        print("\\n➕ NOVO TEMPLATE\\n")
        t={"channels":{},"expected_sequence":[],"common_issues":{}}
        t["manufacturer"]=input("Fabricante: ").strip()
        t["model"]=input("Modelo: ").strip()
        t["board"]=input("Placa: ").strip()
        t["name"]=f"{t['manufacturer']} {t['model']} Power Sequence"
        print("\\nCanais (Enter para parar):")
        for ch in range(16):
            s=input(f"CH{ch}: ").strip()
            if not s: break
            t["channels"][str(ch)]=s.upper()
        print("\\nSequência (Enter para parar):")
        tm=0
        for sig in t["channels"].values():
            edge=input(f"{sig} edge (r/f) [r]: ").strip() or "rising"
            edge="rising" if edge.startswith("r") else "falling"
            ms=float(input(f"{sig} tempo ms [{tm+5}]: ").strip() or tm+5)
            t["expected_sequence"].append({"signal":sig,"edge":edge,"time_ms":ms,"tolerance_ms":5})
            tm=ms
        fn=f"{t['manufacturer']}_{t['model']}_{t['board']}".lower().replace(" ","_")+".json"
        with open(self.tdir/fn,"w") as f: json.dump(t,f,indent=2)
        print(f"\\n✅ Salvo: {fn}")
    def validate(self,fn):
        fp=self.tdir/fn
        if not fp.exists(): print(f"❌ {fn} não existe"); return
        with open(fp) as f: t=json.load(f)
        errs=[]
        for r in["name","channels","expected_sequence"]:
            if r not in t: errs.append(f"Falta: {r}")
        if errs: print("❌ Erros:\\n  "+("\\n  ".join(errs)))
        else: print(f"✅ {fn} válido!")
def main():
    tm=TM()
    if len(sys.argv)<2: print("Uso: list | add | validate <file>"); return
    cmd=sys.argv[1]
    if cmd=="list": tm.list()
    elif cmd=="add": tm.add()
    elif cmd=="validate" and len(sys.argv)>2: tm.validate(sys.argv[2])
if __name__=="__main__": main()
'''
(base_dir / "template_manager.py").write_text(tm, encoding="utf-8")

# Template Dell G15
dell_template = {
    "name": "Dell G15 5511 / Alienware M15 R6 Power Sequence",
    "description": "Sequência de boot para Dell G15 5511 e Alienware M15 R6 - Placa LA-K452P",
    "manufacturer": "Dell",
    "model": "G15 5511 / Alienware M15 R6",
    "board": "LA-K452P",
    "chipset": "Intel TGL-H",
    "ec": "MEC1515",
    "gpu": "NVIDIA GN20",
    "channels": {
        "0": "PWRBTN#", "1": "3VALW_EN", "2": "3VALW_PG", "3": "5VALW_EN",
        "4": "5VALW_PG", "5": "1V8_AON_EN", "6": "3V3_SYS_EN", "7": "DGPU_PWR_EN",
        "8": "DGPU_PWROK", "9": "PCH_PWROK", "10": "VCORE_EN", "11": "VCORE_PG",
        "12": "PLT_RST#", "13": "SYS_PWROK", "14": "EC_RSMRST#", "15": "SLP_S3#"
    },
    "expected_sequence": [
        {"signal": "PWRBTN#", "edge": "falling", "time_ms": 0, "tolerance_ms": 1, "critical": True},
        {"signal": "3VALW_EN", "edge": "rising", "time_ms": 2, "tolerance_ms": 2, "critical": True},
        {"signal": "3VALW_PG", "edge": "rising", "time_ms": 5, "tolerance_ms": 3, "critical": True},
        {"signal": "5VALW_EN", "edge": "rising", "time_ms": 7, "tolerance_ms": 3, "critical": True},
        {"signal": "5VALW_PG", "edge": "rising", "time_ms": 12, "tolerance_ms": 5, "critical": True},
        {"signal": "1V8_AON_EN", "edge": "rising", "time_ms": 15, "tolerance_ms": 5, "critical": True},
        {"signal": "3V3_SYS_EN", "edge": "rising", "time_ms": 20, "tolerance_ms": 5, "critical": True},
        {"signal": "EC_RSMRST#", "edge": "rising", "time_ms": 25, "tolerance_ms": 10, "critical": True},
        {"signal": "PCH_PWROK", "edge": "rising", "time_ms": 35, "tolerance_ms": 15, "critical": True},
        {"signal": "SLP_S3#", "edge": "rising", "time_ms": 40, "tolerance_ms": 15, "critical": False},
        {"signal": "VCORE_EN", "edge": "rising", "time_ms": 45, "tolerance_ms": 10, "critical": True},
        {"signal": "VCORE_PG", "edge": "rising", "time_ms": 55, "tolerance_ms": 15, "critical": True},
        {"signal": "PLT_RST#", "edge": "rising", "time_ms": 65, "tolerance_ms": 20, "critical": True},
        {"signal": "SYS_PWROK", "edge": "rising", "time_ms": 80, "tolerance_ms": 30, "critical": True},
        {"signal": "DGPU_PWR_EN", "edge": "rising", "time_ms": 100, "tolerance_ms": 50, "critical": False},
        {"signal": "DGPU_PWROK", "edge": "rising", "time_ms": 150, "tolerance_ms": 50, "critical": False}
    ],
    "common_issues": {
        "3VALW_PG missing": "Verificar buck 3.3V, capacitores, curto no rail",
        "5VALW_PG missing": "Verificar buck 5V, fusível",
        "1V8_AON_EN not rising": "Verificar EC MEC1515, cristal 32kHz",
        "PCH_PWROK missing": "Verificar rails do PCH",
        "VCORE_PG missing": "Verificar IMVP, MOSFETs",
        "DGPU_PWROK missing": "Verificar reguladores GPU, NVVDD"
    }
}
with open(base_dir / "src" / "templates" / "dell_g15_5511_la_k452p.json", "w") as f:
    json.dump(dell_template, f, indent=2)

# Template base
base_template = {"name":"","manufacturer":"","model":"","board":"","channels":{},"expected_sequence":[],"common_issues":{}}
with open(base_dir / "src" / "templates" / "_template_base.json", "w") as f:
    json.dump(base_template, f, indent=2)

# Criar ZIP final
zip_name = "notebook-logic-analyzer-github.zip"
with zipfile.ZipFile(zip_name, 'w', zipfile.ZIP_DEFLATED) as z:
    for root, dirs, files in os.walk(base_dir):
        for f in files:
            path = os.path.join(root, f)
            arc = os.path.relpath(path, base_dir.parent)
            z.write(path, arc)
            print(f"  ✓ {arc}")

print(f"\n✅ {zip_name} criado ({os.path.getsize(zip_name)/1024:.1f} KB)")
print(f"📦 Total: {sum(1 for _ in base_dir.rglob('*') if _.is_file())} arquivos")
