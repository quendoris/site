#!/usr/bin/env python3
"""Explicitly install the reviewed B source into a checked-out quendoris/site tree.

No SSH/deployment. Default is read-only preflight; --apply changes local working tree.
Requires a clean checkout at the historically verified v0.4 Git commit.
"""
from __future__ import annotations
import argparse
import hashlib
import shutil
import subprocess
import sys
from pathlib import Path
from build_reference_b import ROOT, build

PIN='fa82eb5e39deea32f00b91d8b52a90c4a908ba6f'
PAPER_SHA='6c4a941a71695cd96d7445ad6de601aeea5cbf59477812a9b0bfab899d215e47'

def command(*args, repo:Path) -> str:
    return subprocess.check_output(['git','-C',str(repo),*args],text=True).strip()

def main()->int:
    p=argparse.ArgumentParser()
    p.add_argument('--repo',required=True,type=Path,help='existing local quendoris/site checkout')
    p.add_argument('--apply',action='store_true',help='explicitly modify that checkout')
    args=p.parse_args();repo=args.repo.resolve()
    if not (repo/'tools/check_site.py').is_file():raise SystemExit('Missing site verifier; choose correct root')
    if command('rev-parse','HEAD',repo=repo)!=PIN:raise SystemExit('REJECT: checkout must be pinned to '+PIN)
    if command('status','--porcelain',repo=repo):raise SystemExit('REJECT: dirty Git checkout; make a clean worktree')
    pth=repo/'dist/publications/constructive-million/v1.0.0/article.pdf'
    if not pth.is_file() or hashlib.sha256(pth.read_bytes()).hexdigest()!=PAPER_SHA:
        raise SystemExit('REJECT: archived published paper missing or changed')
    check=subprocess.run([sys.executable,str(repo/'tools/check_site.py'),'--root',str(repo)],capture_output=True,text=True)
    if check.returncode:raise SystemExit('REJECT: baseline site integrity check failed\n'+check.stdout+'\n'+check.stderr)
    print('PRECHECK: clean verified site at',PIN)
    print('PRECHECK: original paper SHA-256 preserved')
    print('PLAN: replace five canonical HTML pages and add seven original-B/atmosphere assets')
    print('PLAN: regenerate SHA256SUMS for every file in dist; do NOT touch server')
    if not args.apply:
        print('DRY RUN ONLY. Use --apply to write to this checkout.');return 0
    build(repo/'dist')
    files={f'dist/{f.relative_to(repo/"dist").as_posix()}':hashlib.sha256(f.read_bytes()).hexdigest()
        for f in sorted((repo/'dist').rglob('*')) if f.is_file()}
    manifest=''.join(f'{digest}  {name}\n' for name,digest in sorted(files.items()))
    (repo/'SHA256SUMS').write_text(manifest,encoding='utf-8')
    verify=subprocess.run([sys.executable,str(repo/'tools/check_site.py'),'--root',str(repo)],capture_output=True,text=True)
    if verify.returncode:raise SystemExit('POSTCHECK FAILED; do not commit\n'+verify.stdout+'\n'+verify.stderr)
    if hashlib.sha256(pth.read_bytes()).hexdigest()!=PAPER_SHA:raise SystemExit('FAILED: paper digest changed')
    print(verify.stdout.strip())
    print('SUCCESS: staged B-based v0.6 changes in the LOCAL Git working tree only.')
    print('Review with git diff; do not push or deploy until accepted in Firefox.')
    return 0
if __name__=='__main__':raise SystemExit(main())
