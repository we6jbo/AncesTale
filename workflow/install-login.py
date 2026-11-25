#!/usr/bin/env python3
import pathlib,os,argparse
p=argparse.ArgumentParser();p.add_argument('--apply',action='store_true');a=p.parse_args()
if not a.apply:p.error('Use --apply to authorize login startup')
folder=pathlib.Path.home()/'.config/autostart';folder.mkdir(parents=True,exist_ok=True)
target=folder/'ancestale-finale.desktop'; data='[Desktop Entry]\nType=Application\nName=AncesTale\nExec=/usr/bin/python3 /home/we6jbo/Projects/AncesTale/workflow/login.py\nTerminal=false\n'
if target.exists() and target.read_text()!=data:raise SystemExit('Existing autostart differs; review it manually')
if not target.exists():target.write_text(data)
print(target,'installed; starts app on login from Nov 21, not game or email')
