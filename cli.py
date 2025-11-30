#!/usr/bin/env python3
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
    print("\n📋 Templates:\n")
    for f in sorted(d.glob('*.json')):
        if f.name.startswith('_'): continue
        with open(f) as fp: t = json.load(fp)
        print(f"  📄 {f.name}\n     {t.get('name','')}\n     Canais: {len(t.get('channels',{}))}\n")
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
